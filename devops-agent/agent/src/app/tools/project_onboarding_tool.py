"""Tool for creating new project entries via the supervisor agent."""
from __future__ import annotations

from pathlib import Path

from agent_framework import AIFunction
from git import Repo
from pydantic import AnyUrl, BaseModel, Field

from app.config import settings
from app.models.project import Project, ProjectCreate, ProjectType
from app.services import project_store


class ProjectOnboardingInput(BaseModel):
    name: str = Field(description="Human-friendly project name")
    description: str | None = Field(default=None, description="Optional description")
    repo_url: AnyUrl = Field(description="Git repository containing infrastructure code")
    workspace_dir: str | None = Field(default=None, description="Optional pre-existing workspace directory")
    default_environment: str = Field(default="dev", description="Default environment alias")
    default_branch: str = Field(default="main", description="Default Git branch to base plans from")
    project_type: ProjectType = Field(default="terraform", description="Type of project (terraform, python-container)")
    project_id: str | None = Field(default=None, description="Optional slug identifier")


async def _create_project(inputs: ProjectOnboardingInput) -> Project:
    project_id = inputs.project_id or project_store.generate_project_id(inputs.name)
    workspace_dir = inputs.workspace_dir

    if workspace_dir is None:
        projects_root = Path(settings.projects_root).expanduser()
        projects_root.mkdir(parents=True, exist_ok=True)
        destination = projects_root / project_id
        if destination.exists():
            raise ValueError(f"Workspace path {destination} already exists")
        try:
            Repo.clone_from(str(inputs.repo_url), destination, branch=inputs.default_branch)
        except Exception as exc:  # pragma: no cover - network/IO error
            raise ValueError(f"Failed to clone repository: {exc}") from exc
        workspace_dir = str(destination)

    payload = ProjectCreate(
        project_id=project_id,
        name=inputs.name,
        description=inputs.description,
        repo_url=inputs.repo_url,
        workspace_dir=workspace_dir,
        default_environment=inputs.default_environment,
        default_branch=inputs.default_branch,
        project_type=inputs.project_type,
    )
    return await project_store.create_project(payload)


project_onboarding_tool = AIFunction(
    name="create_project",
    description="Register a new infrastructure project (repo, workspace, environment defaults).",
    func=_create_project,
    input_model=ProjectOnboardingInput,
    output_model=Project,
    approval_mode="never_require",
    max_invocations=1,
)
