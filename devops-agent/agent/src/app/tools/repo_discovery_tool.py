"""Fallback tool to list GitHub repositories via REST API when MCP is unavailable."""
from __future__ import annotations

import logging
from typing import Literal

from agent_framework import AIFunction
from pydantic import BaseModel, Field, HttpUrl

from app.services import repo_discovery

logger = logging.getLogger(__name__)


class RepoRecord(BaseModel):
    name: str
    full_name: str
    clone_url: HttpUrl
    default_branch: str
    private: bool


class RepoDiscoveryOutput(BaseModel):
    provider: Literal["github"]
    unmanaged_repos: list[RepoRecord] = Field(description="Repos accessible but not yet onboarded")
    managed_repos: list[RepoRecord] = Field(description="Repos already registered as projects")
    message: str | None = Field(
        default=None, description="Optional status or error message when discovery cannot complete"
    )


async def _discover_repos() -> RepoDiscoveryOutput:
    try:
        unmanaged_raw, managed_raw = await repo_discovery.get_unmanaged_github_repos()

        def _convert(raw: dict) -> RepoRecord:
            return RepoRecord(
                name=raw.get("name", ""),
                full_name=raw.get("full_name", ""),
                clone_url=raw.get("clone_url", raw.get("html_url")),
                default_branch=raw.get("default_branch", "main"),
                private=raw.get("private", False),
            )

        return RepoDiscoveryOutput(
            provider="github",
            unmanaged_repos=[_convert(repo) for repo in unmanaged_raw],
            managed_repos=[_convert(repo) for repo in managed_raw],
        )
    except Exception as exc:  # pragma: no cover
        logger.warning("Repo discovery failed: %s", exc)
        return RepoDiscoveryOutput(
            provider="github",
            unmanaged_repos=[],
            managed_repos=[],
            message=f"Repo discovery failed: {exc}",
        )


repo_discovery_tool = AIFunction(
    name="discover_repos",
    description="List accessible GitHub repositories via REST API (fallback when MCP isn't available).",
    func=_discover_repos,
    output_model=RepoDiscoveryOutput,
    approval_mode="never_require",
    max_invocations=1,
)
