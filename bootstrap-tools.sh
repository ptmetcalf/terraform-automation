#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Prefer repo-local virtualenv python if available, otherwise fall back to system python3/python.
if [[ -n "${PYTHON_BIN:-}" ]]; then
  PYTHON_CMD="${PYTHON_BIN}"
elif [[ -x "${ROOT_DIR}/.venv/bin/python" ]]; then
  PYTHON_CMD="${ROOT_DIR}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="$(command -v python)"
else
  echo "No python interpreter found. Install python3 or specify PYTHON_BIN." >&2
  exit 1
fi

export TOOLS_INSTALL_DIR="${TOOLS_INSTALL_DIR:-${ROOT_DIR}/.tools/bin}"
export PYTHONPATH="${ROOT_DIR}/devops-agent/agent/src:${PYTHONPATH:-}"

cd "${ROOT_DIR}/devops-agent/agent"

"${PYTHON_CMD}" - <<'PY'
from app.services.tool_installer import ensure_tool_binaries

ensure_tool_binaries()
PY

echo "CLI tool bootstrap complete. Installed binaries live in ${TOOLS_INSTALL_DIR}"
