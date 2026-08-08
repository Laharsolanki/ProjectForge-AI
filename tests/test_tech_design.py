"""
ProjectForge AI — Technical Design Agent & Tools Tests
"""

import pytest
from tools.recommendation_engine import (
    get_supported_technologies,
    get_architecture_patterns,
    filter_recommendations_for_student,
)
from tools.report_tools import generate_mermaid_diagram
from models import (
    TechDesign,
    TechStackItem,
    DatabaseSchema,
    DatabaseTable,
    DatabaseColumn,
    APIDesign,
    APIEndpoint,
    Milestone,
)


class TestRecommendationEngine:
    def test_get_supported_technologies_structure(self):
        stacks = get_supported_technologies()
        assert "frontend" in stacks
        assert "backend" in stacks
        assert "database" in stacks

        assert any("Svelte" in item["name"] for item in stacks["frontend"])
        assert any("Go" in item["name"] for item in stacks["backend"])
        assert any("PostgreSQL" in item["name"] for item in stacks["database"])

    def test_get_architecture_patterns(self):
        patterns = get_architecture_patterns()
        assert "decoupled_spa_api" in patterns
        assert "fullstack_framework" in patterns
        assert "baas_serverless" in patterns
        assert "tradeoffs" in patterns["decoupled_spa_api"]

    def test_filter_recommendations_excludes_familiar(self):
        # Student knows Python and SQLite, wants Backend & Database
        filtered = filter_recommendations_for_student(
            learning_focus=["Backend", "Database"],
            familiar_technologies=["Python", "FastAPI", "SQLite"],
        )
        assert "backend" in filtered
        assert "database" in filtered

        # FastAPI should be excluded since student is familiar with Python/FastAPI
        backend_names = [opt["name"] for opt in filtered["backend"]]
        assert any("Go" in name for name in backend_names)
        assert any("Rust" in name for name in backend_names)

        # SQLite should be excluded, Postgres / Mongo should be present
        db_names = [opt["name"] for opt in filtered["database"]]
        assert any("PostgreSQL" in name for name in db_names)
        assert any("MongoDB" in name for name in db_names)

    def test_filter_recommendations_all_familiar_fallback(self):
        # If student says they know everything, return all options with advanced guidance
        filtered = filter_recommendations_for_student(
            learning_focus=["Frontend"],
            familiar_technologies=["Svelte", "Astro", "React", "Next.js"],
        )
        assert len(filtered["frontend"]) > 0


class TestMermaidTool:
    def test_generate_mermaid_diagram_default_graph(self):
        res = generate_mermaid_diagram("Client --> API\nAPI --> DB")
        assert res["status"] == "success"
        assert "```mermaid" in res["mermaid_code"]
        assert "graph TD" in res["mermaid_code"]
        assert "Client --> API" in res["mermaid_code"]

    def test_generate_mermaid_diagram_explicit_type(self):
        res = generate_mermaid_diagram("sequenceDiagram\nAlice->>Bob: Hello")
        assert res["status"] == "success"
        assert "sequenceDiagram" in res["mermaid_code"]


class TestTechDesignModels:
    def test_tech_design_full_instantiation(self):
        tech_item = TechStackItem(
            category="Backend",
            technology="Go (Gin)",
            version="1.22",
            justification="Teaches statically typed compiled concurrency",
            why_it_teaches="Teaches goroutines and explicit pointer/memory semantics",
            why_preferred_over_familiar="Replaces single-threaded Node.js event loop with lightweight threads",
            what_to_learn_first="Structs, interfaces, and goroutines/channels",
        )

        db_schema = DatabaseSchema(
            tables=[
                DatabaseTable(
                    name="users",
                    description="Stores user accounts",
                    columns=[
                        DatabaseColumn(name="id", type="UUID", constraints="PRIMARY KEY"),
                        DatabaseColumn(name="email", type="VARCHAR(255)", constraints="UNIQUE NOT NULL"),
                    ],
                    indexes=["idx_users_email"],
                    relationships=[],
                )
            ]
        )

        api_design = APIDesign(
            base_url="/api/v1",
            auth_mechanism="JWT Bearer",
            endpoints=[
                APIEndpoint(
                    method="POST",
                    path="/api/v1/auth/login",
                    description="User login and JWT generation",
                    request_body='{"email": "string", "password": "string"}',
                    response_body='{"token": "string"}',
                    auth_required=False,
                )
            ]
        )

        tech_design = TechDesign(
            architecture_pattern="Decoupled SPA + REST API",
            architecture_reasoning="Separates frontend learning from high-concurrency Go backend services.",
            tech_stack=[tech_item],
            database_schema=db_schema,
            api_design=api_design,
            milestones=[
                Milestone(
                    number=1,
                    name="Project Scaffolding",
                    description="Set up Go module and Gin router",
                    effort_days="1-2 days",
                    deliverables=["Working healthcheck endpoint"],
                )
            ],
            learning_action_plan=[
                "Day 1: Go syntax, structs, and Gin setup",
                "Day 2: PostgreSQL schema migration and DB connection",
                "Week 1: JWT Auth and CRUD endpoints",
            ],
            assumptions=["Targeting MVP scale under 100 users."],
            architecture_diagram="graph TD\nClient-->API\nAPI-->PostgreSQL",
        )

        assert tech_design.architecture_pattern == "Decoupled SPA + REST API"
        assert len(tech_design.tech_stack) == 1
        assert tech_design.tech_stack[0].why_it_teaches is not None
        assert len(tech_design.learning_action_plan) == 3
        assert len(tech_design.database_schema.tables) == 1
        assert len(tech_design.api_design.endpoints) == 1
