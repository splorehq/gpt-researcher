from gpt_researcher import GPTResearcher
from colorama import Fore, Style
from .utils.views import print_agent_output


class ResearchAgent:
    def __init__(self, websocket=None, stream_output=None, tone=None, headers=None, base_id=None, agent_id=None):
        self.websocket = websocket
        self.stream_output = stream_output
        self.headers = headers or {}
        self.base_id = base_id
        self.agent_id = agent_id
        self.tone = tone

    async def research(self, query: str, research_report: str = "research_report",
                       parent_query: str = "", verbose=True, source="web", tone=None, headers=None, source_urls=None, include_domains=None, search_query_instructions=None, prompts_from_db=None):
        # Initialize the researcher
        researcher = GPTResearcher(query=query, report_type=research_report, parent_query=parent_query,
                                   verbose=verbose, report_source=source, tone=tone, websocket=self.websocket, headers=self.headers, source_urls=source_urls, include_domains=include_domains, search_query_instructions=search_query_instructions, base_id=self.base_id, agent_id=self.agent_id, prompts_from_db=prompts_from_db)
       # Conduct research on the given query
        await researcher.conduct_research()
        # Write the report
        report = await researcher.write_report()

        return report

    async def run_subtopic_research(self, parent_query: str, subtopic: str, verbose: bool = True, source="web", headers=None, source_urls=None, include_domains=None, search_query_instructions=None, prompts_from_db=None):
        try:
            report = await self.research(parent_query=parent_query, query=subtopic,
                                         research_report="subtopic_report", verbose=verbose, source=source, tone=self.tone, headers=None, source_urls=source_urls,include_domains=include_domains,search_query_instructions=search_query_instructions, prompts_from_db=prompts_from_db)
        except Exception as e:
            print(f"{Fore.RED}Error in researching topic {subtopic}: {e}{Style.RESET_ALL}")
            report = None
        return {subtopic: report}

    async def run_initial_research(self, research_state: dict):
        task = research_state.get("task")
        query = task.get("query")
        source = task.get("source", "web")
        source_urls = task.get("source_urls", [])
        include_domains = task.get("include_domains", None)
        search_query_instructions = task.get("search_query_instructions", None)
        prompts_from_db = task.get("prompts_from_db", None)
        
        if self.websocket and self.stream_output:
            await self.stream_output("status", "publishing", f"Starting Research…", self.websocket)
            await self.stream_output("logs", "initial_research", f"Running initial research on the following query: {query}", self.websocket)
        else:
            print_agent_output(f"Running initial research on the following query: {query}", agent="RESEARCHER")
        return {"task": task, "initial_research": await self.research(query=query, verbose=task.get("verbose"),
                                                                      source=source, tone=self.tone, headers=self.headers, source_urls=source_urls, include_domains=include_domains, search_query_instructions=search_query_instructions, prompts_from_db=prompts_from_db)}

    async def run_depth_research(self, draft_state: dict):
        task = draft_state.get("task")
        topic = draft_state.get("topic")
        parent_query = task.get("query")
        source = task.get("source", "web")
        verbose = task.get("verbose")
        source_urls = task.get("source_urls", [])
        include_domains = task.get("include_domains", None)
        search_query_instructions = task.get("search_query_instructions", None)
        prompts_from_db= task.get("prompts_from_db")

        if self.websocket and self.stream_output:
            await self.stream_output("logs", "depth_research", f"Running in depth research on the following report topic: {topic}", self.websocket)
        else:
            print_agent_output(f"Running in depth research on the following report topic: {topic}", agent="RESEARCHER")
        research_draft = await self.run_subtopic_research(parent_query=parent_query, subtopic=topic,
                                                          verbose=verbose, source=source, headers=self.headers, source_urls=source_urls, include_domains=include_domains, search_query_instructions=search_query_instructions, prompts_from_db=prompts_from_db)
        return {"draft": research_draft}