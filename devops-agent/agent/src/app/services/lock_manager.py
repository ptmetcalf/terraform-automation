"""Coarse-grained workspace lock manager."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import and_, select

from app.models import WorkspaceLock
from app.services.database import database, locks_table


class LockManager:
    async def acquire_lock(self, workspace: str, ticket_id: str, purpose: str) -> Optional[WorkspaceLock]:
        """Try to acquire a workspace lock. Returns lock info when successful."""

        query = select(locks_table).where(
            and_(locks_table.c.workspace == workspace, locks_table.c.status != "released")
        )
        existing = await database.fetch_one(query)
        if existing:
            return None
        lock = WorkspaceLock(
            lock_id=str(uuid4()),
            workspace=workspace,
            ticket_id=ticket_id,
            status=f"locked_for_{purpose}",
            locked_at=datetime.now(timezone.utc),
        )
        await database.execute(locks_table.insert().values(**lock.model_dump()))
        return lock

    async def release_lock(self, lock_id: str) -> None:
        await database.execute(locks_table.delete().where(locks_table.c.lock_id == lock_id))

    async def get_active_lock(self, workspace: str) -> Optional[WorkspaceLock]:
        query = select(locks_table).where(locks_table.c.workspace == workspace)
        record = await database.fetch_one(query)
        if not record:
            return None
        return WorkspaceLock.model_validate(record)


lock_manager = LockManager()
