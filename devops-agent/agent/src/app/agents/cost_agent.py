"""Cost estimation agent."""
from __future__ import annotations

from app.agents.base import build_logic_agent
from app.agents.schemas import CostResponse
from app.tools import estimate_cost

INSTRUCTIONS = """
Estimate the monthly cost impact of the proposed Terraform plan using the estimate_cost tool.
Highlight delta values and confidence along with any assumptions and include the resulting CostReport
in your response under 'report'.
"""

_TOOLS = [estimate_cost]


def create_agent():
    return build_logic_agent(
        name="CostAgent",
        instructions=INSTRUCTIONS,
        tools=_TOOLS,
        response_format=CostResponse,
    )


agent = create_agent()
