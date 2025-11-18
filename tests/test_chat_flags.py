from datetime import datetime, timezone

from app.services.chat_executor import apply_supervisor_flags
from app.models import Constraints, DeploymentTicket, GitReference


def _ticket() -> DeploymentTicket:
    now = datetime.now(timezone.utc)
    return DeploymentTicket(
        ticket_id="t-1",
        thread_id="thread",
        status="draft",
        requested_by="tester",
        environment="dev",
        target_cloud="azure",
        terraform_workspace="ws",
        git=GitReference(repo_url="https://example.com/repo.git", branch="main"),
        intent_summary="summary",
        constraints=Constraints(),
        current_stage="draft",
        flags={},
        created_at=now,
        updated_at=now,
    )


def test_apply_supervisor_flags_unlocks_coding():
    ticket = _ticket()
    changed = apply_supervisor_flags(ticket, "/approve plan")
    assert changed is True
    assert ticket.flags.get("plan_approved") is True


def test_apply_supervisor_flags_relocks_coding():
    ticket = _ticket()
    ticket.flags["plan_approved"] = True
    changed = apply_supervisor_flags(ticket, "/reset plan")
    assert changed is True
    assert ticket.flags.get("plan_approved") is False


def test_apply_supervisor_flags_unlocks_apply():
    ticket = _ticket()
    changed = apply_supervisor_flags(ticket, "/approve apply")
    assert changed is True
    assert ticket.flags.get("apply_authorized") is True


def test_apply_supervisor_flags_hold_apply():
    ticket = _ticket()
    ticket.flags["apply_authorized"] = True
    changed = apply_supervisor_flags(ticket, "/hold apply")
    assert changed is True
    assert ticket.flags.get("apply_authorized") is False
