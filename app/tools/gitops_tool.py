"""GitOps utility functions."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated

from git import Repo
from pydantic import Field

from app.models import GitOpsChangeRequest, GitOpsResult

logger = logging.getLogger(__name__)


class GitOpsError(RuntimeError):
    pass


def apply_git_changes(
    request: Annotated[GitOpsChangeRequest, Field(description="Proposed GitOps change request")]
) -> GitOpsResult:
    """Apply file edits inside a repository and open a branch."""

    repo_path = Path(request.repo)
    if not repo_path.exists():
        raise GitOpsError(f"Repo path {repo_path} is missing")

    repo = Repo(repo_path)
    normalized_ticket = request.ticket_id.replace(" ", "-").lower()
    if normalized_ticket not in request.preferred_branch_name.lower():
        raise GitOpsError("Branch name must include the ticket identifier for traceability")
    try:
        repo.config_reader().get_value("user", "name")
    except Exception:  # pragma: no cover - config fallback
        writer = repo.config_writer()
        writer.set_value("user", "name", "Terraform Agent Bot")
        writer.set_value("user", "email", "terraform-agent@example.com")
        writer.release()
    if repo.is_dirty(untracked_files=True):
        raise GitOpsError("Repository has dirty state; aborting GitOps changes")

    base_branch = request.base_branch
    target_branch = request.preferred_branch_name
    repo.git.checkout(base_branch)
    repo.git.checkout("-B", target_branch)

    edited_paths: list[str] = []
    for edit in request.file_edits:
        file_path = repo_path / edit.path
        if edit.mode == "delete":
            if file_path.exists():
                file_path.unlink()
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if edit.mode == "append" and file_path.exists():
                with file_path.open("a", encoding="utf-8") as handle:
                    handle.write(edit.content)
            else:
                file_path.write_text(edit.content, encoding="utf-8")
        edited_paths.append(str(file_path.relative_to(repo_path)))

    repo.index.add(edited_paths)
    repo.index.commit(f"GitOps changes for ticket {request.ticket_id}")
    logger.info("[GITOPS] Created branch %s with %d edits", target_branch, len(edited_paths))

    return GitOpsResult(
        ticket_id=request.ticket_id,
        result="success",
        branch=target_branch,
        pull_request_url=None,
        ci_status="pending",
        error_message=None,
    )


def get_repo_status(repo_path: Annotated[str, Field(description="Path to clone directory")]) -> dict:
    repo = Repo(Path(repo_path))
    return {
        "active_branch": str(repo.active_branch),
        "dirty": repo.is_dirty(untracked_files=True),
        "head": repo.head.commit.hexsha if repo.head.is_valid() else None,
    }
