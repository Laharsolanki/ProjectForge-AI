"""
ProjectForge AI — Master Orchestrator Agent

The root agent that manages the full conversation lifecycle,
routing to specialized sub-agents by stage.
"""

from google.adk.agents import LlmAgent

from config import ORCHESTRATOR_MODEL
from prompts.orchestrator_prompt import ORCHESTRATOR_PROMPT
from agents.discovery import discovery_agent
from agents.tech_design import tech_design_agent
from agents.risk_analysis import risk_analysis_agent
from agents.report_generator import report_generator_agent
from tools.memory_tools import save_project_summary, load_project_history, list_projects
from tools.github_tools import create_github_repo, create_github_issues

orchestrator = LlmAgent(
    name="projectforge_orchestrator",
    model=ORCHESTRATOR_MODEL,
    instruction=ORCHESTRATOR_PROMPT,
    description="ProjectForge AI — Student stack recommendation orchestrator",
    sub_agents=[
        discovery_agent,
        tech_design_agent,
        risk_analysis_agent,
        report_generator_agent,
    ],
    tools=[
        save_project_summary,
        load_project_history,
        list_projects,
        create_github_repo,
        create_github_issues,
    ],
    output_key="orchestrator_response",
)
