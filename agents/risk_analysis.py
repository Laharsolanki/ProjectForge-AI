"""
ProjectForge AI — Risk Analysis Agent

Specialized agent for Stage 3: identifying failure modes and mitigations.
"""

from google.adk.agents import LlmAgent

from config import WORKER_MODEL
from prompts.risk_prompt import RISK_PROMPT
from tools.cost_estimator import estimate_cloud_costs

risk_analysis_agent = LlmAgent(
    name="risk_analysis_agent",
    model=WORKER_MODEL,
    instruction=RISK_PROMPT,
    description=(
        "Reliability engineer agent that identifies 5-10 specific failure modes, "
        "concurrency/database pitfalls, security risks, and provides cloud cost estimations. "
        "Use this agent after Technical Design is complete."
    ),
    tools=[
        estimate_cloud_costs,
    ],
    output_key="risk_assessment",
)
