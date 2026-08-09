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
        "Specialized discovery agent that interviews the student to capture their "
        "project idea, learning goals, and familiar technologies."
    ),
    output_key="discovery_report",
)
