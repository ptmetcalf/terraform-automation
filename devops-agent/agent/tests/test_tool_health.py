from app.services.tool_health import list_tool_statuses


def _status_by_name(statuses, name):
    return next(status for status in statuses if status.name == name)


def test_tool_health_available(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("GITHUB_MCP_COMMAND", "/bin/echo")
    monkeypatch.setenv("TERRAFORM_MCP_COMMAND", "/bin/echo")
    monkeypatch.setenv("MSLEARN_MCP_URL", "https://example.com")

    statuses = list_tool_statuses()
    assert _status_by_name(statuses, "github_mcp").available is True
    assert _status_by_name(statuses, "github_rest").available is True
    assert _status_by_name(statuses, "terraform_mcp").available is True
    assert _status_by_name(statuses, "ms_learn_mcp").available is True


def test_tool_health_missing(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("GITHUB_MCP_COMMAND", "")
    monkeypatch.setenv("TERRAFORM_MCP_COMMAND", "")
    monkeypatch.delenv("MSLEARN_MCP_URL", raising=False)

    statuses = list_tool_statuses()
    assert _status_by_name(statuses, "github_mcp").available is False
    assert _status_by_name(statuses, "github_rest").available is False
    assert _status_by_name(statuses, "terraform_mcp").available is False
    assert _status_by_name(statuses, "ms_learn_mcp").available is False
