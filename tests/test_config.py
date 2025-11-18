import importlib


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("OSS_MODEL_ENDPOINT", "https://models.example.com/v1")
    monkeypatch.setenv("OSS_MODEL_API_KEY", "oss-key")
    monkeypatch.setenv("OSS_MODEL_ID", "openai/gpt-oss-20b")
    monkeypatch.setenv("CODEX_API_KEY", "codex-key")
    config = importlib.import_module("app.config")
    importlib.reload(config)
    config.Settings.model_config["env_file"] = ()
    settings = config.Settings()
    assert str(settings.oss_model_endpoint) == "https://models.example.com/v1"
    assert settings.oss_model_api_key == "oss-key"
    assert settings.oss_model_id == "openai/gpt-oss-20b"
    assert settings.codex_api_key == "codex-key"


def test_oss_model_api_key_optional(monkeypatch):
    monkeypatch.setenv("OSS_MODEL_ENDPOINT", "https://models.example.com/v1")
    monkeypatch.delenv("OSS_MODEL_API_KEY", raising=False)
    monkeypatch.delenv("OSS_MODEL_ID", raising=False)
    monkeypatch.setenv("CODEX_API_KEY", "codex-key")
    config = importlib.import_module("app.config")
    importlib.reload(config)
    config.Settings.model_config["env_file"] = ()
    settings = config.Settings()
    assert settings.oss_model_api_key is None
    assert settings.oss_model_id == "openai/gpt-oss-20b"


def test_oss_model_id_override(monkeypatch):
    monkeypatch.setenv("OSS_MODEL_ENDPOINT", "https://models.example.com/v1")
    monkeypatch.setenv("CODEX_API_KEY", "codex-key")
    monkeypatch.setenv("OSS_MODEL_ID", "custom-model")
    config = importlib.import_module("app.config")
    importlib.reload(config)
    config.Settings.model_config["env_file"] = ()
    settings = config.Settings()
    assert settings.oss_model_id == "custom-model"
