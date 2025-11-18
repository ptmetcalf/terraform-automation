from fastapi.testclient import TestClient

from app.api.routes_capabilities import router as capabilities_router
from app.capabilities import get_capabilities, get_capability
from app.main import api_app


def test_capability_registry_contains_supervisor():
    capabilities = {cap.slug: cap for cap in get_capabilities()}
    assert "supervisor" in capabilities
    assert capabilities["supervisor"].approval_required is False


def test_get_capability_by_slug():
    capability = get_capability("devops")
    assert capability is not None
    assert "/approve plan" in capability.approval_commands


def test_capabilities_api_list(monkeypatch):
    client = TestClient(api_app)
    response = client.get("/api/capabilities")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert any(item["slug"] == "devops" for item in payload)


def test_capabilities_api_detail():
    client = TestClient(api_app)
    response = client.get("/api/capabilities/supervisor")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "supervisor"


def test_capabilities_api_not_found():
    client = TestClient(api_app)
    response = client.get("/api/capabilities/unknown")
    assert response.status_code == 404
