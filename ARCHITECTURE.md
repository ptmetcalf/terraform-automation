# Architecture Overview

This project implements a modular “agent coworker” platform that exposes a conversational interface for developers while delegating work to specialized agents. Every operation that mutates infrastructure, code, or runtime state must go through a human-in-the-loop (HIL) approval step that includes clear descriptions of the proposed changes.

## High-Level Components

1. **Supervisor / Lead Engineer**
   - Aggregates ticket context, enforces guardrails, and routes work to capability agents via the workflow graph.
   - Injects guardrail summaries (e.g., plan/apply locks) into every prompt so downstream agents know which actions are permitted.

2. **Capability Agents**
   - Pluggable agents (DevOps, SRE, AI engineer, backend, frontend, cost, health, documentation) defined under `app/agents/`.
   - Each agent exports structured responses that capture outcomes, next steps, and whether HIL approval is required.
   - Capabilities rely on shared tools (`app/tools/`) such as Terraform wrappers, GitOps helpers, or MCP clients.

3. **Workflow Orchestrator**
   - `app/workflows/terraform_workflow.py` currently embodies the multi-phase orchestration; it will evolve into a generic capability router that sequences requested specialists.
   - Uses Agent Framework’s `WorkflowBuilder` to encode routing logic, fan-in/fan-out patterns, and recorders (e.g., plan artifacts).

4. **API Layer**
   - `app/api/routes_chat.py` exposes `/api/chat`, managing tickets, guardrail commands (e.g., `/approve plan`), and serialization of workflow outputs.
   - Additional FastAPI routers provide ticket administration and health checks.

5. **Persistence & Services**
   - SQLite-backed stores (`app/services/`) persist tickets, artifacts, locks, approvals (future), and audit logs.
   - Tool installer (`app/services/tool_installer.py`) ensures CLI dependencies (Terraform, Checkov, tfsec, Infracost) are available at runtime; the Docker image pre-installs them.

6. **Capability Registry**
   - `app/capabilities/registry.py` enumerates each coworker capability (slug, description, responsibilities, tools, approval commands, lifecycle status).
   - The data is exposed through `/api/capabilities` for UI surfaces and informs future workflow routing decisions.

6. **UI & Dev Experience**
   - `app/main.py` mounts the Dev UI (`/devui`) and AG-UI endpoints when packages are installed, enabling interactive debugging and visualization.
   - Future developer-facing UI will consume capability metadata and approval endpoints to present a coworker dashboard.

## Runtime Flow (Current State)

1. A developer POSTs to `/api/chat` with ticket info and a message.
2. The supervisor agent receives the message, along with guardrail summaries, and emits an `OrchestratorDirective`.
3. The workflow routes the ticket through design → coding → plan → review → approval → apply → post-apply/documentation, delegating to specialized agents.
4. Agents call shared tools (Terraform, MCP servers, GitOps helper) and emit structured responses captured by the workflow.
5. The API stores ticket updates, returns agent outputs, and surfaces any approval requirements.

## Evolution Path

The existing Terraform-focused workflow will be generalized into a capability registry plus routing layer. Each capability will define:

- Instructions template and response schema.
- Required tools and MCP servers.
- HIL policies (approval commands, data required for consent).
- UI metadata (status badges, artifact types).

This document must be kept current whenever architectural components, workflows, or capability behaviors change. Any PR touching agent logic, orchestration, tooling, or approvals should re-validate that ARCHITECTURE.md and README.md reflect reality.
