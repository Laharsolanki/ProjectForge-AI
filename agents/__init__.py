"""
ProjectForge AI — Agents Package

Exports the root_agent for ADK compatibility.
The `adk web` command and ADK runners expect a `root_agent` at the package level.
"""

from agents.orchestrator import orchestrator

# ADK convention: the root_agent is the top-level agent
root_agent = orchestrator
