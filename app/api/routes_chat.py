"""Chat API for orchestrating workflow runs."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from app.models import Constraints, DeploymentTicket, GitReference
from app.services.ticket_store import ticket_store
from app.workflows.terraform_workflow import workflow

router = APIRouter(prefix="/api", tags=["chat"])

_workflow_lock = asyncio.Lock()


class ChatRequest(BaseModel):
    message: str
    requested_by: str
    environment: str = "dev"
    thread_id: Optional[str] = None
    terraform_workspace: str
    repo_url: HttpUrl
    branch: str = "main"
    intent_summary: str | None = None


class ChatResponse(BaseModel):
    ticket_id: str
    thread_id: str
    status: str
    workflow_outputs: list[Any]


async def _ensure_ticket(payload: ChatRequest) -> DeploymentTicket:
    existing_ticket: DeploymentTicket | None = None
    if payload.thread_id:
        tickets = await ticket_store.list_tickets(thread_id=payload.thread_id)
        existing_ticket = tickets[0] if tickets else None
    if existing_ticket:
        return existing_ticket

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


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    ticket = await _ensure_ticket(payload)
    augmented_message = (
        f"Ticket {ticket.ticket_id} ({ticket.environment}) request from {ticket.requested_by}:\n"
        f"{payload.message}"
    )

    async with _workflow_lock:
        try:
            result = await workflow.run(message=augmented_message)
        except Exception as exc:  # pragma: no cover - workflow runtime errors bubble up
            raise HTTPException(status_code=500, detail=f"Workflow execution failed: {exc}") from exc

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
