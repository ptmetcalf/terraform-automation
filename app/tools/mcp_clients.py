"""Helpers to connect to Terraform and Microsoft Learn MCP servers."""
from __future__ import annotations

import logging
import os
from functools import lru_cache
from agent_framework import MCPStdioTool, MCPStreamableHTTPTool

logger = logging.getLogger(__name__)


@lru_cache()
def get_terraform_mcp_tools() -> list[MCPStdioTool]:
    command = os.environ.get("TERRAFORM_MCP_COMMAND")
    if not command:
        logger.warning("TERRAFORM_MCP_COMMAND not set; Terraform MCP tools disabled")
        return []
    args = os.environ.get("TERRAFORM_MCP_ARGS", "").split()
    tool = MCPStdioTool(
        name="terraform-mcp",
        command=command,
        args=args,
        description="Access Terraform MCP server for state queries",
    )
    return [tool]


@lru_cache()
def get_ms_learn_mcp_tools() -> list[MCPStreamableHTTPTool]:
    url = os.environ.get("MSLEARN_MCP_URL")
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
