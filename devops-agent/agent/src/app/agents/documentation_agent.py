"""Documentation agent."""
from __future__ import annotations

from app.agents.base import build_logic_agent
from app.agents.schemas import DocumentationResponse

INSTRUCTIONS = """
Produce customer-facing release notes, plan/apply summaries, and link to GitOps pull requests.
Always emit Markdown under artifacts_markdown with headings for Architecture, Changes, Validation, and Next Steps.
"""


def create_agent():
    return build_logic_agent(
        name="DocumentationAgent",
        instructions=INSTRUCTIONS,
        response_format=DocumentationResponse,
    )


agent = create_agent()
