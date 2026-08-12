"""
ProjectForge AI — Report Generator Agent

Specialized agent for Stage 5: assembling the final professional document.
"""

from google.adk.agents import LlmAgent

try:
    from config import REPORT_MODEL
except ImportError:
    from config import WORKER_MODEL as REPORT_MODEL
from prompts.report_prompt import REPORT_PROMPT
from tools.report_tools import save_report, generate_mermaid_diagram

report_generator_agent = LlmAgent(
    name="report_generator_agent",
    model=REPORT_MODEL,
    instruction=REPORT_PROMPT,
    mode="single_turn",
    description=(
        "Technical writer agent that assembles all outputs from Discovery, "
        "Technical Design, and Risk Analysis into a professional, shareable "
        "project document in Markdown format. Includes architecture diagrams, "
        "tech stack tables, and milestone timelines. "
        "Use this agent as the final stage after all analysis is complete."
    ),
    tools=[save_report, generate_mermaid_diagram],
    output_key="final_report",
)
