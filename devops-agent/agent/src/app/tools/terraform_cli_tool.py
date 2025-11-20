"""Terraform CLI tool wrappers exposed to agents."""
from __future__ import annotations

import json
import logging
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Optional

from pydantic import BaseModel, Field

from app.config import settings
from app.models import DriftFinding, DriftReport, PlanArtifact, PlanResourceChange

logger = logging.getLogger(__name__)


class TerraformCLIError(RuntimeError):
    """Raised when Terraform commands fail."""


class PlanRequest(BaseModel):
    ticket_id: str
    workspace_dir: str
    terraform_workspace: str
    variables: dict[str, str] = Field(default_factory=dict)
    backend_config: dict[str, str] = Field(default_factory=dict)


class ApplyRequest(BaseModel):
    ticket_id: str
    workspace_dir: str
    plan_path: Optional[str] = None
    auto_approve: bool = False


class ApplyResult(BaseModel):
    ticket_id: str
    success: bool
    stdout: str
    stderr: Optional[str]


class DriftRequest(BaseModel):
    ticket_id: str
    workspace_dir: str
    terraform_workspace: str


@dataclass
class _CommandResult:
    stdout: str
    stderr: str


def _run_terraform(cmd: list[str], cwd: Path, env: Optional[dict[str, str]] = None) -> _CommandResult:
    """Run terraform command and capture JSON output."""

    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    logger.debug("Running terraform command: %s", " ".join(cmd))
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            env=merged_env,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise TerraformCLIError("Terraform binary not found. Set TF_CLI_PATH or install terraform.") from exc
    except subprocess.CalledProcessError as exc:
        raise TerraformCLIError(exc.stderr or exc.stdout or "Terraform command failed") from exc
    return _CommandResult(stdout=proc.stdout, stderr=proc.stderr)


def _workspace_path(path: str) -> Path:
    workspace = Path(path)
    if not workspace.exists():
        raise TerraformCLIError(f"Terraform workspace directory {workspace} does not exist")
    return workspace


def run_terraform_plan(
    request: Annotated[PlanRequest, Field(description="Terraform plan request parameters")]
) -> PlanArtifact:
    """Run terraform plan and convert to PlanArtifact."""

    workspace = _workspace_path(request.workspace_dir)
    terraform = settings.tf_cli_path
    logger.info("[TF] Initializing workspace %s", workspace)
    init_cmd = [terraform, "init", "-input=false"]
    for key, value in request.backend_config.items():
        init_cmd.append(f"-backend-config={key}={value}")
    _run_terraform(init_cmd, cwd=workspace)
    logger.info("[TF] Selecting workspace %s", request.terraform_workspace)
    _run_terraform([terraform, "workspace", "select", request.terraform_workspace], cwd=workspace)

    plan_file = workspace / f"plan-{request.ticket_id}.tfplan"
    cmd = [terraform, "plan", "-input=false", f"-out={plan_file}"]
    for key, value in request.variables.items():
        cmd.append(f"-var={key}={value}")
    logger.info("[TF] Generating plan for ticket %s", request.ticket_id)
    _run_terraform(cmd, cwd=workspace)
    show = _run_terraform([terraform, "show", "-json", str(plan_file)], cwd=workspace)
    plan_json = json.loads(show.stdout) if show.stdout else {}
    plan_artifact = _parse_plan_output(request, plan_json, str(plan_file))
    return plan_artifact


def run_terraform_apply(
    request: Annotated[ApplyRequest, Field(description="Terraform apply request parameters")]
) -> ApplyResult:
    """Apply terraform changes."""

    workspace = _workspace_path(request.workspace_dir)
    terraform = settings.tf_cli_path
    cmd = [terraform, "apply", "-input=false"]
    if request.auto_approve:
        cmd.append("-auto-approve")
    if request.plan_path:
        cmd.append(request.plan_path)
    logger.info("[TF] Applying plan for ticket %s", request.ticket_id)
    try:
        result = _run_terraform(cmd, cwd=workspace)
        success = True
        stderr = result.stderr or None
        stdout = result.stdout
    except TerraformCLIError as exc:
        logger.error("[TF] Apply failed: %s", exc)
        success = False
        stdout = ""
        stderr = str(exc)
    return ApplyResult(ticket_id=request.ticket_id, success=success, stdout=stdout, stderr=stderr)


def run_drift_check(
    request: Annotated[DriftRequest, Field(description="Terraform drift detection request")]
) -> DriftReport:
    """Perform drift detection by running plan without desired changes."""

    plan_request = PlanRequest(
        ticket_id=f"drift-{request.ticket_id}",
        workspace_dir=request.workspace_dir,
        terraform_workspace=request.terraform_workspace,
    )
    try:
        plan = run_terraform_plan(plan_request)
    except TerraformCLIError as exc:
        logger.error("Drift detection failed: %s", exc)
        raise

    findings = [
        DriftFinding(
            address=change.address,
            detected_at=datetime.now(timezone.utc),
            drift_type="configuration" if change.action != "no_op" else "unknown",
            details={"summary": change.summary},
        )
        for change in plan.changes
        if change.action != "no_op"
    ]

    return DriftReport(
        ticket_id=request.ticket_id,
        plan_id=plan.plan_id,
        timestamp_utc=datetime.now(timezone.utc),
        findings=findings,
    )


def _parse_plan_output(request: PlanRequest, plan_json: dict, plan_file: str) -> PlanArtifact:
    changes: list[PlanResourceChange] = []
    resource_changes = plan_json.get("resource_changes", [])
    for change in resource_changes:
        actions = change.get("change", {}).get("actions", [])
        action = actions[0] if actions else "no_op"
        summary = change.get("address", "")
        changes.append(
            PlanResourceChange(
                address=change.get("address", "unknown"),
                action=action,
                resource_type=change.get("type", ""),
                summary=summary,
            )
        )
    summary_text = f"{len(changes)} resource change(s) detected"
    now = datetime.now(timezone.utc)
    return PlanArtifact(
        plan_id=f"plan-{request.ticket_id}-{int(now.timestamp())}",
        ticket_id=request.ticket_id,
        workspace=request.terraform_workspace,
        timestamp_utc=now,
        raw_plan_path=plan_file,
        changes=changes,
        summary=summary_text,
        terraform_version=plan_json.get("terraform_version"),
    )
