import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from git import Repo

from app.config import settings
from app.services.database import database, projects_table
from app.tools.project_onboarding_tool import ProjectOnboardingInput, _create_project


def test_project_onboarding_clones_repo(tmp_path):
    # Set up source repo
    source = tmp_path / "source"
    source.mkdir()
    repo = Repo.init(source)
    readme = source / "README.md"
    readme.write_text("# demo repo\n")
    repo.index.add(["README.md"])
    repo.index.commit("init")
    branch_name = repo.active_branch.name

    original_root = settings.projects_root
    settings.projects_root = str(tmp_path / "projects")
    try:
        payload = ProjectOnboardingInput(
            name="Clone Demo",
            repo_url=source.as_uri(),
            workspace_dir=None,
            default_environment="dev",
            default_branch=branch_name,
            project_type="terraform",
        )
        project = asyncio.run(_create_project(payload))
        cloned_path = Path(project.workspace_dir)
        assert cloned_path.exists()
        assert (cloned_path / "README.md").exists()
    finally:
        settings.projects_root = original_root
        asyncio.run(database.execute(projects_table.delete()))
