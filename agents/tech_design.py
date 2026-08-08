"""
ProjectForge AI — Technical Design Agent

Specialized agent for Stage 2: designing architecture and tech stack.
"""

from google.adk.agents import LlmAgent

from config import ORCHESTRATOR_MODEL
from prompts.tech_design_prompt import TECH_DESIGN_PROMPT
from tools.recommendation_engine import get_supported_technologies
from tools.report_tools import generate_mermaid_diagram

tech_design_agent = LlmAgent(
    name="tech_design_agent",
    model=ORCHESTRATOR_MODEL,
    mode="single_turn",
    instruction=TECH_DESIGN_PROMPT,
    description=(
        "Specialized stack recommender agent that designs technology stacks "
        "specifically tailored to help students learn something new."
    ),
    tools=[get_supported_technologies, generate_mermaid_diagram],
    output_key="tech_design",
)
