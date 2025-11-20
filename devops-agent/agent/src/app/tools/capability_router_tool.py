"""Tools for invoking capabilities from the supervisor agent."""
from __future__ import annotations

from typing import Any

from agent_framework import AIFunction
from pydantic import BaseModel, Field, HttpUrl

from app.models.chat import ChatRequest

class DevOpsCapabilityInput(BaseModel):
    """Inputs required to run the DevOps/Terraform capability."""

    requested_by: str = Field(description="Human requesting the change")
    message: str = Field(description="High-level intent or request details")
    terraform_workspace: str = Field(description="Terraform workspace or directory to target")
    repo_url: HttpUrl = Field(description="Git repository containing the Terraform code")
    branch: str = Field(default="main", description="Git branch to base changes from")
    environment: str = Field(default="dev", description="Deployment environment (dev/stage/prod)")
    thread_id: str | None = Field(default=None, description="Existing ticket/thread id if resuming")


class DevOpsCapabilityResult(BaseModel):
    ticket_id: str
    thread_id: str
    status: str
    workflow_outputs: list[Any]
    summary: str


async def run_devops_capability(inputs: DevOpsCapabilityInput) -> DevOpsCapabilityResult:
    """Invoke the existing Terraform workflow via the chat service."""

    from app.services.chat_executor import chat_service

    payload = ChatRequest(
        message=inputs.message,
        requested_by=inputs.requested_by,
        environment=inputs.environment,
        thread_id=inputs.thread_id,
        terraform_workspace=inputs.terraform_workspace,
        repo_url=inputs.repo_url,
        branch=inputs.branch,
    )
    response = await chat_service.run_chat(payload)
    summary = f"Ticket {response.ticket_id} handled capability 'devops' with status {response.status}."
    return DevOpsCapabilityResult(
        ticket_id=response.ticket_id,
        thread_id=response.thread_id,
        status=response.status,
        workflow_outputs=response.workflow_outputs,
        summary=summary,
    )

# Create a FunctionTool instance so AG-UI/Agent Framework can serialize schemas.
devops_capability_tool = AIFunction(
    name="run_devops_capability",
    description="Invoke the DevOps/Terraform workflow with the provided repo/workspace metadata.",
    func=run_devops_capability,
    input_model=DevOpsCapabilityInput,
    output_model=DevOpsCapabilityResult,
    approval_mode="always_require",
    max_invocations=1,
)
