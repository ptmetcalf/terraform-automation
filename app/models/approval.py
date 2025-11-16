"""Approval workflows between Apply Agent and humans."""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ApprovalRequest(BaseModel):
    request_id: str
    ticket_id: str
    plan_id: str
    summary: str
    plan_overview: str
    security_summary: Optional[str]
    cost_summary: Optional[str]
    created_at: datetime
    requested_by: str
    approvers: list[str] = Field(default_factory=list)


class ApprovalDecision(BaseModel):
    request_id: str
    ticket_id: str
    decision: Literal["approve", "reject", "needs_changes"]
    decided_by: str
    decided_at: datetime
    comments: Optional[str]
