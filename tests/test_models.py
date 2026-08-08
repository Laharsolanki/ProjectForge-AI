"""
Tests for ProjectForge AI — Pydantic Data Models

Validates model creation, serialization, and constraint enforcement.
"""

import pytest
from models import (
    Confidence,
    DiscoveryStatus,
    DiscoveryReport,
    DiscoveryTurn,
    TechStackItem,
    DatabaseTable,
    DatabaseColumn,
    DatabaseSchema,
    APIEndpoint,
    APIDesign,
    Milestone,
    TechDesign,
    Risk,
    RiskImpact,
    RiskProbability,
    RiskAssessment,
    CostLineItem,
    CostEstimate,
    CloudProvider,
    LearningResource,
    LearningPath,
    ProjectReport,
)


class TestDiscoveryReport:
    def test_create_valid_report(self):
        report = DiscoveryReport(
            project_idea="A collaborative real-time code editor",
            learning_focus=["Backend", "Database"],
            familiar_technologies=["Python", "JavaScript"],
            timeline="2 weeks",
            preferred_language="Go",
            expected_users="50 developers",
            confidence=Confidence.HIGH,
        )
        assert report.confidence == Confidence.HIGH
        assert report.project_idea == "A collaborative real-time code editor"
        assert len(report.learning_focus) == 2

    def test_optional_fields_default(self):
        report = DiscoveryReport(
            project_idea="Task tracker",
            learning_focus=["Frontend"],
            familiar_technologies=["HTML/CSS"],
        )
        assert report.timeline == "2 weeks (typical MVP scope)"
        assert report.expected_users == "under 100 users"
        assert report.open_questions == []
        assert report.assumptions == []
        assert report.confidence == Confidence.HIGH

    def test_serialization(self):
        report = DiscoveryReport(
            project_idea="Expense manager",
            learning_focus=["Database"],
            familiar_technologies=["Python"],
            confidence=Confidence.LOW,
        )
        data = report.model_dump()
        assert data["confidence"] == "low"
        # Roundtrip
        restored = DiscoveryReport.model_validate(data)
        assert restored.confidence == Confidence.LOW

    def test_discovery_turn_gathering_info(self):
        turn = DiscoveryTurn(
            status=DiscoveryStatus.GATHERING_INFO,
            message_to_user="What programming languages are you familiar with?",
            report=None,
        )
        assert turn.status == DiscoveryStatus.GATHERING_INFO
        assert turn.report is None
        assert "familiar" in turn.message_to_user

    def test_discovery_turn_ready(self):
        turn = DiscoveryTurn(
            status=DiscoveryStatus.READY,
            message_to_user="Great! Discovery is complete.",
            report=DiscoveryReport(
                project_idea="Real-time chat",
                learning_focus=["Backend"],
                familiar_technologies=["Python"],
            ),
        )
        assert turn.status == DiscoveryStatus.READY
        assert turn.report is not None
        assert turn.report.project_idea == "Real-time chat"


class TestTechDesign:
    def test_create_tech_stack(self):
        item = TechStackItem(
            category="Backend",
            technology="FastAPI",
            version="0.115.0",
            justification="Async, high performance, good for APIs",
            why_it_teaches="Teaches async Python and typing",
            why_preferred_over_familiar="More modern than Flask",
        )
        assert item.category == "Backend"
        assert item.version == "0.115.0"
        assert item.why_it_teaches == "Teaches async Python and typing"

    def test_create_database_schema(self):
        schema = DatabaseSchema(
            tables=[
                DatabaseTable(
                    name="users",
                    description="User accounts",
                    columns=[
                        DatabaseColumn(name="id", type="UUID", constraints="PRIMARY KEY"),
                        DatabaseColumn(name="email", type="VARCHAR(255)", constraints="UNIQUE NOT NULL"),
                    ],
                    indexes=["idx_users_email"],
                    relationships=["expenses.user_id -> users.id"],
                ),
            ],
            scalability_notes=["Partition by created_at after 10M rows"],
        )
        assert len(schema.tables) == 1
        assert len(schema.tables[0].columns) == 2

    def test_create_milestone(self):
        milestone = Milestone(
            number=1,
            name="Auth + Database",
            description="Set up authentication and core database schema",
            effort_days="3-5 days",
            dependencies=[],
            deliverables=["JWT auth", "User table", "Login endpoint"],
            is_critical_path=True,
        )
        assert milestone.is_critical_path is True
        assert len(milestone.deliverables) == 3

    def test_full_tech_design(self):
        design = TechDesign(
            architecture_pattern="Modular Monolith",
            architecture_reasoning="Small team, tight timeline, single deployment unit",
            tech_stack=[
                TechStackItem(
                    category="Backend",
                    technology="Django",
                    version="5.1",
                    justification="Batteries included",
                ),
            ],
            milestones=[
                Milestone(
                    number=1,
                    name="Setup",
                    description="Initial setup",
                    effort_days="2 days",
                ),
            ],
            non_obvious_suggestions=["Add caching layer early"],
        )
        assert design.architecture_pattern == "Modular Monolith"
        assert len(design.non_obvious_suggestions) == 1


class TestRiskAssessment:
    def test_create_risk(self):
        risk = Risk(
            title="Database SPOF",
            description="Single database without replication",
            impact=RiskImpact.CRITICAL,
            probability=RiskProbability.MEDIUM,
            mitigation="Add read replica and automated failover",
            detection="Set up health checks and alerting on connection failures",
            category="Infrastructure",
        )
        assert risk.impact == RiskImpact.CRITICAL

    def test_create_assessment(self):
        assessment = RiskAssessment(
            risks=[
                Risk(
                    title="Test",
                    description="Test risk",
                    impact=RiskImpact.LOW,
                    probability=RiskProbability.LOW,
                    mitigation="None needed",
                    detection="Monitoring",
                ),
            ],
            overall_risk_level="Low",
            critical_risks_summary="No critical risks identified",
        )
        assert len(assessment.risks) == 1


class TestCostEstimate:
    def test_create_estimate(self):
        estimate = CostEstimate(
            line_items=[
                CostLineItem(
                    service="EC2 t3.medium",
                    provider=CloudProvider.AWS,
                    description="Compute",
                    monthly_cost_usd=30.0,
                ),
            ],
            total_monthly_usd=30.0,
            total_annual_usd=360.0,
            assumptions=["On-demand pricing"],
        )
        assert estimate.total_annual_usd == 360.0


class TestProjectReport:
    def test_create_minimal_report(self):
        report = ProjectReport(
            project_name="Test Project",
            executive_summary="A test project.",
        )
        assert report.discovery is None
        assert report.next_steps == []

    def test_create_full_report(self):
        report = ProjectReport(
            project_name="Expense Tracker",
            executive_summary="An expense tracking SaaS application.",
            discovery=DiscoveryReport(
                project_idea="Expense Tracker",
                learning_focus=["Backend"],
                familiar_technologies=["Python"],
                confidence=Confidence.HIGH,
            ),
            next_steps=["Set up repo", "Configure CI/CD"],
        )
        assert report.discovery.confidence == Confidence.HIGH
        assert len(report.next_steps) == 2
