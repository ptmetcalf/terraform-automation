"""Project registry service for storing repo/workspace metadata."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


from app.models.project import Project, ProjectCreate, ProjectUpdate
from app.services.database import database, projects_table


def generate_project_id(name: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")
    slug = "-".join(filter(None, slug.split("-")))
    return slug or f"project-{int(datetime.now(timezone.utc).timestamp())}"


async def list_projects() -> list[Project]:
    query = projects_table.select()
    rows = await database.fetch_all(query)
    return [Project(**row) for row in rows]


async def list_project_repo_urls() -> set[str]:
    projects = await list_projects()
    urls: set[str] = set()
    for project in projects:
        urls.add(str(project.repo_url))
    return urls


async def get_project(project_id: str) -> Optional[Project]:
    query = projects_table.select().where(projects_table.c.project_id == project_id)
    row = await database.fetch_one(query)
    return Project(**row) if row else None


async def create_project(payload: ProjectCreate) -> Project:
    project_id = payload.project_id or generate_project_id(payload.name)
    now = datetime.now(timezone.utc)
    values = {
        "project_id": project_id,
        "name": payload.name,
        "description": payload.description,
        "repo_url": str(payload.repo_url),
        "workspace_dir": payload.workspace_dir,
        "default_environment": payload.default_environment,
        "default_branch": payload.default_branch,
        "project_type": payload.project_type,
        "metadata": payload.metadata,
        "created_at": now,
        "updated_at": now,
    }
    await database.execute(projects_table.insert().values(values))
    return Project(**values)


async def update_project(project_id: str, payload: ProjectUpdate) -> Optional[Project]:
    current = await get_project(project_id)
    if current is None:
        return None
    data = payload.model_dump(exclude_unset=True)
    if not data:
        return current
    data["updated_at"] = datetime.now(timezone.utc)
    if "repo_url" in data and data["repo_url"] is not None:
        data["repo_url"] = str(data["repo_url"])
    await database.execute(projects_table.update().where(projects_table.c.project_id == project_id).values(data))
    updated = current.model_copy(update=data)
    return updated


async def delete_project(project_id: str) -> None:
    await database.execute(projects_table.delete().where(projects_table.c.project_id == project_id))
