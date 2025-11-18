"""AI Engineer supervisor agent that orchestrates capability execution."""
from __future__ import annotations

from textwrap import dedent

from app.agents.base import build_logic_agent
from app.capabilities import get_capabilities
from app.constants import APPLY_AUTHORIZED_FLAG, PLAN_APPROVED_FLAG
from app.tools.capability_router_tool import run_devops_capability


def _capability_table() -> str:
    rows = []
    for capability in get_capabilities():
        rows.append(
            f"- **{capability.title}** (`{capability.slug}`): {capability.description} "
            f"(approval cmds: {', '.join(capability.approval_commands) or 'none'})"
        )
    return "\n".join(rows)


INSTRUCTIONS = dedent(
    f"""
    You are the AI Engineer supervisor agent. Hold a natural language conversation with the operator,
    understand their goals, and coordinate the specialist capabilities below. Always:

    {_capability_table()}

    Guardrails:
    - Never trigger coding/DevOps activities until the human unlocks `{PLAN_APPROVED_FLAG}` via `/approve plan`.
    - Never allow apply/deployment operations until `{APPLY_AUTHORIZED_FLAG}` is set via `/approve apply`.
    - Collect missing context (repo URL, workspace, environment, etc.) before invoking a capability tool.
    - After running a capability, summarize the outcome, outstanding approvals, and next recommended steps.
    - If a capability cannot run (missing data/permissions), explain what the human must provide.
    - Maintain a helpful conversational tone and always respond with plain language plus bullet lists when appropriate.
    """
).strip()


_TOOLS = [run_devops_capability]


def create_agent():
    return build_logic_agent(name="SupervisorAgent", instructions=INSTRUCTIONS, tools=_TOOLS)


agent = create_agent()
