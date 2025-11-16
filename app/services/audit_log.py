"""Audit logging to support Dev UI observability."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel
from sqlalchemy import select

from app.services.database import audits_table, database


class AuditEvent(BaseModel):
    event_id: str
    ticket_id: str
    actor: str
    actor_type: str
    action: str
    timestamp: datetime
    metadata: Dict[str, str] | None = None


class AuditLogService:
    async def record_event(self, event: AuditEvent) -> None:
        await database.execute(audits_table.insert().values(**event.model_dump()))

    async def list_events(self, ticket_id: str) -> List[AuditEvent]:
        query = select(audits_table).where(audits_table.c.ticket_id == ticket_id)
        rows = await database.fetch_all(query)
        return [AuditEvent.model_validate(dict(row)) for row in rows]


audit_log = AuditLogService()
