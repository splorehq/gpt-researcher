from datetime import datetime
import json5 as json
from .utils.views import print_agent_output
from .utils.llms import call_model

sample_json_default = """
{
  "table_of_contents": A table of contents in markdown syntax (using '-') based on the research headers and subheaders,
  "introduction": An indepth introduction to the topic in markdown syntax and hyperlink references to relevant sources,
  "conclusion": A conclusion to the entire research based on all research data in markdown syntax and hyperlink references to relevant sources,
  "sources": A list with strings of all used source links in the entire research data in markdown syntax and apa citation format. For example: ['-  Title, year, Author [source url](source)', ...]
}
"""
sample_json_brief = """
{
  "overview": A brief overview of the research highlights and key takeaways in markdown syntax and hyperlink references to relevant sources,
  "sources": A list with strings of all used source links in the entire research data in markdown syntax and apa citation format. For example: ['-  Title, year, Author [source url](source)', ...]
}
"""

class WriterAgent:
    def __init__(self, websocket=None, stream_output=None, headers=None):
        self.websocket = websocket
        self.stream_output = stream_output
        self.headers = headers

    def get_headers(self, research_state: dict):
        task = research_state.get("task")
        report_style = task.get("report_style")

        if report_style == "detailed report":
            return {
            "title": research_state.get("title"),
            "date": "Date",
            "introduction": "Introduction",
            "table_of_contents": "Table of Contents",
            "conclusion": "Conclusion",
            "references": "References"
        }
        elif report_style == "summary":
            return {
            "title": research_state.get("title"),
            "overview": "Overview",
            "references": "References"
        }
        elif report_style == "policy brief":
            return {
            "title": research_state.get("title"),
            "date": "Date",
            "introduction": "Introduction",
            "table_of_contents": "Table of Contents",
            "conclusion": "Conclusion",
            "references": "References"
        }
        elif report_style == "landscape analysis":
            return {
            "title": research_state.get("title"),
            "date": "Date",
            "introduction": "Introduction",
            "table_of_contents": "Table of Contents",
            "conclusion": "Conclusion",
            "references": "References"
        }
        elif report_style == "research paper brief":
            return {
            "title": research_state.get("title"),
            "date": "Date",
            "introduction": "Introduction",
            "table_of_contents": "Table of Contents",
            "conclusion": "Conclusion",
            "references": "References"
        }

    async def write_sections(self, research_state: dict):
        query = research_state.get("title")
        data = research_state.get("research_data")
        task = research_state.get("task")
        follow_guidelines = task.get("follow_guidelines")
        guidelines = task.get("guidelines")
        report_style = task.get("report_style")

        style_val = ""
        system_prompt = """"You are a research writer. Your sole purpose is to write a well-written research reports about a topic based on research findings and information.\n """
        if report_style == "detailed report":
            style_val = "Write a concise introduction and conclusion for the research report using the provided data. Skip unnecessary details—focus strictly on the topic. Remember, your reader is busy, so keep both sections brief and to the point."
            system_prompt = """Create a structured, rigorous, but succint analyst insights based on the provided topic and subtopics, and conclude with a list of sources. The report should be presented first, followed by the sources. Do not include a final conclusion section.
                            Remember, your reader is busy, so keep both introduction and conclusion sections brief and to the point. 
                            """#**HEIRARCHICAL INFORMATION REPRESENTATION**: Enumerate all the topics and subtopics in the table of contents, and represent the information in a hierarchical manner to match the same numbering."""
        elif report_style == "summary":
            style_val = "Your task is to write a consice yet informative summary from the provided research data. This should be concise and focused on key points, specifically using bullet points where necessary to highlight major outcomes, recommendations, and next steps. Numbers and figures better represented in tabular format."
        elif report_style == "policy brief":
            style_val = "Your task is to write a policy overview report from the provided research data. Write a concise policy brief outlining key findings, policy implications, and actionable recommendations related to the given topic"
        elif report_style == "landscape analysis":
            style_val = "Your task is to write a detailed landscape analysis report from the provided research data. Document a comprehensive landscape analysis summarizing key stakeholders, market trends, challenges, and opportunities within the current policy and regulatory environment."
        elif report_style == "research paper brief":
            style_val = "Your task is to write a thorough scientifc research report from the provided research data. Write a research paper brief that summarizes the key objectives, methodology, findings, and conclusions of the study in a concise and structured format."
        
        sample_json = sample_json_default
        if report_style == "summary":
            sample_json = sample_json_brief
        prompt = [{
            "role": "system",
            "content": system_prompt,
        }, {
            "role": "user",
            "content": f"Today's date is {datetime.now().strftime('%d/%m/%Y')}\n."
                       f"Query or Topic: {query}\n"
                       f"Research data: {str(data)}\n"
                       f"Instruction : {style_val}. \n"
                       f"Do not include headers in the results.\n"
                       f"You MUST include any relevant sources to the introduction and conclusion as markdown hyperlinks -"
                       f"For example: 'This is a sample text. ([url website](url))'\n\n"
                       f"{f'You must follow the guidelines provided: {guidelines}' if follow_guidelines else ''}\n"
                       f"You MUST return nothing but a JSON in the following format (without json markdown):\n"
                       f"Make sure that the 'table_of_contents' holds all the topics and sub-topics mentioned in the 'Research data' in markdown format."
                       f"{sample_json}\n\n"
                       f"References shall be mentioned properly with proper name for that URL, do not say 'source', 'source url' etc., instead give a proper name.\n"
                       f"Do not include the key name in the value again, for example, if key is 'Introduction', do not add '# Introduction' again in the generated content. Same with the 'Conclusion'\n"
                       f"Make sure that the citations are not made up links, they should be valid and reliable. Example of a made up citation is 'example.com', 'sample.com' etc.,\n"

        }]

        response = await call_model(prompt, task.get("model"), response_format='json')
        return response#json.loads(response)

    async def revise_headers(self, task: dict, headers: dict):
        prompt = [{
            "role": "system",
            "content": """You are a research writer. 
Your sole purpose is to revise the headers data based on the given guidelines."""
        }, {
            "role": "user",
            "content": f"""Your task is to revise the given headers JSON based on the guidelines given.
You are to follow the guidelines but the values should be in simple strings, ignoring all markdown syntax.
You must return nothing but a JSON in the same format as given in headers data.
Guidelines: {task.get("guidelines")}\n
Headers Data: {headers}\n
"""

        }]

        response = await call_model(
            prompt,
            task.get("model"),
            response_format="json",
        )
        return {"headers": response}

    async def run(self, research_state: dict):
        if self.websocket and self.stream_output:
            await self.stream_output(
                "logs",
                "writing_report",
                f"Writing final research report based on research data...",
                self.websocket,
            )
        else:
            print_agent_output(
                f"Writing final research report based on research data...",
                agent="WRITER",
            )

        research_layout_content = await self.write_sections(research_state)

        if research_state.get("task").get("verbose"):
            if self.websocket and self.stream_output:
                research_layout_content_str = json.dumps(
                    research_layout_content, indent=2
                )
                await self.stream_output(
                    "logs",
                    "research_layout_content",
                    research_layout_content_str,
                    self.websocket,
                )
            else:
                print_agent_output(research_layout_content, agent="WRITER")

        headers = self.get_headers(research_state)
        if research_state.get("task").get("follow_guidelines"):
            if self.websocket and self.stream_output:
                await self.stream_output(
                    "logs",
                    "rewriting_layout",
                    "Rewriting layout based on guidelines...",
                    self.websocket,
                )
            else:
                print_agent_output(
                    "Rewriting layout based on guidelines...", agent="WRITER"
                )
            headers = await self.revise_headers(
                task=research_state.get("task"), headers=headers
            )
            headers = headers.get("headers")

        return {**research_layout_content, "headers": headers}
