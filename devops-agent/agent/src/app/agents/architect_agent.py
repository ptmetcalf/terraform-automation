"""Architect agent uses MCP sources and documentation."""
from __future__ import annotations

from app.agents.base import build_logic_agent
from app.agents.schemas import DesignResponse
from app.tools import get_ms_learn_mcp_tools, get_terraform_mcp_tools, get_terraform_standards

INSTRUCTIONS = """
You act as the Lead Cloud Architect. Review the DeploymentTicket intent, query the Terraform MCP server
for existing modules/state, and consult Microsoft Learn for best practices. Use the Terraform standards tool
to ensure modules comply with docs/terraform-standards.md. Produce a concise architecture summary, note
required Terraform modules, and highlight risks or unknowns. Return JSON matching DesignResponse.
"""

_ARCHITECT_TOOLS = [get_terraform_standards, *get_terraform_mcp_tools(), *get_ms_learn_mcp_tools()]


def create_agent():
    return build_logic_agent(
        name="ArchitectAgent",
        instructions=INSTRUCTIONS,
        tools=_ARCHITECT_TOOLS,
        response_format=DesignResponse,
    )


agent = create_agent()
