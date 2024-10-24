from datetime import datetime
from .utils.views import print_agent_output
from .utils.llms import call_model
from langgraph.graph import StateGraph, END
import asyncio
import json

from ..memory.draft import DraftState
from . import ResearchAgent, ReviewerAgent, ReviserAgent


class EditorAgent:
    def __init__(self, websocket=None, stream_output=None, tone=None, headers=None, base_id=None, agent_id=None):
        self.websocket = websocket
        self.stream_output = stream_output
        self.tone = tone
        self.headers = headers or {}
        self.base_id = base_id
        self.agent_id = agent_id

    async def plan_research(self, research_state: dict):
        """
        Curate relevant sources for a query
        :param summary_report:
        :return:
        :param total_sub_headers:
        :return:
        """

        initial_research = research_state.get("initial_research")
        task = research_state.get("task")
        max_sections = task.get("max_sections")
        include_human_feedback = task.get("include_human_feedback")
        human_feedback = research_state.get("human_feedback")
        system_instructions = task["system_instructions"]

        prompt = [{
            "role": "system",
            "content": f"You are a research editor. Your goal is to oversee the research project from inception to completion. {system_instructions}"
        }, {
            "role": "user",
            "content": f"Today's date is {datetime.now().strftime('%d/%m/%Y')}\n."
                       f"Research summary report: '{initial_research}'\n"
                       f"{f'Human feedback: {human_feedback}. You must plan the sections based on the human feedback.' if include_human_feedback else ''}\n"
                       f"Your task is to generate an outline of sections headers for the research project"
                       f" based on the research summary report above.\n"
                       f"You must generate a maximum of {max_sections} section headers.\n"
                       #f"Make sure that the sections are diversified considering multiple horizons like 'Idustrial', 'Investments', 'Science' and 'Technology' are covered if necessary.\n"
                       f"You must focus ONLY on related research topics for subheaders and do NOT include introduction, conclusion and references.\n"
                       f"You must return nothing but a JSON with the fields 'title' (str) and "
                       f"'sections' (maximum {max_sections} section headers) with the following structure: "
                       f"'{{title: string research title, date: today's date, "
                       f"sections: ['section header 1', 'section header 2', 'section header 3' ...]}}.\n "
        }]

        print_agent_output(
            f"Planning an outline layout based on initial research...", agent="EDITOR"
        )
        plan = await call_model(
            prompt=prompt,
            model=task.get("model"),
            response_format="json",
        )

        return {
            "title": plan.get("title"),
            "date": plan.get("date"),
            "sections": plan.get("sections"),
        }

    async def run_parallel_research(self, research_state: dict):
        task = research_state.get("task")
        report_style = task.get("report_style")
        
        research_agent = ResearchAgent(self.websocket, self.stream_output, self.tone, self.headers, self.base_id, self.agent_id)
        queries = research_state.get("sections")
        title = research_state.get("title")
        
        human_feedback = research_state.get("human_feedback")
        workflow = StateGraph(DraftState)

        workflow.add_node("researcher", research_agent.run_depth_research)
        workflow.set_entry_point("researcher")

        if report_style != "summary":
            reviewer_agent = ReviewerAgent(self.websocket, self.stream_output, self.headers)
            reviser_agent = ReviserAgent(self.websocket, self.stream_output, self.headers)
            workflow.add_node("reviewer", reviewer_agent.run)
            workflow.add_node("reviser", reviser_agent.run)

            # set up edges researcher->reviewer->reviser->reviewer...
        
            workflow.add_edge('researcher', 'reviewer')
            workflow.add_edge('reviewer', 'reviser')
            workflow.add_edge('reviser', END)

            # workflow.add_conditional_edges(
            #     "reviewer",
            #     (lambda draft: "accept" if draft["review"] is None else "revise"),
            #     {"accept": END, "revise": "reviser"},
            # )

        chain = workflow.compile()

        # Execute the graph for each query in parallel
        if self.websocket and self.stream_output:
            await self.stream_output(
                "logs",
                "parallel_research",
                f"Running parallel research for the following queries: {queries}",
                self.websocket,
            )
        else:
            print_agent_output(
                f"Running the following research tasks in parallel: {queries}...",
                agent="EDITOR",
            )

        final_drafts = [
            chain.ainvoke(
                {
                    "task": research_state.get("task"),
                    "topic": query,  # + (f". Also: {human_feedback}" if human_feedback is not None else ""),
                    "title": title,
                    "headers": self.headers,
                }
            )
            for query in queries
        ]
        research_results = [
            result["draft"] for result in await asyncio.gather(*final_drafts)
        ]

        return {"research_data": research_results}
