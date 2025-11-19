"""Models describing tool health and connectivity."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ToolStatus(BaseModel):
    name: str = Field(description="Unique identifier for the tool or integration")
    description: str
    available: bool = Field(description="Whether the supervisor can currently use this tool")
    reason: str | None = Field(
        default=None, description="Optional explanation when a tool is unavailable or degraded"
    )


class ToolsHealthResponse(BaseModel):
    items: list[ToolStatus] = Field(default_factory=list)
