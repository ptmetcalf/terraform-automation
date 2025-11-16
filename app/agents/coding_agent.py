"""Coding agent that prepares Terraform diffs."""
from __future__ import annotations

from app.agents.base import build_coding_agent
from app.agents.schemas import CodingResponse
from app.tools import get_terraform_standards

INSTRUCTIONS = """
You are the implementation engineer. Translate design decisions into Terraform and documentation
changes. Call the Terraform standards tool before authoring code and enforce module reuse per docs/terraform-standards.md.
Only describe intended edits and produce a GitOpsChangeRequest payload referencing specific files.
Never run terraform or git directly; the GitOps agent handles file mutations.
"""


def create_agent():
    return build_coding_agent(
        name="CodingAgent",
        instructions=INSTRUCTIONS,
        tools=[get_terraform_standards],
        response_format=CodingResponse,
    )


agent = create_agent()
