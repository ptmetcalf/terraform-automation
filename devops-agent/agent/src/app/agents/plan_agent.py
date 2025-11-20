"""Terraform plan agent."""
from __future__ import annotations

from app.agents.base import build_logic_agent
from app.agents.schemas import PlanResponse
from app.tools import run_terraform_plan

INSTRUCTIONS = """
You handle terraform init/plan flows. Acquire workspace locks via the lock service
before running the plan tool. Summarize the resulting plan and provide the lock ID.
Always call the run_terraform_plan tool with accurate parameters and include the returned
PlanArtifact in the PlanResponse under plan_artifact.
"""

_TOOLS = [run_terraform_plan]


def create_agent():
    return build_logic_agent(
        name="PlanAgent",
        instructions=INSTRUCTIONS,
        tools=_TOOLS,
        response_format=PlanResponse,
    )


agent = create_agent()
