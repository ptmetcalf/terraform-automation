"""Read-only drift monitoring tool for supervisor agent."""
from __future__ import annotations

from typing import Any
from uuid import uuid4

from agent_framework import AIFunction
from pydantic import BaseModel, Field

from app.tools.terraform_cli_tool import DriftRequest, run_drift_check, TerraformCLIError


class DriftMonitorInput(BaseModel):
    """Inputs required to run a Terraform drift check."""

    requested_by: str = Field(description="Human requesting the drift check")
    workspace_dir: str = Field(description="Path to the Terraform workspace directory on disk")
    terraform_workspace: str = Field(description="Terraform workspace name to select before running plan")
    ticket_id: str | None = Field(
        default=None,
        description="Optional ticket identifier used for labeling the drift report",
    )


class DriftMonitorResult(BaseModel):
    ticket_id: str
    plan_id: str
    finding_count: int
    findings: list[dict[str, Any]]
    summary: str


async def run_drift_monitor(inputs: DriftMonitorInput) -> DriftMonitorResult:
    """Invoke Terraform drift detection without mutating state."""

    ticket_id = inputs.ticket_id or f"drift-{uuid4().hex[:8]}"
    request = DriftRequest(
        ticket_id=ticket_id,
        workspace_dir=inputs.workspace_dir,
        terraform_workspace=inputs.terraform_workspace,
    )
    report = run_drift_check(request)
    finding_count = len(report.findings)
    summary = "No drift detected" if finding_count == 0 else f"{finding_count} drift findings detected"
    findings_payload = [
        {
            "address": finding.address,
            "drift_type": finding.drift_type,
            "details": finding.details,
            "detected_at": finding.detected_at.isoformat(),
        }
        for finding in report.findings
    ]
    return DriftMonitorResult(
        ticket_id=report.ticket_id,
        plan_id=report.plan_id,
        finding_count=finding_count,
        findings=findings_payload,
        summary=summary,
    )


drift_monitor_tool = AIFunction(
    name="drift_monitor",
    description="Run a read-only Terraform plan to detect drift or untracked resources.",
    func=run_drift_monitor,
    input_model=DriftMonitorInput,
    output_model=DriftMonitorResult,
    approval_mode="never_require",
    max_invocations=1,
)
