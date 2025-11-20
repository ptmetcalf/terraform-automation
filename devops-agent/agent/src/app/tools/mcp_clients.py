"""Helpers to connect to Terraform and Microsoft Learn MCP servers."""
from __future__ import annotations

import logging
import os
from functools import lru_cache
from shlex import split

from agent_framework import MCPStdioTool, MCPStreamableHTTPTool

logger = logging.getLogger(__name__)

DEFAULT_TERRAFORM_MCP_COMMAND = "npx"
DEFAULT_TERRAFORM_MCP_ARGS = "-y terraform-mcp-server".split()
DEFAULT_MSLEARN_MCP_URL = "https://learn.microsoft.com/api/agentframework/mslearn-mcp"
DEFAULT_GITHUB_MCP_COMMAND = ""
DEFAULT_GITHUB_MCP_ARGS = []

@lru_cache()
def get_terraform_mcp_tools() -> list[MCPStdioTool]:
    command = os.environ.get("TERRAFORM_MCP_COMMAND", DEFAULT_TERRAFORM_MCP_COMMAND)
    args_raw = os.environ.get("TERRAFORM_MCP_ARGS")
    args = split(args_raw) if args_raw else DEFAULT_TERRAFORM_MCP_ARGS
    tool = MCPStdioTool(
        name="terraform-mcp",
        command=command,
        args=args,
        description="Access Terraform MCP server for state queries",
    )
    return [tool]


@lru_cache()
def get_ms_learn_mcp_tools() -> list[MCPStreamableHTTPTool]:
    url = os.environ.get("MSLEARN_MCP_URL", DEFAULT_MSLEARN_MCP_URL)
    api_key = os.environ.get("MSLEARN_MCP_KEY")
    if not url:
        logger.warning("MSLEARN_MCP_URL not set; Microsoft Learn MCP disabled")
        return []
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else None
    tool = MCPStreamableHTTPTool(
        name="ms-learn",
        url=url,
        headers=headers or {},
        description="Query Microsoft Learn content",
    )
    return [tool]


@lru_cache()
def get_github_mcp_tools() -> list[MCPStdioTool]:
    command = os.environ.get("GITHUB_MCP_COMMAND", DEFAULT_GITHUB_MCP_COMMAND).strip()
    if not command:
        logger.info("GITHUB_MCP_COMMAND not set; GitHub MCP integration disabled")
        return []
    args_raw = os.environ.get("GITHUB_MCP_ARGS")
    args = split(args_raw) if args_raw else DEFAULT_GITHUB_MCP_ARGS
    env = os.environ.copy()
    token = env.get("GITHUB_TOKEN")
    if token:
        env["GITHUB_TOKEN"] = token
    else:
        logger.warning("GITHUB_TOKEN not set; GitHub MCP access may fail")
    tool = MCPStdioTool(
        name="github-mcp",
        command=command,
        args=args,
        description="Interact with GitHub repositories (list, clone, open PRs)",
        env=env,
    )
    return [tool]
