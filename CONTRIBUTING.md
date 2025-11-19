# Contribution Guide

This repository powers a multi-capability “agent coworker” platform. When you add or update agents/tools, follow the guidelines below to keep behaviour predictable and safe.

## Sub-agent Specification

1. **Typed responses only**  
   - Every agent or tool must emit Pydantic models for both inputs and outputs. This keeps the supervisor, REST APIs, and AG‑UI clients in sync.

2. **Human-in-the-loop for writes**  
   - Any capability that mutates infrastructure, code, or runtime state must set `approval_required=True` in the capability registry and list the slash commands (e.g., `/approve plan`, `/approve sre-action`) that satisfy it.
   - Read-only diagnostics (drift, health, cost reports) should default to `approval_required=False`.

3. **Keep scope tight**  
   - Each capability should own a focused task (e.g., “Terraform drift monitor” or “Cost delta reporter”). Break large flows into multiple agents so reasoning stays short and reusable.

4. **Prefer existing tools/APIs**  
   - Reuse the shared tool wrappers (`app/tools/`) or MCP servers (Terraform, GitHub, etc.) whenever possible. New credentials belong in `.env`/environment variables, never hard-coded.

5. **Register everything**  
   - Add new capabilities to `app/capabilities/registry.py` with name, description, responsibilities, tool list, approval commands, and lifecycle status.
   - Export new tools in `app/tools/__init__.py` and wire them into the relevant agent.

6. **Use `AIFunction` wrappers with limits**  
   - Wrap callable tools with `agent_framework.AIFunction` so schemas are auto-generated. Set `max_invocations=1` (or another reasonable cap) to prevent runaway tool loops.

7. **Guardrail-aware instructions**  
   - Update the SupervisorAgent prompt whenever you add capabilities so it knows when approvals are required, which tools to call for read vs write tasks, and how to summarize outcomes.

8. **Surface artifacts & logs**  
   - Persist important outputs (plan artifacts, drift reports, cost summaries) via the appropriate service (`artifact_store`, `ticket_store`) so UI clients can display them later.

9. **Document and test**  
   - Update `README.md`, `ARCHITECTURE.md`, and `IMPLEMENTATION_PLAN.md` for feature changes.
   - Add or adjust tests under `tests/` for new guardrails, services, or tools (`pytest -q` should remain green).

Following these rules ensures every capability behaves consistently in the chat UI and backend workflows.
