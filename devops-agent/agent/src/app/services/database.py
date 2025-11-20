"""Database helpers and table metadata."""
from __future__ import annotations

from typing import Optional

from databases import Database
from sqlalchemy import JSON, Column, DateTime, MetaData, String, Table, Text, create_engine, text, inspect

from app.config import settings

metadata = MetaData()


tickets_table = Table(
    "tickets",
    metadata,
    Column("ticket_id", String, primary_key=True),
    Column("thread_id", String, nullable=False, index=True),
    Column("status", String, nullable=False),
    Column("payload", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


artifacts_table = Table(
    "artifacts",
    metadata,
    Column("artifact_id", String, primary_key=True),
    Column("ticket_id", String, index=True, nullable=False),
    Column("artifact_type", String, nullable=False),
    Column("content", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

projects_table = Table(
    "projects",
    metadata,
    Column("project_id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("description", Text, nullable=True),
    Column("repo_url", String, nullable=False),
    Column("workspace_dir", String, nullable=False),
    Column("default_environment", String, nullable=False),
    Column("default_branch", String, nullable=False),
    Column("project_type", String, nullable=False, server_default="terraform"),
    Column("metadata", JSON, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


locks_table = Table(
    "workspace_locks",
    metadata,
    Column("lock_id", String, primary_key=True),
    Column("workspace", String, index=True, nullable=False),
    Column("ticket_id", String, nullable=False),
    Column("status", String, nullable=False),
    Column("locked_at", DateTime(timezone=True), nullable=False),
)


audits_table = Table(
    "audit_events",
    metadata,
    Column("event_id", String, primary_key=True),
    Column("ticket_id", String, nullable=False, index=True),
    Column("actor", String, nullable=False),
    Column("actor_type", String, nullable=False),
    Column("action", String, nullable=False),
    Column("metadata", JSON, nullable=True),
    Column("timestamp", DateTime(timezone=True), nullable=False),
)


def _sync_database_url(url: str) -> str:
    if "+aiosqlite" in url:
        return url.replace("+aiosqlite", "", 1)
    return url


database = Database(settings.database_url)


async def init_database() -> None:
    """Create tables and open DB connection."""

    sync_url = _sync_database_url(settings.database_url)
    engine = create_engine(sync_url)
    metadata.create_all(engine)
    _ensure_project_schema(engine)
    await database.connect()


async def shutdown_database() -> None:
    """Close DB connection."""

    if database.is_connected:
        await database.disconnect()


def _ensure_project_schema(engine) -> None:
    inspector = inspect(engine)
    if "projects" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("projects")}
    if "project_type" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE projects ADD COLUMN project_type TEXT DEFAULT 'terraform'"))
