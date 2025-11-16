"""Ticketing domain objects used across the workflow."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


class GitReference(BaseModel):
    repo_url: HttpUrl
    branch: str
    commit: Optional[str] = None
    path: Optional[str] = None


class Constraints(BaseModel):
    budget_limit_usd: Optional[float] = Field(default=None, ge=0)
    required_services: list[str] = Field(default_factory=list)
    compliance: list[str] = Field(default_factory=list)
    tags: Dict[str, str] = Field(default_factory=dict)


class DeploymentTicket(BaseModel):
    ticket_id: str
    thread_id: str
    status: Literal[
        "draft",
        "design",
        "coding",
        "plan_pending",
        "review",
        "awaiting_approval",
        "approved",
        "applied",
        "drift_detected",
        "closed",
    ]
    requested_by: str
    environment: str
    target_cloud: Literal["azure"]
    terraform_workspace: str
    git: GitReference
    intent_summary: str
    constraints: Constraints
    current_stage: str
    flags: Dict[str, bool] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class TicketSummary(BaseModel):
    ticket: DeploymentTicket
    pending_artifacts: list[str] = Field(default_factory=list)
    latest_message: Optional[str] = None
