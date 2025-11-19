"""Chat request/response models shared across APIs and tools."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl


class ChatRequest(BaseModel):
    message: str
    requested_by: str
    environment: Optional[str] = "dev"
    thread_id: Optional[str] = None
    project_id: Optional[str] = Field(default=None, description="Known project identifier")
    terraform_workspace: Optional[str] = None
    workspace_dir: Optional[str] = None
    repo_url: Optional[HttpUrl] = None
    branch: Optional[str] = "main"
    intent_summary: str | None = None


class ChatResponse(BaseModel):
    ticket_id: str
    thread_id: str
    status: str
    workflow_outputs: list[Any] = Field(default_factory=list)
