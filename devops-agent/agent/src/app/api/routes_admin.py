"""Admin endpoints for inspecting tickets and artifacts."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models import DeploymentTicket
from app.services.artifact_store import artifact_store
from app.services.ticket_store import ticket_store

router = APIRouter(prefix="/tickets", tags=["tickets"])


class TicketDetail(BaseModel):
    ticket: DeploymentTicket
    artifacts: Dict[str, list[dict[str, Any]]]


@router.get("/{ticket_id}", response_model=TicketDetail)
async def get_ticket(ticket_id: str) -> TicketDetail:
    ticket = await ticket_store.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    artifacts = {
        "plan": await artifact_store.list_artifacts(ticket_id, artifact_type="plan"),
        "security": await artifact_store.list_artifacts(ticket_id, artifact_type="security"),
        "cost": await artifact_store.list_artifacts(ticket_id, artifact_type="cost"),
        "drift": await artifact_store.list_artifacts(ticket_id, artifact_type="drift"),
    }
    return TicketDetail(ticket=ticket, artifacts=artifacts)


@router.get("/", response_model=list[DeploymentTicket])
async def list_tickets() -> list[DeploymentTicket]:
    return await ticket_store.list_tickets()
