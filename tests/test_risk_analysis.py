"""
Tests for ProjectForge AI — Risk Analysis Agent & Models
"""

import pytest
from agents.risk_analysis import risk_analysis_agent
from models import Risk, RiskAssessment, RiskImpact, RiskProbability, CostEstimate, CostLineItem, CloudProvider


class TestRiskAnalysisAgentSetup:
    """Test the agent configuration and tools."""

    def test_agent_name_and_description(self):
        assert risk_analysis_agent.name == "risk_analysis_agent"
        assert "risk" in risk_analysis_agent.description.lower()
        assert risk_analysis_agent.output_key == "risk_assessment"

    def test_agent_has_cost_tool(self):
        assert risk_analysis_agent.tools is not None
        tool_names = [t.__name__ if hasattr(t, "__name__") else str(t) for t in risk_analysis_agent.tools]
        assert "estimate_cloud_costs" in tool_names


class TestRiskModels:
    """Test Risk and RiskAssessment models."""

    def test_create_valid_risk(self):
        risk = Risk(
            title="Database Connection Exhaustion",
            description="High concurrency may exceed PostgreSQL default max connections.",
            impact=RiskImpact.HIGH,
            probability=RiskProbability.MEDIUM,
            mitigation="Use connection pooling (PgBouncer) or manage pool size in Go.",
            detection="Monitor active connection counts and error logs.",
            category="Infrastructure",
        )
        assert risk.impact == RiskImpact.HIGH
        assert risk.probability == RiskProbability.MEDIUM
        assert risk.category == "Infrastructure"

    def test_create_risk_assessment(self):
        risk = Risk(
            title="WebSocket State Desynchronization",
            description="Client reconnects could cause state mismatch.",
            impact=RiskImpact.MEDIUM,
            probability=RiskProbability.HIGH,
            mitigation="Send full state snapshot on reconnection.",
            detection="Client-side sequence number mismatch assertions.",
        )
        assessment = RiskAssessment(
            risks=[risk],
            overall_risk_level="Medium",
            critical_risks_summary="Reconnection synchronization requires idempotent snapshot broadcasts.",
        )
        assert len(assessment.risks) == 1
        assert assessment.overall_risk_level == "Medium"
        data = assessment.model_dump()
        assert data["risks"][0]["title"] == "WebSocket State Desynchronization"

    def test_cost_estimate_model(self):
        line = CostLineItem(
            service="EC2 / VM",
            provider=CloudProvider.AWS,
            description="Small compute instance",
            monthly_cost_usd=15.0,
        )
        estimate = CostEstimate(
            line_items=[line],
            total_monthly_usd=15.0,
            total_annual_usd=180.0,
            assumptions=["1 small instance", "Single region"],
            optimization_tips=["Use free tier or local Docker during development"],
        )
        assert estimate.total_monthly_usd == 15.0
        assert estimate.total_annual_usd == 180.0
        assert len(estimate.optimization_tips) == 1
