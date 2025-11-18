"""Download and manage pinned CLI tool binaries."""
from __future__ import annotations

import logging
import os
import shutil
import stat
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.request import urlopen

try:  # Import lazily so builds/tests without config env still succeed
    from app.config import settings as _settings
except Exception:  # pragma: no cover - env may not be configured during docker build/tests
    _settings = None

logger = logging.getLogger(__name__)


ArchiveType = Literal["binary", "zip", "tar.gz"]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    version: str
    url: str
    archive: ArchiveType
    binary_name: str
    url_env: str
    version_env: str | None = None
    target_name: str | None = None

    @property
    def install_name(self) -> str:
        return self.target_name or self.binary_name


PINNED_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="terraform",
        version="1.9.5",
        url="https://releases.hashicorp.com/terraform/1.9.5/terraform_1.9.5_linux_amd64.zip",
        archive="zip",
        binary_name="terraform",
        url_env="TERRAFORM_DOWNLOAD_URL",
        version_env="TERRAFORM_VERSION",
    ),
    ToolSpec(
        name="checkov",
        version="3.2.332",
        url="https://github.com/bridgecrewio/checkov/releases/download/v3.2.332/checkov_3.2.332_linux_amd64",
        archive="binary",
        binary_name="checkov",
        url_env="CHECKOV_DOWNLOAD_URL",
        version_env="CHECKOV_VERSION",
    ),
    ToolSpec(
        name="tfsec",
        version="1.28.3",
        url="https://github.com/aquasecurity/tfsec/releases/download/v1.28.3/tfsec-linux-amd64",
        archive="binary",
        binary_name="tfsec-linux-amd64",
        target_name="tfsec",
        url_env="TFSEC_DOWNLOAD_URL",
        version_env="TFSEC_VERSION",
    ),
    ToolSpec(
        name="infracost",
        version="0.10.42",
        url="https://github.com/infracost/infracost/releases/download/v0.10.42/infracost-linux-amd64.tar.gz",
        archive="tar.gz",
        binary_name="infracost-linux-amd64",
        target_name="infracost",
        url_env="INFRACOST_DOWNLOAD_URL",
        version_env="INFRACOST_VERSION",
    ),
]


def ensure_tool_binaries(install_dir: str | Path | None = None) -> None:
    """Ensure pinned tool binaries are present and on PATH."""

    resolved_dir = _resolve_install_dir(install_dir)
    install_dir = resolved_dir
    install_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Ensuring CLI tools in %s", install_dir)

    for spec in PINNED_TOOLS:
        _ensure_tool(install_dir, spec)

    # prepend install dir to PATH so subprocesses can find binaries
    path_env = os.environ.get("PATH", "")
    if str(install_dir) not in path_env.split(os.pathsep):
        os.environ["PATH"] = f"{install_dir}{os.pathsep}{path_env}"


def _resolve_install_dir(explicit: str | Path | None = None) -> Path:
    """Determine the installation directory, even when settings/env aren't configured."""

    if explicit:
        return Path(explicit).expanduser()

    env_dir = os.environ.get("TOOLS_INSTALL_DIR")
    if env_dir:
        return Path(env_dir).expanduser()

    if _settings is not None:
        try:
            return Path(_settings.tools_install_dir).expanduser()
        except AttributeError:
            pass

    return Path(".tools/bin").expanduser()


def _ensure_tool(install_dir: Path, spec: ToolSpec) -> None:
    binary_path = install_dir / spec.install_name
    url = os.environ.get(spec.url_env, spec.url)
    version = os.environ.get(spec.version_env, spec.version) if spec.version_env else spec.version
    version_marker = install_dir / f".{spec.name}.version"

    if binary_path.exists() and version_marker.exists():
        recorded_version = version_marker.read_text().strip()
        if recorded_version == version:
            logger.info("%s v%s already installed", spec.name, spec.version)
            return

    logger.info("Installing %s v%s", spec.name, version)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_file = Path(tmpdir) / f"{spec.name}.download"
        _download_file(url, tmp_file)

        if spec.archive == "binary":
            shutil.move(tmp_file, binary_path)
        elif spec.archive == "zip":
            with zipfile.ZipFile(tmp_file, "r") as zip_ref:
                zip_ref.extract(spec.binary_name, tmpdir)
            shutil.move(Path(tmpdir) / spec.binary_name, binary_path)
        elif spec.archive == "tar.gz":
            with tarfile.open(tmp_file, "r:gz") as tar_ref:
                tar_ref.extractall(tmpdir)
            extracted = _find_binary(Path(tmpdir), spec.binary_name)
            if extracted is None:
                raise RuntimeError(f"Unable to locate {spec.binary_name} in tarball for {spec.name}")
            shutil.move(extracted, binary_path)
        else:
            raise ValueError(f"Unsupported archive type {spec.archive}")

    binary_path.chmod(binary_path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    version_marker.write_text(version)


def _download_file(url: str, destination: Path) -> None:
    with urlopen(url) as resp, destination.open("wb") as sink:  # nosec - trusted release URLs
        shutil.copyfileobj(resp, sink)


def _find_binary(root: Path, name: str) -> Path | None:
    for path in root.rglob("*"):
        if path.name == name and path.is_file():
            return path
    return None
