"""Artifact store for plan, security, cost, and drift outputs."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select

from app.models import CostReport, DriftReport, PlanArtifact, SecurityReport
from app.services.database import artifacts_table, database


class ArtifactStore:
    """Persist artifacts as JSON blobs with type metadata."""

    async def save_plan(self, plan: PlanArtifact) -> PlanArtifact:
        await self._upsert(artifact_id=plan.plan_id, artifact_type="plan", ticket_id=plan.ticket_id, payload=plan.model_dump(mode="json"))
        return plan

    async def save_security_report(self, report: SecurityReport) -> SecurityReport:
        artifact_id = self._build_artifact_id("security", report.ticket_id, report.plan_id, report.timestamp_utc.isoformat())
        await self._upsert(artifact_id, "security", report.ticket_id, report.model_dump(mode="json"))
        return report

    async def save_cost_report(self, report: CostReport) -> CostReport:
        artifact_id = self._build_artifact_id("cost", report.ticket_id, report.plan_id, report.timestamp_utc.isoformat())
        await self._upsert(artifact_id, "cost", report.ticket_id, report.model_dump(mode="json"))
        return report

    async def save_drift_report(self, report: DriftReport) -> DriftReport:
        artifact_id = self._build_artifact_id("drift", report.ticket_id, report.plan_id, report.timestamp_utc.isoformat())
        await self._upsert(artifact_id, "drift", report.ticket_id, report.model_dump(mode="json"))
        return report

    async def list_artifacts(self, ticket_id: str, *, artifact_type: Optional[str] = None) -> List[dict]:
        query = select(artifacts_table.c.artifact_type, artifacts_table.c.content).where(
            artifacts_table.c.ticket_id == ticket_id
        )
        if artifact_type:
            query = query.where(artifacts_table.c.artifact_type == artifact_type)
        rows = await database.fetch_all(query)
        artifacts: list[dict] = []
        for row in rows:
            content = row["content"]
            if isinstance(content, str):
                import json

                content = json.loads(content)
            artifacts.append(content)
        return artifacts

    async def _upsert(self, artifact_id: str, artifact_type: str, ticket_id: str, payload: dict) -> None:
        exists_query = select(artifacts_table.c.artifact_id).where(artifacts_table.c.artifact_id == artifact_id)
        exists = await database.fetch_one(exists_query)
        created_at = payload.get("timestamp_utc")
        if isinstance(created_at, str):
            from datetime import datetime, timezone

            try:
                created_at = datetime.fromisoformat(created_at)
            except ValueError:
                created_at = datetime.now(timezone.utc)
        values = {
            "artifact_id": artifact_id,
            "ticket_id": ticket_id,
            "artifact_type": artifact_type,
            "content": payload,
            "created_at": created_at,
        }
        if exists:
            query = artifacts_table.update().where(artifacts_table.c.artifact_id == artifact_id).values(values)
        else:
            query = artifacts_table.insert().values(values)
        await database.execute(query)

    @staticmethod
    def _build_artifact_id(artifact_type: str, ticket_id: str, plan_id: Optional[str], unique_part: str) -> str:
        if plan_id:
            return f"{artifact_type}:{plan_id}"
        return f"{artifact_type}:{ticket_id}:{unique_part}"


artifact_store = ArtifactStore()
