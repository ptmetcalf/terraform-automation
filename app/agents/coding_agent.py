"""Coding agent that prepares Terraform diffs."""
from __future__ import annotations

from app.agents.base import build_coding_agent
from app.agents.schemas import CodingResponse

INSTRUCTIONS = """
You are the implementation engineer. Translate design decisions into Terraform and documentation
changes. Only describe intended edits and produce a GitOpsChangeRequest payload referencing specific files.
Never run terraform or git directly; the GitOps agent handles file mutations.
"""


def create_agent():
    return build_coding_agent(
        name="CodingAgent",
        instructions=INSTRUCTIONS,
        response_format=CodingResponse,
    )


agent = create_agent()
