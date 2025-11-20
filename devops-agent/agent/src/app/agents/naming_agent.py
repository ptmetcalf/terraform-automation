"""Naming policy expert agent."""
from __future__ import annotations

from app.agents.base import build_logic_agent
from app.agents.schemas import NamingResponse
from app.tools import generate_resource_name, get_ms_learn_mcp_tools

INSTRUCTIONS = """
You enforce Azure naming standards. When given resource intents, call the azure naming tool to
produce deterministic names and cross-check Microsoft Learn governance guidance. Output JSON with
resources list entries shaped as {"resource_type": str, "proposed_name": str} and governance_notes.
"""

_TOOLS = [generate_resource_name, *get_ms_learn_mcp_tools()]


def create_agent():
    return build_logic_agent(
        name="NamingAgent",
        instructions=INSTRUCTIONS,
        tools=_TOOLS,
        response_format=NamingResponse,
    )


agent = create_agent()
