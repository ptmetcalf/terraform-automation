"""Chat request/response models shared across APIs and tools."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl


class ChatRequest(BaseModel):
    message: str
    requested_by: str
    environment: str = "dev"
    thread_id: Optional[str] = None
    terraform_workspace: str
    repo_url: HttpUrl
    branch: str = "main"
    intent_summary: str | None = None


class ChatResponse(BaseModel):
    ticket_id: str
    thread_id: str
    status: str
    workflow_outputs: list[Any] = Field(default_factory=list)
