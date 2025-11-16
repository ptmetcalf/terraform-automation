"""Terraform deployment workflow graph definition."""
from __future__ import annotations

from agent_framework import (
    AgentExecutorRequest,
    AgentExecutorResponse,
    ChatMessage,
    Role,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)

from app.agents import (
    apply_agent,
    architect_agent,
    coding_agent,
    cost_agent,
    documentation_agent,
    drift_agent,
    gitops_agent,
    naming_agent,
    orchestrator_agent,
    plan_agent,
    plan_reviewer_agent,
    qa_agent,
    security_agent,
)
from app.agents.schemas import OrchestratorDirective


@executor(id="route_from_orchestrator")
async def route_from_orchestrator(
    response: AgentExecutorResponse, ctx: WorkflowContext[OrchestratorDirective]
) -> None:
    directive = OrchestratorDirective.model_validate_json(response.agent_run_response.text)
    await ctx.send_message(directive)


PHASE_ORDER = [
    "design",
    "coding",
    "plan",
    "review",
    "approval",
    "apply",
    "post_apply",
    "documentation",
]


def _select_phase(directive: OrchestratorDirective, target_ids: list[str]) -> list[str]:
    try:
        idx = PHASE_ORDER.index(directive.next_phase)
        return [target_ids[idx]]
    except (ValueError, IndexError):
        return []


def _phase_prompt(phase: str, directive: OrchestratorDirective) -> AgentExecutorRequest:
    message = ChatMessage(
        role=Role.USER,
        text=f"{phase} phase requested. Consider prior notes: {directive.summary}",
    )
    return AgentExecutorRequest(messages=[message], should_respond=True)


@executor(id="design_phase_entry")
async def design_phase_entry(directive: OrchestratorDirective, ctx: WorkflowContext[AgentExecutorRequest]) -> None:
    await ctx.send_message(_phase_prompt("Design", directive))


@executor(id="coding_phase_entry")
async def coding_phase_entry(directive: OrchestratorDirective, ctx: WorkflowContext[AgentExecutorRequest]) -> None:
    await ctx.send_message(_phase_prompt("Coding", directive))


@executor(id="plan_phase_entry")
async def plan_phase_entry(directive: OrchestratorDirective, ctx: WorkflowContext[AgentExecutorRequest]) -> None:
    await ctx.send_message(_phase_prompt("Plan", directive))


@executor(id="review_phase_entry")
async def review_phase_entry(directive: OrchestratorDirective, ctx: WorkflowContext[AgentExecutorRequest]) -> None:
    await ctx.send_message(_phase_prompt("Review", directive))


@executor(id="approval_phase_entry")
async def approval_phase_entry(directive: OrchestratorDirective, ctx: WorkflowContext[AgentExecutorRequest]) -> None:
    await ctx.send_message(_phase_prompt("Approval", directive))


@executor(id="apply_phase_entry")
async def apply_phase_entry(directive: OrchestratorDirective, ctx: WorkflowContext[AgentExecutorRequest]) -> None:
    await ctx.send_message(_phase_prompt("Apply", directive))


@executor(id="post_apply_phase_entry")
async def post_apply_phase_entry(
    directive: OrchestratorDirective, ctx: WorkflowContext[AgentExecutorRequest]
) -> None:
    await ctx.send_message(_phase_prompt("Post-Apply", directive))


@executor(id="documentation_phase_entry")
async def documentation_phase_entry(
    directive: OrchestratorDirective, ctx: WorkflowContext[AgentExecutorRequest]
) -> None:
    await ctx.send_message(_phase_prompt("Documentation", directive))


workflow = (
    WorkflowBuilder(name="TerraformDeploymentWorkflow", description="Multi-agent Terraform orchestration")
    .set_start_executor(orchestrator_agent)
    .add_edge(orchestrator_agent, route_from_orchestrator)
    .add_multi_selection_edge_group(
        route_from_orchestrator,
        [
            design_phase_entry,
            coding_phase_entry,
            plan_phase_entry,
            review_phase_entry,
            approval_phase_entry,
            apply_phase_entry,
            post_apply_phase_entry,
            documentation_phase_entry,
        ],
        selection_func=_select_phase,
    )
    # Design chain
    .add_edge(design_phase_entry, architect_agent)
    .add_edge(architect_agent, naming_agent)
    .add_edge(naming_agent, qa_agent)
    .add_edge(qa_agent, orchestrator_agent)
    # Coding chain
    .add_edge(coding_phase_entry, coding_agent)
    .add_edge(coding_agent, gitops_agent)
    .add_edge(gitops_agent, orchestrator_agent)
    # Plan chain
    .add_edge(plan_phase_entry, plan_agent)
    .add_edge(plan_agent, orchestrator_agent)
    # Review chain
    .add_edge(review_phase_entry, security_agent)
    .add_edge(security_agent, cost_agent)
    .add_edge(cost_agent, plan_reviewer_agent)
    .add_edge(plan_reviewer_agent, qa_agent)
    # Approval chain (apply agent handles approvals)
    .add_edge(approval_phase_entry, apply_agent)
    .add_edge(apply_agent, orchestrator_agent)
    # Apply chain (executes terraform apply explicitly)
    .add_edge(apply_phase_entry, apply_agent)
    .add_edge(apply_agent, orchestrator_agent)
    # Post apply -> drift -> docs -> orchestrator
    .add_edge(post_apply_phase_entry, drift_agent)
    .add_edge(drift_agent, documentation_agent)
    .add_edge(documentation_agent, orchestrator_agent)
    # Documentation ad-hoc entry
    .add_edge(documentation_phase_entry, documentation_agent)
    .add_edge(documentation_agent, orchestrator_agent)
    .build()
)
