"""Repo discovery helpers for onboarding accessible repositories."""
from __future__ import annotations

import os
from typing import Any

import httpx

from app.services import project_store


async def _fetch_github_repos(token: str, per_page: int = 100, max_pages: int = 5) -> list[dict[str, Any]]:
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    repos: list[dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=20) as client:
        page = 1
        while page <= max_pages:
            response = await client.get(
                url,
                headers=headers,
                params={"per_page": per_page, "page": page, "sort": "updated"},
            )
            response.raise_for_status()
            batch = response.json()
            if not batch:
                break
            repos.extend(batch)
            page += 1
    return repos


async def discover_github_repos() -> list[dict[str, Any]]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GIT_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN is required to discover GitHub repositories")
    return await _fetch_github_repos(token)


async def get_unmanaged_github_repos() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    repos = await discover_github_repos()
    existing_urls = {str(url) for url in await project_store.list_project_repo_urls()}
    unmanaged: list[dict[str, Any]] = []
    managed: list[dict[str, Any]] = []
    for repo in repos:
        clone_url = repo.get("clone_url")
        html_url = repo.get("html_url")
        if clone_url in existing_urls or html_url in existing_urls:
            managed.append(repo)
        else:
            unmanaged.append(repo)
    return unmanaged, managed
