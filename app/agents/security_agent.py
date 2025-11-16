"""Security review agent."""
from __future__ import annotations

from app.agents.base import build_logic_agent
from app.agents.schemas import SecurityResponse
from app.tools import run_security_scan

INSTRUCTIONS = """
You coordinate IaC security scans via Checkov/tfsec. Always call run_security_scan with
accurate directory metadata, summarize blocking findings, and map them back to Terraform resources.
"""

_TOOLS = [run_security_scan]


def create_agent():
    return build_logic_agent(
        name="SecurityAgent",
        instructions=INSTRUCTIONS,
        tools=_TOOLS,
        response_format=SecurityResponse,
    )


agent = create_agent()
