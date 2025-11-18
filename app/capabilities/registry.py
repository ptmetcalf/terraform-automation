"""Static registry describing available coworker capabilities."""
from __future__ import annotations

from enum import Enum
from functools import lru_cache
from typing import List

from pydantic import BaseModel, Field


class CapabilityStatus(str, Enum):
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    PLANNED = "planned"


class Capability(BaseModel):
    slug: str
    title: str
    description: str
    responsibilities: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    approval_required: bool = True
    approval_commands: List[str] = Field(default_factory=list)
    status: CapabilityStatus = CapabilityStatus.PLANNED


@lru_cache()
def get_capabilities() -> list[Capability]:
    """Return the registry of defined capabilities."""

    return [
        Capability(
            slug="supervisor",
            title="Lead Engineer / Supervisor",
            description="Owns ticket context, enforces guardrails, and routes work to other agents.",
            responsibilities=[
                "Summarize ticket state and blockers",
                "Select next capability to execute",
                "Track human guardrail commands",
            ],
            tools=["Workflow orchestration"],
            approval_required=False,
            approval_commands=[],
            status=CapabilityStatus.AVAILABLE,
        ),
        Capability(
            slug="devops",
            title="DevOps / Terraform",
            description="Plans and applies infrastructure changes via Terraform and GitOps flows.",
            responsibilities=[
                "Generate Terraform diffs",
                "Run plan and capture artifacts",
                "Coordinate apply after approvals",
            ],
            tools=["Terraform CLI", "GitOps Tooling", "MCP Terraform server"],
            approval_commands=["/approve plan", "/approve apply"],
            status=CapabilityStatus.AVAILABLE,
        ),
        Capability(
            slug="sre",
            title="Site Reliability Engineer",
            description="Responds to incidents, runs diagnostics, and proposes remediation.",
            responsibilities=[
                "Collect telemetry and impact",
                "Recommend fixes or rollbacks",
                "Execute runbooks after approval",
            ],
            tools=["Monitoring APIs", "Runbook executors"],
            approval_commands=["/approve sre-action"],
            status=CapabilityStatus.PLANNED,
        ),
        Capability(
            slug="ai-engineer",
            title="AI / ML Engineer",
            description="Builds and deploys model workflows, tracks experiments, and manages inference infra.",
            responsibilities=[
                "Prepare training data requirements",
                "Launch training jobs",
                "Deploy or roll back models",
            ],
            tools=["ML toolchains", "Artifact stores"],
            approval_commands=["/approve ai-train", "/approve ai-deploy"],
            status=CapabilityStatus.PLANNED,
        ),
        Capability(
            slug="backend",
            title="Backend Engineer",
            description="Implements service APIs, writes tests, and prepares GitOps change requests.",
            responsibilities=[
                "Propose architectural changes",
                "Generate diffs with context",
                "Surface test strategies",
            ],
            tools=["Repo tooling", "Unit test harness"],
            approval_commands=["/approve backend-change"],
            status=CapabilityStatus.IN_PROGRESS,
        ),
        Capability(
            slug="frontend",
            title="Frontend Engineer",
            description="Builds UI components, integrates APIs, and ensures design compliance.",
            responsibilities=[
                "Produce component diffs",
                "Run UI test plan outlines",
                "Coordinate with design system",
            ],
            tools=["Repo tooling", "UI test runners"],
            approval_commands=["/approve frontend-change"],
            status=CapabilityStatus.IN_PROGRESS,
        ),
        Capability(
            slug="cost-monitor",
            title="Cost Monitor",
            description="Tracks budget, forecasts, and alerts on cost anomalies.",
            responsibilities=[
                "Pull cost deltas",
                "Forecast budget impacts",
                "Escalate overruns or remediation ideas",
            ],
            tools=["Infracost", "Cloud billing APIs"],
            approval_required=False,
            approval_commands=[],
            status=CapabilityStatus.PLANNED,
        ),
        Capability(
            slug="health-monitor",
            title="Health Monitor",
            description="Observes service health metrics and detects drift or incidents.",
            responsibilities=[
                "Aggregate telemetry streams",
                "Report anomalies",
                "Trigger SRE workflows when needed",
            ],
            tools=["Observability APIs"],
            approval_required=False,
            approval_commands=[],
            status=CapabilityStatus.PLANNED,
        ),
    ]


def get_capability(slug: str) -> Capability | None:
    """Return a capability by slug."""

    for capability in get_capabilities():
        if capability.slug == slug:
            return capability
    return None
