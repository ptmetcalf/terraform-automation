"""Orchestrator agent responsible for routing work across specialists."""
from __future__ import annotations

from app.agents.base import build_logic_agent
from app.agents.schemas import OrchestratorDirective

INSTRUCTIONS = """
You are the Terraform Deployment Orchestrator. Maintain overall state for the deployment thread,
update the DeploymentTicket status, and determine which specialist agent should act next. Always:
- Summarize the latest state of the ticket.
- List blockers or missing information before routing.
- Output JSON matching OrchestratorDirective with the next_phase that should run.
"""


def create_agent():
    return build_logic_agent(
        name="OrchestratorAgent",
        instructions=INSTRUCTIONS,
        response_format=OrchestratorDirective,
    )


def get_agent():
    return create_agent()


agent = create_agent()
