"""Drift detection agent."""
from __future__ import annotations

from app.agents.base import build_logic_agent
from app.agents.schemas import DriftResponse
from app.tools import drift_monitor_tool

INSTRUCTIONS = """
Run drift checks after apply and on demand. Use the drift_monitor tool to compare desired vs actual state
without mutating infrastructure and summarize findings. Provide counts, remediation hints, and include
the DriftReport under 'report'.
"""

_TOOLS = [drift_monitor_tool]


def create_agent():
    return build_logic_agent(
        name="DriftAgent",
        instructions=INSTRUCTIONS,
        tools=_TOOLS,
        response_format=DriftResponse,
    )


agent = create_agent()
