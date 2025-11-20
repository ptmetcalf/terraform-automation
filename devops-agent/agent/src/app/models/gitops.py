"""GitOps request/response models."""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


class FileEdit(BaseModel):
    path: str
    content: str
    mode: Literal["overwrite", "append", "delete"] = "overwrite"


class GitOpsChangeRequest(BaseModel):
    ticket_id: str
    repo: Optional[str] = None
    root_path: str
    base_branch: str
    preferred_branch_name: str
    file_edits: List[FileEdit] = Field(default_factory=list)


class GitOpsResult(BaseModel):
    ticket_id: str
    result: Literal["success", "error"]
    branch: Optional[str]
    pull_request_url: Optional[HttpUrl]
    ci_status: Optional[Literal["pending", "success", "failed"]]
    error_message: Optional[str]
