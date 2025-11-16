import importlib


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("OSS_MODEL_ENDPOINT", "https://models.example.com/v1")
    monkeypatch.setenv("OSS_MODEL_API_KEY", "oss-key")
    monkeypatch.setenv("CODEX_API_KEY", "codex-key")
    config = importlib.import_module("app.config")
    importlib.reload(config)
    settings = config.Settings()
    assert str(settings.oss_model_endpoint) == "https://models.example.com/v1"
    assert settings.oss_model_api_key == "oss-key"
    assert settings.codex_api_key == "codex-key"
