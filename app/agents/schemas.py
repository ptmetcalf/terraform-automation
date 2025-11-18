"""Structured response formats for specialized agents."""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl

from app.models import CostReport, DriftReport, GitOpsChangeRequest, PlanArtifact, SecurityReport


class OrchestratorDirective(BaseModel):
    """High-level decision from the orchestrator."""

    next_phase: Literal[
        "design",
        "coding",
        "plan",
        "review",
        "approval",
        "apply",
        "post_apply",
        "documentation",
        "awaiting_input",
    ]
    summary: str
    blockers: list[str] = Field(default_factory=list)


class DesignResponse(BaseModel):
    architecture_summary: str
    required_modules: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class NamingResponse(BaseModel):
    resources: List[dict] = Field(default_factory=list, description="List of {resource_type, proposed_name}")
    governance_notes: str


class QAResponse(BaseModel):
    quality_gate: Literal["pass", "fail", "needs_more_info"]
    findings: list[str] = Field(default_factory=list)


class CodingResponse(BaseModel):
    description_of_changes: str
    gitops_request: GitOpsChangeRequest


class PlanResponse(BaseModel):
    plan_id: str
    highlights: list[str] = Field(default_factory=list)
    workspace_lock_id: Optional[str]
    plan_artifact: PlanArtifact


class PlanReviewResponse(BaseModel):
    ready_for_apply: bool
    required_actions: list[str] = Field(default_factory=list)


class SecurityResponse(BaseModel):
    blocking_issues: list[str] = Field(default_factory=list)
    summary: str
    report: SecurityReport


class CostResponse(BaseModel):
    delta_monthly_cost: float
    confidence: Literal["low", "medium", "high"]
    notes: str
    report: CostReport


class ApplyResponse(BaseModel):
    decision: Literal["pending_approval", "approved", "rejected"]
    approval_request_id: Optional[str]
    details: str


class DocumentationResponse(BaseModel):
    artifacts_markdown: str
    links: list[HttpUrl] = Field(default_factory=list)


class GitOpsResponse(BaseModel):
    status: Literal["success", "error"]
    pull_request_url: Optional[HttpUrl]
    notes: Optional[str]


class DriftResponse(BaseModel):
    status: Literal["no_drift", "drift_detected"]
    summary: str
    finding_count: int
    report: DriftReport


class PostApplySummary(BaseModel):
    ticket_id: str
    applied_at: datetime
    notes: str
