"""Drift detection agent."""
from __future__ import annotations

from app.agents.base import build_logic_agent
from app.agents.schemas import DriftResponse
from app.tools import run_drift_check

INSTRUCTIONS = """
Run drift checks after apply and on demand. Use run_drift_check to compare desired vs actual state
and summarize findings. Provide counts and remediation hints and include the DriftReport under 'report'.
"""

_TOOLS = [run_drift_check]


def create_agent():
    return build_logic_agent(
        name="DriftAgent",
        instructions=INSTRUCTIONS,
        tools=_TOOLS,
        response_format=DriftResponse,
    )


agent = create_agent()
