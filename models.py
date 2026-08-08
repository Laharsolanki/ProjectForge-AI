"""
ProjectForge AI — Pydantic Data Models

Structured representations for every output artifact produced by the agents.
These models ensure consistency across CLI, web UI, and report generation.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ─── Enums ────────────────────────────────────────────────────────────────────

class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskProbability(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskImpact(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CloudProvider(str, Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


# ─── Discovery Models ────────────────────────────────────────────────────────

class DiscoveryReport(BaseModel):
    """Output of the Discovery Agent — captures the project understanding."""
    problem_statement: Optional[str] = Field(
        default=None,
        description="The problem reframed in the agent's own words"
    )
    target_users: Optional[str] = Field(
        default=None,
        description="Who the users are and their technical level"
    )
    success_metrics: Optional[str] = Field(
        default=None,
        description="How success is measured (revenue, users, time saved)"
    )
    timeline: Optional[str] = Field(
        default=None,
        description="When the project needs to be live"
    )
    team_size: Optional[str] = Field(
        default=None,
        description="Team size and skill set"
    )
    budget: Optional[str] = Field(
        default=None,
        description="Budget constraints, if any"
    )
    scale_expectations: Optional[str] = Field(
        default=None,
        description="Expected scale (10 users or 10 million)"
    )
    existing_systems: Optional[str] = Field(
        default=None,
        description="What's already built or needs integration"
    )
    key_constraints: list[str] = Field(
        default_factory=list,
        description="Top 3-5 constraints/risks identified"
    )
    confidence: Confidence = Field(
        description="Agent's confidence level in understanding"
    )
    open_questions: list[str] = Field(
        default_factory=list,
        description="Remaining clarifying questions"
    )
    # New fields for student stack recommender
    project_idea: Optional[str] = Field(
        default=None,
        description="The student's project idea in detail"
    )
    learning_focus: list[str] = Field(
        default_factory=list,
        description="List of areas the student wants to learn (Frontend, Backend, Database)"
    )
    familiar_technologies: list[str] = Field(
        default_factory=list,
        description="Technologies the student is already familiar with"
    )
    preferred_language: Optional[str] = Field(
        default=None,
        description="Preferred programming language"
    )
    expected_users: Optional[str] = Field(
        default=None,
        description="Expected user scale"
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions made by the agent for missing optional inputs"
    )


# ─── Technical Design Models ─────────────────────────────────────────────────

class TechStackItem(BaseModel):
    """A single technology choice with justification and learning path."""
    category: str = Field(description="e.g., Backend, Frontend, Database")
    technology: str = Field(description="Specific tool/framework name")
    version: Optional[str] = Field(default=None, description="Recommended version")
    justification: str = Field(description="Why this was chosen over alternatives")
    why_it_teaches: Optional[str] = Field(
        default=None,
        description="Key architectural or programming concept this tool teaches"
    )
    why_preferred_over_familiar: Optional[str] = Field(
        default=None,
        description="Comparison with student's familiar tools"
    )
    what_to_learn_first: Optional[str] = Field(
        default=None,
        description="Initial learning steps and core topics"
    )


class DatabaseColumn(BaseModel):
    """A column in a database table."""
    name: str
    type: str
    constraints: Optional[str] = None
    description: Optional[str] = None


class DatabaseTable(BaseModel):
    """A database table definition."""
    name: str
    description: str
    columns: list[DatabaseColumn] = Field(default_factory=list)
    indexes: list[str] = Field(default_factory=list)
    relationships: list[str] = Field(
        default_factory=list,
        description="Foreign key relationships"
    )


class DatabaseSchema(BaseModel):
    """Complete database schema."""
    tables: list[DatabaseTable] = Field(default_factory=list)
    scalability_notes: list[str] = Field(default_factory=list)


class APIEndpoint(BaseModel):
    """An API endpoint definition."""
    method: str = Field(description="HTTP method (GET, POST, PUT, DELETE, WS)")
    path: str = Field(description="URL path")
    description: str
    request_body: Optional[str] = Field(default=None, description="Request shape")
    response_body: Optional[str] = Field(default=None, description="Response shape")
    auth_required: bool = True


class APIDesign(BaseModel):
    """API design specification."""
    base_url: Optional[str] = None
    auth_mechanism: str = Field(
        default="JWT",
        description="Authentication mechanism (JWT, OAuth2, API Key, RLS)"
    )
    rate_limiting: Optional[str] = None
    endpoints: list[APIEndpoint] = Field(default_factory=list)


class Milestone(BaseModel):
    """A project milestone with effort estimate."""
    number: int
    name: str
    description: str
    effort_days: str = Field(description="Estimated effort (e.g., '3-5 days')")
    dependencies: list[str] = Field(
        default_factory=list,
        description="What milestones this depends on"
    )
    deliverables: list[str] = Field(default_factory=list)
    is_critical_path: bool = False


class TechDesign(BaseModel):
    """Complete technical design output."""
    architecture_pattern: Optional[str] = Field(
        default=None,
        description="Monolith, Microservices, Serverless, Decoupled SPA+API, etc."
    )
    architecture_reasoning: Optional[str] = Field(
        default=None,
        description="Why this pattern was chosen with tradeoff analysis"
    )
    tech_stack: list[TechStackItem] = Field(default_factory=list)
    database_schema: Optional[DatabaseSchema] = None
    api_design: Optional[APIDesign] = None
    milestones: list[Milestone] = Field(default_factory=list)
    learning_action_plan: list[str] = Field(
        default_factory=list,
        description="Step-by-step roadmap: Day 1 setup, Day 2 core logic, Week 1 milestone"
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions made regarding missing inputs and scope guardrails"
    )
    non_obvious_suggestions: list[str] = Field(
        default_factory=list,
        description="Insights the user likely hasn't considered"
    )
    architecture_diagram: Optional[str] = Field(
        default=None,
        description="Mermaid diagram source code"
    )


# ─── Risk Models ─────────────────────────────────────────────────────────────

class Risk(BaseModel):
    """A specific risk with mitigation strategy."""
    title: str
    description: str
    impact: RiskImpact
    probability: RiskProbability
    mitigation: str = Field(description="How to prevent or reduce this risk")
    detection: str = Field(description="How to know when this risk materializes")
    category: Optional[str] = Field(
        default=None,
        description="e.g., Infrastructure, Security, Performance, Team"
    )


class RiskAssessment(BaseModel):
    """Complete risk analysis output."""
    risks: list[Risk] = Field(default_factory=list)
    overall_risk_level: str = Field(
        description="Overall project risk level assessment"
    )
    critical_risks_summary: str = Field(
        description="Summary of the most critical risks"
    )


# ─── Cost Estimation Models ──────────────────────────────────────────────────

class CostLineItem(BaseModel):
    """A single cost line item."""
    service: str
    provider: CloudProvider
    description: str
    monthly_cost_usd: float
    notes: Optional[str] = None


class CostEstimate(BaseModel):
    """Cloud infrastructure cost estimate."""
    line_items: list[CostLineItem] = Field(default_factory=list)
    total_monthly_usd: float
    total_annual_usd: float
    assumptions: list[str] = Field(default_factory=list)
    optimization_tips: list[str] = Field(default_factory=list)


# ─── Learning Path Model ─────────────────────────────────────────────────────

class LearningResource(BaseModel):
    """A learning resource recommendation."""
    topic: str
    resource_type: str = Field(description="tutorial, docs, book, course, video")
    title: str
    url: Optional[str] = None
    estimated_time: Optional[str] = None
    priority: str = Field(default="medium", description="high, medium, low")


class LearningPath(BaseModel):
    """Learning path for the recommended tech stack."""
    resources: list[LearningResource] = Field(default_factory=list)
    estimated_total_time: Optional[str] = None
    prerequisites: list[str] = Field(default_factory=list)


# ─── Complete Project Report ─────────────────────────────────────────────────

class ProjectReport(BaseModel):
    """The complete project report — composite of all agent outputs."""
    project_name: str
    executive_summary: str
    discovery: Optional[DiscoveryReport] = None
    tech_design: Optional[TechDesign] = None
    risk_assessment: Optional[RiskAssessment] = None
    cost_estimate: Optional[CostEstimate] = None
    learning_path: Optional[LearningPath] = None
    next_steps: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
