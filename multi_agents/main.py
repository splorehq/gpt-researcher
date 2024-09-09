from dotenv import load_dotenv
import sys
import os
import uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from multi_agents.agents import ChiefEditorAgent
import asyncio
import json
from gpt_researcher.utils.enum import Tone

# Run with LangSmith if API key is set
if os.environ.get("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
load_dotenv()

def open_task():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the absolute path to task.json
    task_json_path = os.path.join(current_dir, 'task.json')
    
    with open(task_json_path, 'r') as f:
        task = json.load(f)

    if not task:
        raise Exception("No task provided. Please include a task.json file in the multi_agents directory.")

    return task

async def run_research_task(query, task_id=None, websocket=None, stream_output=None, tone=Tone.Objective, headers=None, source = None, report_style="detailed report", source_urls=None, agent_specialization=None):
    task = open_task()
    task["query"] = query
    task["source"] = source
    task["report_style"] = report_style
    task["source_urls"] = source_urls
    include_domains, system_instructions = await get_secialisation_config(agent_specialization)
    task["include_domains"] = include_domains
    task["system_instructions"] = system_instructions
    task["task_id"] = task_id
    
    chief_editor = ChiefEditorAgent(task, websocket, stream_output, tone, headers)
    if websocket and stream_output:
        await stream_output("task_id", "research_report", chief_editor.task_id, websocket)

    research_report = await chief_editor.run_research_task()

    if websocket and stream_output:
        await stream_output("logs", "research_report", research_report, websocket)

    return research_report

async def get_secialisation_config(agent_specialization):
    include_domains = None
    system_instructions = """"You are a research editor. Your goal is to oversee the research project"
                " from inception to completion. Your main task is to plan the article section "
                "layout based on an initial research summary.\n """
    
    if agent_specialization == 'investment':
        include_domains =[]# ["https://www.iucn.org/","https://www.wri.org/","https://www.unep.org/","https://www.fao.org/","https://www.cbd.int/","https://www.thegef.org/","https://www.worldwildlife.org/","https://www.birdlife.org/","https://www.nature.org/","https://www.ifpri.org/","https://www.worldbank.org/en/topic/environment","https://glp.earth/","https://www.undp.org/","https://www.ramsar.org/","https://www.iied.org/","https://www.conservation.org/","https://www.adb.org/sectors/environment/main","https://www.icimod.org/","http://teebweb.org/","https://www.mandainature.org/","https://www.reuters.com/business/energy/","https://www.bloomberg.com/energy","https://www.greentechmedia.com/","https://energynews.us/","https://www.renewableenergyworld.com/","https://www.energymonitor.ai/","https://www.pv-tech.org/","https://www.carbonbrief.org/","https://www.offshorewind.biz/","https://cleantechnica.com/","https://www.spglobal.com/platts/en","https://www.energyvoice.com/","https://www.euractiv.com/section/energy-environment/","https://www.axios.com/energy","https://www.power-technology.com/","https://www.reuters.com/business/environment","https://carbon-pulse.com/","https://www.bloomberg.com/green","https://www.climatechangenews.com/","https://www.carbonbrief.org/","https://www.ecosystemmarketplace.com/","https://www.ft.com/climate-capital","https://www.spglobal.com/platts/en/market-insights/latest-news/energy-transition","https://www.theguardian.com/environment/climate-crisis","https://www.axios.com/climate","https://www.euractiv.com/section/climate-environment/","https://insideclimatenews.org/","https://www.environmental-finance.com/","https://www.icis.com/explore/services/carbon-markets/"]
        system_instructions = """You are a senior scientific analyst at a top-tier global deep tech VC firm. "
                        "Your expertise lies in conducting PhD-level research by analyzing market reports, surveys, "
                        "scientific studies, and other relevant sources to identify promising technological innovations and potential risks. "
                        "Your goal is to oversee the research project from inception to completion. "
                        "Your main task is to plan the article section layout based on an initial research summary, "
                        "drawing inspiration from analyst reports from top-tier institutions like the World Bank, IMF, and Bloomberg. "
                        "Assume the reader is already an expert in the field."""
    
    elif agent_specialization == 'deeptech':
        include_domains = ["https://www.ieee.org/","https://www.arxiv.org/","https://www.nasa.gov/"]
        
    return include_domains, system_instructions
    
async def main():
    task = open_task()

    chief_editor = ChiefEditorAgent(task)
    research_report = await chief_editor.run_research_task(task_id=uuid.uuid4())

    return research_report

if __name__ == "__main__":
    asyncio.run(main())