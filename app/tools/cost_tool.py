"""Cost estimation helper tool."""
from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field

from app.models import CostComponent, CostReport

logger = logging.getLogger(__name__)


class CostEstimateRequest(BaseModel):
    ticket_id: str
    plan_id: str
    directory: str
    usage_file: str | None = Field(default=None, description="Optional Infracost usage file")


class CostEstimationError(RuntimeError):
    pass


def estimate_cost(
    request: Annotated[CostEstimateRequest, Field(description="Estimate Terraform cost impact")]
) -> CostReport:
    """Estimate monthly cost deltas using Infracost when available."""

    directory = Path(request.directory)
    if not directory.exists():
        raise CostEstimationError(f"Directory {directory} does not exist")

    cmd = ["infracost", "breakdown", f"--path={directory.as_posix()}", "--format", "json"]
    if request.usage_file:
        cmd.append(f"--usage-file={request.usage_file}")

    logger.info("[COST] Running infracost for ticket %s", request.ticket_id)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        payload = json.loads(proc.stdout or "{}")
        total_monthly_cost = payload.get("projects", [{}])[0].get("diff", {}).get("totalMonthlyCost", 0.0)
        delta = payload.get("projects", [{}])[0].get("diff", {}).get("totalMonthlyDiff", 0.0)
        components = _parse_components(payload)
    except FileNotFoundError:
        logger.warning("Infracost not found, returning zero cost report")
        total_monthly_cost = 0.0
        delta = 0.0
        components = []
    except json.JSONDecodeError as exc:
        logger.warning("[COST] Invalid infracost JSON output: %s", exc)
        total_monthly_cost = 0.0
        delta = 0.0
        components = []
    except subprocess.CalledProcessError as exc:
        raise CostEstimationError(exc.stderr or exc.stdout or "Cost estimation failed") from exc

    return CostReport(
        ticket_id=request.ticket_id,
        plan_id=request.plan_id,
        timestamp_utc=datetime.now(timezone.utc),
        total_monthly_cost=total_monthly_cost,
        delta_monthly_cost=delta,
        currency="USD",
        components=components,
    )


def _parse_components(payload: dict) -> list[CostComponent]:
    components: list[CostComponent] = []
    for project in payload.get("projects", []):
        for resource in project.get("diff", {}).get("resources", []):
            components.append(
                CostComponent(
                    name=resource.get("name", "resource"),
                    monthly_cost=float(resource.get("monthlyCost", 0) or 0),
                    delta_monthly_cost=float(resource.get("monthlyCostDiff", 0) or 0),
                    currency=resource.get("currency", "USD"),
                )
            )
    return components
