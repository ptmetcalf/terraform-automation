"""Project configuration models used for onboarding infrastructure repos."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import AnyUrl, BaseModel, Field, HttpUrl

ProjectType = Literal["terraform", "python-container"]


class ProjectBase(BaseModel):
    name: str = Field(description="Human-friendly project name")
    description: Optional[str] = Field(default=None, description="Optional description")
    repo_url: AnyUrl = Field(description="Git repository containing infrastructure code")
    workspace_dir: str = Field(description="Path to the Terraform workspace directory on disk")
    default_environment: str = Field(default="dev", description="Default environment alias (dev/stage/prod)")
    default_branch: str = Field(default="main", description="Default Git branch to base plans from")
    project_type: ProjectType = Field(default="terraform", description="Type of project (terraform, python-container)")
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProjectCreate(ProjectBase):
    project_id: Optional[str] = Field(default=None, description="Optional slug/identifier for the project")


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    repo_url: Optional[HttpUrl] = None
    workspace_dir: Optional[str] = None
    default_environment: Optional[str] = None
    default_branch: Optional[str] = None
    project_type: Optional[ProjectType] = None
    metadata: Optional[dict[str, Any]] = None


class Project(ProjectBase):
    project_id: str
    created_at: datetime
    updated_at: datetime


class ProjectList(BaseModel):
    items: list[Project]
