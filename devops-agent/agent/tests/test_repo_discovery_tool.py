import asyncio

from app.tools.repo_discovery_tool import RepoDiscoveryOutput, _discover_repos


def test_repo_discovery_success(monkeypatch):
    async def fake_get_unmanaged():
        unmanaged = [
            {
                "name": "repo-a",
                "full_name": "acme/repo-a",
                "clone_url": "https://github.com/acme/repo-a.git",
                "default_branch": "main",
                "private": True,
            }
        ]
        managed = []
        return unmanaged, managed

    monkeypatch.setattr("app.services.repo_discovery.get_unmanaged_github_repos", fake_get_unmanaged)

    output = asyncio.run(_discover_repos())
    assert isinstance(output, RepoDiscoveryOutput)
    assert output.unmanaged_repos and output.managed_repos == []
    assert output.message is None


def test_repo_discovery_error(monkeypatch):
    async def fake_get_unmanaged():
        raise ValueError("boom")

    monkeypatch.setattr("app.services.repo_discovery.get_unmanaged_github_repos", fake_get_unmanaged)

    output = asyncio.run(_discover_repos())
    assert output.unmanaged_repos == []
    assert output.managed_repos == []
    assert output.message and "boom" in output.message
