"""Shared chat workflow execution service."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.constants import (
    APPLY_APPROVAL_COMMANDS,
    APPLY_AUTHORIZED_FLAG,
    APPLY_RESET_COMMANDS,
    PLAN_APPROVAL_COMMANDS,
    PLAN_APPROVED_FLAG,
    PLAN_RESET_COMMANDS,
    SRE_ACTION_FLAG,
    SRE_APPROVAL_COMMANDS,
    SRE_RESET_COMMANDS,
    SUPERVISOR_GUARDRAIL_HELP,
)
from app.models import Constraints, DeploymentTicket, GitReference
from app.models.chat import ChatRequest, ChatResponse
from app.services import project_store
from app.services.ticket_store import ticket_store
from app.workflows.terraform_workflow import workflow


def _normalize(text: str) -> str:
    return text.lower()


def _matches_command(text: str, commands: tuple[str, ...]) -> bool:
    lowered = _normalize(text)
    return any(cmd in lowered for cmd in commands)


def apply_supervisor_flags(ticket: DeploymentTicket, message: str) -> bool:
    """Adjust ticket flags based on explicit slash commands from the operator."""

    updated = False
    if not message:
        return False

    if _matches_command(message, PLAN_APPROVAL_COMMANDS) and not ticket.flags.get(PLAN_APPROVED_FLAG):
        ticket.flags[PLAN_APPROVED_FLAG] = True
        updated = True
    if _matches_command(message, PLAN_RESET_COMMANDS) and ticket.flags.get(PLAN_APPROVED_FLAG):
        ticket.flags[PLAN_APPROVED_FLAG] = False
        updated = True

    if _matches_command(message, APPLY_APPROVAL_COMMANDS) and not ticket.flags.get(APPLY_AUTHORIZED_FLAG):
        ticket.flags[APPLY_AUTHORIZED_FLAG] = True
        updated = True
    if _matches_command(message, APPLY_RESET_COMMANDS) and ticket.flags.get(APPLY_AUTHORIZED_FLAG):
        ticket.flags[APPLY_AUTHORIZED_FLAG] = False
        updated = True

    if _matches_command(message, SRE_APPROVAL_COMMANDS) and not ticket.flags.get(SRE_ACTION_FLAG):
        ticket.flags[SRE_ACTION_FLAG] = True
        updated = True
    if _matches_command(message, SRE_RESET_COMMANDS) and ticket.flags.get(SRE_ACTION_FLAG):
        ticket.flags[SRE_ACTION_FLAG] = False
        updated = True

    return updated


def guardrail_summary(ticket: DeploymentTicket) -> str:
    plan_unlocked = ticket.flags.get(PLAN_APPROVED_FLAG, False)
    apply_unlocked = ticket.flags.get(APPLY_AUTHORIZED_FLAG, False)
    sre_unlocked = ticket.flags.get(SRE_ACTION_FLAG, False)
    return (
        "[Supervisor Guardrails]\n"
        f"- coding unlocked ({PLAN_APPROVED_FLAG}): {'true' if plan_unlocked else 'false'}\n"
        f"- apply authorized ({APPLY_AUTHORIZED_FLAG}): {'true' if apply_unlocked else 'false'}\n"
        f"- sre remediation allowed ({SRE_ACTION_FLAG}): {'true' if sre_unlocked else 'false'}\n"
        f"- Commands: {SUPERVISOR_GUARDRAIL_HELP}"
    )


class ChatService:
    """Coordinate ticket creation and workflow execution."""

    def __init__(self) -> None:
        self._workflow_lock = asyncio.Lock()

    async def _apply_project_context(self, payload: ChatRequest) -> tuple[ChatRequest, str]:
        project_lines: list[str] = []
        if payload.project_id:
            project = await project_store.get_project(payload.project_id)
            if project is None:
                raise ValueError(f"Project '{payload.project_id}' not found")
            if payload.environment is None:
                payload.environment = project.default_environment
            if payload.repo_url is None:
                payload.repo_url = project.repo_url
            if payload.workspace_dir is None:
                payload.workspace_dir = project.workspace_dir
            if payload.terraform_workspace is None:
                payload.terraform_workspace = project.default_environment
            if payload.branch is None:
                payload.branch = project.default_branch
            project_lines.extend(
                [
                    f"- project_id: {project.project_id}",
                    f"- name: {project.name}",
                    f"- repo_url: {project.repo_url}",
                    f"- workspace_dir: {project.workspace_dir}",
                    f"- default_environment: {project.default_environment}",
                    f"- default_branch: {project.default_branch}",
                ]
            )

        if payload.environment is None:
            payload.environment = "dev"
        if payload.branch is None:
            payload.branch = "main"

        if payload.repo_url is None or payload.terraform_workspace is None:
            raise ValueError("Terraform workspace and repo URL are required (provide project_id or explicit values)")

        project_lines.extend(
            [
                f"- repo_url: {payload.repo_url}",
                f"- terraform_workspace: {payload.terraform_workspace}",
                f"- branch: {payload.branch}",
                f"- environment: {payload.environment}",
            ]
        )
        if payload.workspace_dir:
            project_lines.append(f"- workspace_dir: {payload.workspace_dir}")

        context = "[Project Context]\n" + "\n".join(project_lines)
        return payload, context

    async def _ensure_ticket(self, payload: ChatRequest) -> DeploymentTicket:
        existing_ticket: DeploymentTicket | None = None
        if payload.thread_id:
            tickets = await ticket_store.list_tickets(thread_id=payload.thread_id)
            existing_ticket = tickets[0] if tickets else None
        if existing_ticket:
            return existing_ticket

        if payload.terraform_workspace is None or payload.repo_url is None or payload.branch is None:
            raise ValueError("Terraform workspace, repo URL, and branch are required")
        if payload.environment is None:
            payload.environment = "dev"

        now = datetime.now(timezone.utc)
        ticket = DeploymentTicket(
            ticket_id=str(uuid4()),
            thread_id=payload.thread_id or str(uuid4()),
            status="draft",
            requested_by=payload.requested_by,
            environment=payload.environment,
            target_cloud="azure",
            terraform_workspace=payload.terraform_workspace,
            git=GitReference(repo_url=payload.repo_url, branch=payload.branch),
            intent_summary=payload.intent_summary or payload.message,
            constraints=Constraints(),
            current_stage="draft",
            flags={},
            created_at=now,
            updated_at=now,
        )
        await ticket_store.upsert_ticket(ticket)
        return ticket

    async def run_chat(self, payload: ChatRequest) -> ChatResponse:
        payload, project_context = await self._apply_project_context(payload)
        ticket = await self._ensure_ticket(payload)
        apply_supervisor_flags(ticket, payload.message)
        guardrails = guardrail_summary(ticket)
        augmented_message = (
            f"Ticket {ticket.ticket_id} ({ticket.environment}) request from {ticket.requested_by}:\n"
            f"{guardrails}\n"
            f"{project_context}\n"
            f"Operator message:\n{payload.message}"
        )

        async with self._workflow_lock:
            result = await workflow.run(message=augmented_message)

        raw_outputs = result.get_outputs()
        outputs: list[Any] = []
        for item in raw_outputs:
            if hasattr(item, "model_dump"):
                outputs.append(item.model_dump())  # type: ignore[call-arg]
            else:
                outputs.append(item)
        ticket.updated_at = datetime.now(timezone.utc)
        await ticket_store.upsert_ticket(ticket)

        try:
            final_state = result.get_final_state()
            status = getattr(final_state, "value", str(final_state))
        except RuntimeError:
            status = "unknown"
        return ChatResponse(
            ticket_id=ticket.ticket_id,
            thread_id=ticket.thread_id,
            status=status,
            workflow_outputs=outputs,
        )


chat_service = ChatService()
