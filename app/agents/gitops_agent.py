"""GitOps specialist agent."""
from __future__ import annotations

from app.agents.base import build_logic_agent
from app.agents.schemas import GitOpsResponse
from app.tools import apply_git_changes, get_repo_status

INSTRUCTIONS = """
You are the only agent allowed to mutate Git repositories. Ensure branch naming follows
<ticket-id>/<purpose> and enforce path restrictions before applying edits. Always call get_repo_status
before and after invoking apply_git_changes to maintain auditability. Return GitOpsResponse JSON.
"""

_TOOLS = [get_repo_status, apply_git_changes]


def create_agent():
    return build_logic_agent(
        name="GitOpsAgent",
        instructions=INSTRUCTIONS,
        tools=_TOOLS,
        response_format=GitOpsResponse,
    )


agent = create_agent()
