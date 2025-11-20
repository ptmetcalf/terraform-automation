"""Plan reviewer agent."""
from __future__ import annotations

from app.agents.base import build_logic_agent
from app.agents.schemas import PlanReviewResponse

INSTRUCTIONS = """
Act as the plan reviewer combining results from security, cost, and QA. Determine if the plan is
ready for apply. If not, list required actions referencing affected agents.
"""


def create_agent():
    return build_logic_agent(
        name="PlanReviewerAgent",
        instructions=INSTRUCTIONS,
        response_format=PlanReviewResponse,
    )


agent = create_agent()
