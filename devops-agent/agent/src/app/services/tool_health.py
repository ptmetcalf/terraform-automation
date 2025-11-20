"""Utility helpers to report readiness of optional tools/integrations."""
from __future__ import annotations

import os
import shlex
import shutil
from pathlib import Path

from app.models.tooling import ToolStatus


def _command_available(command: str) -> bool:
    if not command:
        return False
    parts = shlex.split(command)
    if not parts:
        return False
    cmd = parts[0]
    path = Path(cmd)
    if path.is_absolute() and path.exists():
        return True
    return shutil.which(cmd) is not None


def list_tool_statuses() -> list[ToolStatus]:
    statuses: list[ToolStatus] = []

    github_token = os.environ.get("GITHUB_TOKEN")
    github_mcp_command = os.environ.get("GITHUB_MCP_COMMAND", "").strip()
    terraform_mcp_command = os.environ.get("TERRAFORM_MCP_COMMAND", "").strip()
    ms_learn_url = os.environ.get("MSLEARN_MCP_URL", "").strip()

    # GitHub MCP stdio integration
    if github_mcp_command:
        cmd_ok = _command_available(github_mcp_command)
        available = bool(github_token and cmd_ok)
        reason = None
        if not available:
            missing_bits = []
            if not github_token:
                missing_bits.append("GITHUB_TOKEN unset")
            if not cmd_ok:
                missing_bits.append("command not found")
            reason = ", ".join(missing_bits) or "Unknown issue"
        statuses.append(
            ToolStatus(
                name="github_mcp",
                description="GitHub MCP server (stdio)",
                available=available,
                reason=reason,
            )
        )
    else:
        statuses.append(
            ToolStatus(
                name="github_mcp",
                description="GitHub MCP server (stdio)",
                available=False,
                reason="GITHUB_MCP_COMMAND not configured",
            )
        )

    # GitHub REST fallback used for repo discovery
    statuses.append(
        ToolStatus(
            name="github_rest",
            description="GitHub REST API (used for repo discovery fallback)",
            available=bool(github_token),
            reason=None if github_token else "GITHUB_TOKEN not configured",
        )
    )

    # Terraform MCP (stdio)
    if terraform_mcp_command:
        cmd_ok = _command_available(terraform_mcp_command)
        statuses.append(
            ToolStatus(
                name="terraform_mcp",
                description="Terraform MCP server (stdio)",
                available=cmd_ok,
                reason=None if cmd_ok else "Command not found",
            )
        )
    else:
        statuses.append(
            ToolStatus(
                name="terraform_mcp",
                description="Terraform MCP server (stdio)",
                available=False,
                reason="TERRAFORM_MCP_COMMAND not configured",
            )
        )

    # Microsoft Learn MCP (HTTP)
    statuses.append(
        ToolStatus(
            name="ms_learn_mcp",
            description="Microsoft Learn MCP (HTTP)",
            available=bool(ms_learn_url),
            reason=None if ms_learn_url else "MSLEARN_MCP_URL not configured",
        )
    )

    return statuses
