"""Quality assurance agent."""
from __future__ import annotations

from app.agents.base import build_logic_agent
from app.agents.schemas import QAResponse

INSTRUCTIONS = """
You are the QA and release manager. Validate that requirements, constraints, and compliance
signals have been satisfied. Flag missing information before plan/apply phases. Output QAResponse JSON.
"""


def create_agent():
    return build_logic_agent(
        name="QAAgent",
        instructions=INSTRUCTIONS,
        response_format=QAResponse,
    )


agent = create_agent()
