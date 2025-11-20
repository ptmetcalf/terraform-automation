import asyncio

from fastapi.testclient import TestClient

from app.main import app
from app.services.database import database, projects_table


client = TestClient(app)


def _clear_projects():
    async def _clear():
        await database.execute(projects_table.delete())

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_clear())
    finally:
        loop.close()


def test_create_and_get_project():
    _clear_projects()
    payload = {
        "name": "Homelab Dev",
        "description": "Dev environment",
        "repo_url": "https://github.com/example/homelab.git",
        "workspace_dir": "/workspaces/homelab",
        "default_environment": "dev",
        "default_branch": "main",
        "project_type": "terraform",
    }
    response = client.post("/api/projects/", json=payload)
    assert response.status_code == 201
    body = response.json()
    project_id = body["project_id"]
    get_resp = client.get(f"/api/projects/{project_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Homelab Dev"


def test_update_project():
    _clear_projects()
    create_resp = client.post(
        "/api/projects/",
        json={
            "name": "Prod",
            "repo_url": "https://github.com/example/prod.git",
            "workspace_dir": "/workspaces/prod",
            "default_environment": "prod",
            "default_branch": "main",
            "project_type": "terraform",
        },
    )
    project_id = create_resp.json()["project_id"]
    update_resp = client.put(
        f"/api/projects/{project_id}",
        json={"default_branch": "release", "description": "Production"},
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["default_branch"] == "release"
    assert data["description"] == "Production"


def test_list_projects():
    _clear_projects()
    client.post(
        "/api/projects/",
        json={
            "name": "Project A",
            "repo_url": "https://github.com/example/a.git",
            "workspace_dir": "/workspaces/a",
            "default_environment": "dev",
            "default_branch": "main",
            "project_type": "terraform",
        },
    )
    resp = client.get("/api/projects/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Project A"
