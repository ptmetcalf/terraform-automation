# Agent Coworker Initiative

This document captures the evolving specification, architectural plan, and execution checklist for transforming the project into a modular “agent coworker” platform. It complements `ARCHITECTURE.md` (system design) and `README.md` (operator onboarding).

## Vision

- **Unified coworker**: One “Lead Engineer” (supervisor) agent that holds ticket context and delegates work to capability-specific agents.
- **Modular capabilities**: Each capability (SRE, DevOps, AI engineer, backend, frontend, cost, health) is pluggable with its own tools, schemas, and approval policies.
- **Human-in-the-loop**: Every mutation or deployment is gated by explicit user approval commands (e.g., `/approve sre-restart`, `/approve devops-apply`). Approvals always include diffs, impact, and rollback plans.
- **Developer-facing UI**: Provide a chat UI and dashboards showing capability state, outstanding approvals, artifacts, and live telemetry.

## Capability Overview

| Capability | Purpose | Key Tools | HIL Requirements |
| --- | --- | --- | --- |
| Supervisor | Route work, summarize state, enforce guardrails | Workflow orchestration | Reads guardrail flags before unlocking capabilities |
| DevOps | Terraform/Infra changes, CI/CD pipelines | Terraform CLI, GitOps tools, MCP | Requires `/approve plan` then `/approve apply` with diff + plan summary |
| SRE | Incident response, config/runtime fixes | Monitoring APIs, runbook executors, shell tools | Requires `/approve sre-action` per remediation |
| Drift Monitor | Read-only Terraform drift detection & health checks | Drift monitor tool, Terraform plan | No approval required (diagnostic only) |
| AI Engineer | Model training/deployment infra | ML toolchains, artifact stores | Requires approval of training runs + deployment diffs |
| Backend | Service code changes | Repo tooling, unit test harness | Requires approval per PR/patch |
| Frontend | UI code changes | Repo tooling, playwright/cypress runners | Requires approval per PR/patch |
| Cost Monitor | Budget alerts, reporting | Infracost, cloud billing APIs | Read-only; approvals only for automated remediation |
| Health Monitor | Telemetry dashboards, anomaly detection | Observability APIs | Read-only unless action requested |

## Implementation Plan

1. **Capability Registry**
   - Create `devops-agent/agent/src/app/capabilities/registry.py` describing each capability (instructions, tools, schema, approval policy).
   - Surface metadata through an `/api/capabilities` endpoint for UI discovery.

2. **Workflow Refactor**
   - Replace the Terraform-specific workflow with a generic capability router.
   - Introduce `CapabilityDirective` / `CapabilityResponse` schemas plus shared approval metadata.

3. **Approval Service**
   - Expand `devops-agent/agent/src/app/models/approval.py`, add `devops-agent/agent/src/app/services/approval_store.py`, and expose `/api/approvals` endpoints.
   - Integrate capability-specific `/approve <capability>` guardrails.

4. **UI Enablement**
   - Extend Dev UI/AG-UI to display capability state and approvals.
   - Draft the requirements for a developer-facing coworker dashboard.

5. **Tooling & Runtime**
   - Ensure required CLIs (Terraform, kubectl, ML tools, etc.) are baked into the Docker image or mounted.
   - Define capability-specific MCP servers or adapters where necessary.

6. **Incremental Migration**
   - Start with the existing Terraform agents as the DevOps capability.
   - Add SRE, Cost, Health, and later AI/Backend/Frontend agents with appropriate tooling.

## Next Steps

- Finalize capability definitions and schemas.
- Implement the registry and supervisor routing logic.
- Build approval endpoints and extend chat commands for capability-specific approvals.
- Draft UI wireframes for the developer chat/approval interface.

## Near-Term Delivery: Ticket Console UI Integration

To make the combined CopilotKit + FastAPI workspace useful beyond the stock demo, we will surface real deployment tickets inside the Next.js frontend and keep the experience aligned with the backend APIs. Deliverable scope:

1. Fetch real ticket data via `/api/tickets`.
2. Render that data with a refresh affordance so operators can monitor workflows without leaving the UI.
3. Document the new configuration knobs so other developers can run the experience without guesswork.

### Task Breakdown

- [x] **UI API helper**
  - Create `devops-agent/src/lib/api.ts` exporting a `getApiBaseUrl()` helper (reads `NEXT_PUBLIC_API_BASE_URL` with `http://localhost:8000` fallback) and a typed `fetchJson<T>(path: string)` that handles errors/logging.
- [x] **Tickets panel**
  - Add `TicketsPanel` component that:
    - Calls `fetchJson` to load `/api/tickets`.
    - Shows loading/error states, ticket metadata (id, status, requested_by, updated_at), and a refresh button.
    - Highlights the active ticket count to mirror backend activity.
- [x] **Page integration**
  - Replace the placeholder Proverbs UI with a layout that renders `TicketsPanel` (keeping the Copilot sidebar + theme control for now).
  - Ensure Copilot shared state no longer references the removed proverbs card to avoid confusing UX.
- [x] **Documentation updates**
  - README: document the new UI behavior and `NEXT_PUBLIC_API_BASE_URL` usage.
  - AGENTS.md: mention `just fullstack` now serves a ticket dashboard rather than the stock CopilotKit demo (so expectations are clear).
- [x] **Testing & validation**
  - Run `just test` (backend) and `npm run lint` (frontend) to ensure no regressions.

## Documentation Requirements

- **ARCHITECTURE.md**: system design and evolution path. Update whenever workflows, orchestration, approvals, or infrastructure tooling change.
- **README.md**: onboarding guide and operational runbooks. Update when user-facing steps, env vars, or tooling behavior change.
- **IMPLEMENTATION_PLAN.md**: capability scope, specs, and checklists. Update when capabilities or execution plans change.

No pull request is complete until these documents reflect the current behavior.

## Execution Checklist

### Phase 1 – Foundations
- [x] Define capability data model and implement `devops-agent/agent/src/app/capabilities/registry.py`.
- [x] Add `/api/capabilities` endpoint exposing registry metadata.
- [x] Update docs (Architecture + README) to describe the registry and API.

### Phase 2 – Workflow Refactor
- [ ] Design `CapabilityDirective` / `CapabilityResponse` schemas.
- [ ] Refactor `devops-agent/agent/src/app/workflows/terraform_workflow.py` into a capability router (DevOps as first capability).
- [x] Align supervisor instructions with the new routing logic (AG-UI now talks to the SupervisorAgent which can trigger the DevOps capability via tools).

### Phase 3 – Approval Service & Guardrails
- [ ] Implement approval store/service and persistence.
- [ ] Add `/api/approvals` CRUD endpoints and integrate with guardrail commands.
- [ ] Expose pending approvals (with plan/diff summaries) in Dev UI/AG-UI.

### Phase 4 – Capability Build-Out
- [ ] Migrate Terraform agents into the DevOps capability module.
- [ ] Introduce SRE, Cost, and Health monitor capabilities with initial tooling.
- [ ] Scaffold AI/Backend/Frontend agents with human approval hooks.

### Phase 5 – UI & DX Enhancements
- [ ] Document UI requirements (wireframes, contracts) and add to README/ARCHITECTURE.
- [ ] Implement streaming/status endpoints for capability progress.
- [ ] Deliver a developer-facing dashboard for chat + approvals.

### Phase 6 – Final Hardening
- [ ] Add automation (pre-commit or CI) to ensure ARCHITECTURE.md, README.md, and IMPLEMENTATION_PLAN.md stay current.
- [ ] Expand test coverage for registry loading, approval flows, and capability routing.
- [ ] Perform a final documentation pass covering end-to-end workflows and deployment steps.
