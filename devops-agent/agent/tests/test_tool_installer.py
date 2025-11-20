import importlib
from pathlib import Path


def reload_module():
    module = importlib.import_module("app.services.tool_installer")
    importlib.reload(module)
    return module


def test_resolve_install_dir_explicit(tmp_path, monkeypatch):
    monkeypatch.delenv("TOOLS_INSTALL_DIR", raising=False)
    module = reload_module()
    result = module._resolve_install_dir(tmp_path)
    assert result == tmp_path


def test_resolve_install_dir_env(tmp_path, monkeypatch):
    monkeypatch.setenv("TOOLS_INSTALL_DIR", str(tmp_path))
    module = reload_module()
    result = module._resolve_install_dir(None)
    assert result == tmp_path


def test_resolve_install_dir_default(monkeypatch):
    monkeypatch.delenv("TOOLS_INSTALL_DIR", raising=False)
    module = reload_module()
    result = module._resolve_install_dir(None)
    assert result == Path(".tools/bin").expanduser()
