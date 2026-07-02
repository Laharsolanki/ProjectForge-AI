"""
ProjectForge AI — Technical Design Agent

Specialized agent for Stage 2: designing architecture and tech stack.
"""

from google.adk.agents import LlmAgent

from config import ORCHESTRATOR_MODEL
from prompts.tech_design_prompt import TECH_DESIGN_PROMPT
from tools.cost_estimator import estimate_cloud_costs

tech_design_agent = LlmAgent(
    name="tech_design_agent",
    model=ORCHESTRATOR_MODEL,
    mode="single_turn",
    instruction=TECH_DESIGN_PROMPT,
    description=(
        "Senior software architect agent that designs the complete technical "
        "solution: architecture pattern, specific tech stack, database schema, "
        "API endpoints, and milestones. Reads the Discovery Report for context. "
        "Use this agent after Discovery is complete with high confidence."
    ),
    tools=[estimate_cloud_costs],
    output_key="tech_design",
)
