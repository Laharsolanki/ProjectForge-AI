"""
ProjectForge AI — Risk Analysis Agent

Specialized agent for Stage 3: identifying failure modes and mitigations.
"""

from google.adk.agents import LlmAgent

from config import WORKER_MODEL
from prompts.risk_prompt import RISK_PROMPT

risk_analysis_agent = LlmAgent(
    name="risk_analysis_agent",
    model=WORKER_MODEL,
    instruction=RISK_PROMPT,
    mode="single_turn",
    description=(
        "Reliability engineer agent that identifies 5-10 specific failure modes "
        "based on the Discovery Report and Technical Design. Provides impact, "
        "probability, mitigation, and detection strategies. "
        "Use this agent after Technical Design is complete."
    ),
    output_key="risk_assessment",
)
