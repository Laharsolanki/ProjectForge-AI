"""
ProjectForge AI — Discovery Agent

Specialized agent for Stage 1: understanding the user's real problem.
"""

from google.adk.agents import LlmAgent

from config import WORKER_MODEL
from prompts.discovery_prompt import DISCOVERY_PROMPT

discovery_agent = LlmAgent(
    name="discovery_agent",
    model=WORKER_MODEL,
    mode="single_turn",
    instruction=DISCOVERY_PROMPT,
    description=(
        "Specialized discovery agent that understands the user's project idea "
        "through targeted questioning. Produces a Discovery Report with problem "
        "statement, users, metrics, constraints, and confidence level. "
        "Use this agent when starting a new project analysis."
    ),
    output_key="discovery_report",
)
