"""Project registry API."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.models.project import Project, ProjectCreate, ProjectList, ProjectUpdate
from app.services import project_store

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=ProjectList)
async def list_projects() -> ProjectList:
    projects = await project_store.list_projects()
    return ProjectList(items=projects)


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate) -> Project:
    return await project_store.create_project(payload)


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str) -> Project:
    project = await project_store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, payload: ProjectUpdate) -> Project:
    project = await project_store.update_project(project_id, payload)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str) -> None:
    project = await project_store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    await project_store.delete_project(project_id)
