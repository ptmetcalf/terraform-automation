"""Lock models used by plan/apply phases."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class WorkspaceLock(BaseModel):
    lock_id: str
    workspace: str
    ticket_id: str
    status: Literal["locked_for_plan", "locked_for_apply"]
    locked_at: datetime
