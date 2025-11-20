"""Artifact models for plan, security, cost, and drift outputs."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class PlanResourceChange(BaseModel):
    address: str
    action: Literal["create", "update", "delete", "replace", "no_op"]
    resource_type: str
    summary: str


class PlanArtifact(BaseModel):
    plan_id: str
    ticket_id: str
    workspace: str
    timestamp_utc: datetime
    raw_plan_path: Optional[str] = None
    changes: List[PlanResourceChange] = Field(default_factory=list)
    summary: str
    terraform_version: Optional[str] = None


class SecurityIssue(BaseModel):
    severity: Literal["critical", "high", "medium", "low", "info"]
    rule_id: str
    description: str
    resource: Optional[str] = None
    remediation: Optional[str] = None


class SecurityReport(BaseModel):
    ticket_id: str
    plan_id: Optional[str]
    tool: Literal["checkov", "tfsec"]
    timestamp_utc: datetime
    issues: List[SecurityIssue] = Field(default_factory=list)

    @property
    def has_blocking_findings(self) -> bool:
        return any(issue.severity in {"critical", "high"} for issue in self.issues)


class CostComponent(BaseModel):
    name: str
    monthly_cost: float = Field(..., ge=0)
    delta_monthly_cost: float = Field(..., ge=-10_000_000)
    currency: str = "USD"


class CostReport(BaseModel):
    ticket_id: str
    plan_id: Optional[str]
    timestamp_utc: datetime
    total_monthly_cost: float
    delta_monthly_cost: float
    currency: str = "USD"
    components: List[CostComponent] = Field(default_factory=list)


class DriftFinding(BaseModel):
    address: str
    detected_at: datetime
    drift_type: Literal["configuration", "state", "resource_missing", "unknown"]
    details: Dict[str, str] = Field(default_factory=dict)


class DriftReport(BaseModel):
    ticket_id: str
    plan_id: Optional[str]
    timestamp_utc: datetime
    findings: List[DriftFinding] = Field(default_factory=list)
