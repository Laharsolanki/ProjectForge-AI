"""
Tests for ProjectForge AI — Pydantic Data Models

Validates model creation, serialization, and constraint enforcement.
"""

import pytest
from models import (
    DiscoveryReport,
    Confidence,
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
            problem_statement="Users need a way to track expenses",
            target_users="Small business owners, non-technical",
            success_metrics="1000 users in 3 months",
            timeline="3 months",
            team_size="2 developers",
            scale_expectations="1K-10K users",
            key_constraints=["Tight timeline", "Small team", "No budget for infra"],
            confidence=Confidence.HIGH,
        )
        assert report.confidence == Confidence.HIGH
        assert len(report.key_constraints) == 3

    def test_optional_fields_default(self):
        report = DiscoveryReport(
            problem_statement="test",
            target_users="test",
            success_metrics="test",
            timeline="test",
            team_size="test",
            scale_expectations="test",
            confidence=Confidence.MEDIUM,
        )
        assert report.budget is None
        assert report.existing_systems is None
        assert report.open_questions == []

    def test_serialization(self):
        report = DiscoveryReport(
            problem_statement="test",
            target_users="test",
            success_metrics="test",
            timeline="test",
            team_size="test",
            scale_expectations="test",
            confidence=Confidence.LOW,
        )
        data = report.model_dump()
        assert data["confidence"] == "low"
        # Roundtrip
        restored = DiscoveryReport.model_validate(data)
        assert restored.confidence == Confidence.LOW

    def test_student_fields(self):
        report = DiscoveryReport(
            project_idea="Build a personal task manager website",
            learning_focus=["Frontend", "Database"],
            familiar_technologies=["Python", "HTML/CSS"],
            preferred_language="JavaScript",
            expected_users="under 100",
            assumptions=["Assume frontend should use interactive elements", "Assume SQLite is fine"],
            confidence=Confidence.HIGH,
        )
        assert report.project_idea == "Build a personal task manager website"
        assert "Frontend" in report.learning_focus
        assert "Python" in report.familiar_technologies
        assert report.preferred_language == "JavaScript"
        assert report.expected_users == "under 100"
        assert len(report.assumptions) == 2
        assert report.confidence == Confidence.HIGH


class TestTechDesign:
    def test_create_tech_stack(self):
        item = TechStackItem(
            category="Backend",
            technology="FastAPI",
            version="0.115.0",
            justification="Async, high performance, good for APIs",
        )
        assert item.category == "Backend"
        assert item.version == "0.115.0"

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
                problem_statement="test",
                target_users="test",
                success_metrics="test",
                timeline="test",
                team_size="test",
                scale_expectations="test",
                confidence=Confidence.HIGH,
            ),
            next_steps=["Set up repo", "Configure CI/CD"],
        )
        assert report.discovery.confidence == Confidence.HIGH
        assert len(report.next_steps) == 2
