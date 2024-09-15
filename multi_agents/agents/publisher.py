from .utils.file_formats import \
    write_md_to_pdf, \
    write_md_to_word, \
    write_text_to_md

from .utils.views import print_agent_output
from .utils.llms import call_model



class PublisherAgent:
    def __init__(self, output_dir: str, websocket=None, stream_output=None, headers=None):
        self.websocket = websocket
        self.stream_output = stream_output
        self.output_dir = output_dir
        self.headers = headers or {}

    async def generate_executive_summary(self, research_state: dict):
        task = research_state.get("task")
        prompt = [{
            "role": "system",
            "content": "You are a professional executive summary writer. Your job is to write concise, high-level overviews of reports, summarizing the key content and purpose in a brief and effective manner. Keep the language clear and formal while ensuring the summary provides an overall understanding of the report's topic and its conclusions.",
        }, {
            "role": "user",
            "content":  f"""Here is the information from a report:

Introduction: {research_state.get("introduction")}

Table of Contents: {research_state.get('table_of_contents')}

Conclusion : {research_state.get('conclusion')}

Task: Please write a short and concise executive summary that provides an overview of what this report is about.

Instructions:
- Please return summary only without any extra descriptions.
- Make sure that the response has no lines directly picked from the given Introduction or Conclusion.
- Use phrases like 'This report is about', 'This report gives information about' etc., but not the same directly."""
        }]

        response = await call_model(prompt, task.get("model"))
        return response
        
    async def publish_research_report(self, research_state: dict, publish_formats: dict, executive_summary: str):
        layout = self.generate_layout(research_state, executive_summary)
        await self.stream_output("status", "publishing", f"Publishing…", self.websocket)
        await self.stream_output("report", "publishing", f"{layout}.", self.websocket)
        await self.write_report_by_formats(layout, publish_formats)

        return layout

    def generate_layout(self, research_state: dict , executive_summary: str):
        sections = '\n\n'.join(f"{value}"
                                 for subheader in research_state.get("research_data")
                                 for key, value in subheader.items())
        references = '\n'.join(f"{reference}" for reference in research_state.get("sources"))
        headers = research_state.get("headers")
        task = research_state.get("task")
        report_style = task.get("report_style")

        if report_style=="summary":
            layout = f"""# {headers.get('title')}
{sections}
## {headers.get("references")}
{references}"""
        else:
            layout = f"""# {headers.get('title')}
#### {headers.get("date")}: {research_state.get('date')}

## Executive Summary
{executive_summary}

## {headers.get("introduction")}
{research_state.get('introduction')}

## {headers.get("table_of_contents")}
{research_state.get('table_of_contents')}

{sections}

## {headers.get("conclusion")}
{research_state.get('conclusion')}

## {headers.get("references")}
{references}
"""
        return layout

    async def write_report_by_formats(self, layout:str, publish_formats: dict):
        if publish_formats.get("pdf"):
            await write_md_to_pdf(layout, self.output_dir)
        if publish_formats.get("docx"):
            await write_md_to_word(layout, self.output_dir)
        if publish_formats.get("markdown"):
            await write_text_to_md(layout, self.output_dir)

    async def run(self, research_state: dict):
        task = research_state.get("task")
        publish_formats = task.get("publish_formats")
        executive_summary = await self.generate_executive_summary(research_state)
        if self.websocket and self.stream_output:
            await self.stream_output("logs", "publishing", f"Publishing final research report based on retrieved data...", self.websocket)
        else:
            print_agent_output(output="Publishing final research report based on retrieved data...", agent="PUBLISHER")
        final_research_report = await self.publish_research_report(research_state, publish_formats, executive_summary)
        return {"report": final_research_report}
