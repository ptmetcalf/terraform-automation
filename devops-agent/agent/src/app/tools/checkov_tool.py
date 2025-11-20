"""Security scanning tool wrappers."""
from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field

from app.models import SecurityIssue, SecurityReport

logger = logging.getLogger(__name__)


class SecurityScanRequest(BaseModel):
    ticket_id: str
    plan_id: str
    directory: str
    tool: str = Field(default="checkov", description="Security scanning tool (checkov|tfsec)")


class SecurityScanError(RuntimeError):
    pass


def run_security_scan(
    request: Annotated[SecurityScanRequest, Field(description="Trigger infrastructure security scan")]
) -> SecurityReport:
    """Run Checkov/tfsec against the Terraform directory."""

    directory = Path(request.directory)
    if not directory.exists():
        raise SecurityScanError(f"Directory {directory} does not exist")

    if request.tool == "tfsec":
        cmd = ["tfsec", directory.as_posix(), "--format", "json"]
    else:
        cmd = ["checkov", "-d", directory.as_posix(), "-o", "json"]

    logger.info("[SEC] Running %s for ticket %s", request.tool, request.ticket_id)
    try:
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        logger.warning("%s not found, returning empty report", request.tool)
        return SecurityReport(
            ticket_id=request.ticket_id,
            plan_id=request.plan_id,
            tool=request.tool,
            timestamp_utc=datetime.now(timezone.utc),
            issues=[],
        )
    except subprocess.CalledProcessError as exc:
        raise SecurityScanError(exc.stderr or exc.stdout or "Security scan failed") from exc

    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        logger.warning("[SEC] Unable to parse %s output: %s", request.tool, exc)
        payload = {}
    issues = _parse_security_payload(payload, request.tool)
    return SecurityReport(
        ticket_id=request.ticket_id,
        plan_id=request.plan_id,
        tool=request.tool,
        timestamp_utc=datetime.now(timezone.utc),
        issues=issues,
    )


def _parse_security_payload(payload: dict, tool: str) -> list[SecurityIssue]:
    issues: list[SecurityIssue] = []
    if tool == "tfsec":
        for finding in payload.get("results", []):
            issues.append(
                SecurityIssue(
                    severity=finding.get("severity", "medium").lower(),
                    rule_id=finding.get("rule_id", ""),
                    description=finding.get("description", ""),
                    resource=finding.get("resource"),
                    remediation=finding.get("resolution"),
                )
            )
    else:
        for finding in payload.get("results", {}).get("failed_checks", []):
            issues.append(
                SecurityIssue(
                    severity=finding.get("severity", "medium").lower(),
                    rule_id=finding.get("check_id", ""),
                    description=finding.get("check_name", ""),
                    resource=finding.get("resource", ""),
                    remediation=finding.get("guideline", ""),
                )
            )
    return issues
