"""Apply agent with human-in-the-loop approvals."""
from __future__ import annotations

from app.agents.base import build_logic_agent
from app.agents.schemas import ApplyResponse
from app.tools import run_terraform_apply

INSTRUCTIONS = """
You manage the apply phase and coordinate human approvals. When approvals are pending,
emit ApplyResponse with decision='pending_approval' and include approval_request_id referencing
records in the approval service. After approval, call run_terraform_apply to execute the change
and report success/failure details.
"""

_TOOLS = [run_terraform_apply]


def create_agent():
    return build_logic_agent(
        name="ApplyAgent",
        instructions=INSTRUCTIONS,
        tools=_TOOLS,
        response_format=ApplyResponse,
    )


agent = create_agent()
