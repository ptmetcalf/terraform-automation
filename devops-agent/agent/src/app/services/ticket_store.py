"""Ticket store backed by SQLite/SQLAlchemy."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select

from app.models import DeploymentTicket
from app.services.database import database, tickets_table


class TicketStore:
    """Provide CRUD operations for deployment tickets."""

    async def get_ticket(self, ticket_id: str) -> Optional[DeploymentTicket]:
        query = select(tickets_table.c.payload).where(tickets_table.c.ticket_id == ticket_id)
        record = await database.fetch_one(query)
        if not record:
            return None
        payload = record["payload"]
        if isinstance(payload, str):
            import json

            payload = json.loads(payload)
        return DeploymentTicket.model_validate(payload)

    async def list_tickets(self, *, thread_id: Optional[str] = None) -> List[DeploymentTicket]:
        query = select(tickets_table.c.payload)
        if thread_id:
            query = query.where(tickets_table.c.thread_id == thread_id)
        records = await database.fetch_all(query)
        tickets: list[DeploymentTicket] = []
        for row in records:
            payload = row["payload"]
            if isinstance(payload, str):
                import json

                payload = json.loads(payload)
            tickets.append(DeploymentTicket.model_validate(payload))
        return tickets

    async def upsert_ticket(self, ticket: DeploymentTicket) -> DeploymentTicket:
        existing = await self.get_ticket(ticket.ticket_id)
        if existing:
            ticket.created_at = existing.created_at
        payload = ticket.model_dump(mode="json")
        if existing:
            query = (
                tickets_table.update()
                .where(tickets_table.c.ticket_id == ticket.ticket_id)
                .values(
                    thread_id=ticket.thread_id,
                    status=ticket.status,
                    payload=payload,
                    created_at=ticket.created_at,
                    updated_at=ticket.updated_at,
                )
            )
        else:
            query = tickets_table.insert().values(
                ticket_id=ticket.ticket_id,
                thread_id=ticket.thread_id,
                status=ticket.status,
                payload=payload,
                created_at=ticket.created_at,
                updated_at=ticket.updated_at,
            )
        await database.execute(query)
        return ticket

    async def delete_ticket(self, ticket_id: str) -> None:
        query = tickets_table.delete().where(tickets_table.c.ticket_id == ticket_id)
        await database.execute(query)


ticket_store = TicketStore()
