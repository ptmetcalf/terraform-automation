"""Project-wide constants and supervisor guardrail settings."""
from __future__ import annotations

PLAN_APPROVED_FLAG = "plan_approved"
APPLY_AUTHORIZED_FLAG = "apply_authorized"
SRE_ACTION_FLAG = "sre_authorized"

PLAN_APPROVAL_COMMANDS = ("/approve plan", "/unlock coding")
PLAN_RESET_COMMANDS = ("/reset plan", "/lock coding")

APPLY_APPROVAL_COMMANDS = ("/approve apply", "/unlock apply", "/run apply")
APPLY_RESET_COMMANDS = ("/hold apply", "/reset apply", "/lock apply")

SRE_APPROVAL_COMMANDS = ("/approve sre-action", "/unlock sre")
SRE_RESET_COMMANDS = ("/reset sre-action", "/lock sre", "/hold sre-action")

SUPERVISOR_GUARDRAIL_HELP = (
    "Use /approve plan to allow coding, /approve apply to authorize terraform apply, "
    "and /approve sre-action to allow remediation tasks. Use the /reset or /hold variants to lock them again."
)
