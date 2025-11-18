"""Project-wide constants and supervisor guardrail settings."""
from __future__ import annotations

PLAN_APPROVED_FLAG = "plan_approved"
APPLY_AUTHORIZED_FLAG = "apply_authorized"

PLAN_APPROVAL_COMMANDS = ("/approve plan", "/unlock coding")
PLAN_RESET_COMMANDS = ("/reset plan", "/lock coding")

APPLY_APPROVAL_COMMANDS = ("/approve apply", "/unlock apply", "/run apply")
APPLY_RESET_COMMANDS = ("/hold apply", "/reset apply", "/lock apply")

SUPERVISOR_GUARDRAIL_HELP = (
    "Use /approve plan to allow coding and /approve apply to authorize terraform apply. "
    "Use /reset plan or /hold apply to lock them again."
)
