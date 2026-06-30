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
    problem_statement: str = Field(
        description="The problem reframed in the agent's own words"
    )
    target_users: str = Field(
        description="Who the users are and their technical level"
    )
    success_metrics: str = Field(
        description="How success is measured (revenue, users, time saved)"
    )
    timeline: str = Field(
        description="When the project needs to be live"
    )
    team_size: str = Field(
        description="Team size and skill set"
    )
    budget: Optional[str] = Field(
        default=None,
        description="Budget constraints, if any"
    )
    scale_expectations: str = Field(
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


# ─── Technical Design Models ─────────────────────────────────────────────────

class TechStackItem(BaseModel):
    """A single technology choice with justification."""
    category: str = Field(description="e.g., Backend, Frontend, Database")
    technology: str = Field(description="Specific tool/framework name")
    version: Optional[str] = Field(default=None, description="Recommended version")
    justification: str = Field(description="Why this was chosen over alternatives")


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
    method: str = Field(description="HTTP method (GET, POST, PUT, DELETE)")
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
        description="Authentication mechanism (JWT, OAuth2, API Key)"
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
    architecture_pattern: str = Field(
        description="Monolith, Microservices, Serverless, etc."
    )
    architecture_reasoning: str = Field(
        description="Why this pattern was chosen with tradeoff analysis"
    )
    tech_stack: list[TechStackItem] = Field(default_factory=list)
    database_schema: Optional[DatabaseSchema] = None
    api_design: Optional[APIDesign] = None
    milestones: list[Milestone] = Field(default_factory=list)
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
