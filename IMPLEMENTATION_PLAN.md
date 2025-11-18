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
| AI Engineer | Model training/deployment infra | ML toolchains, artifact stores | Requires approval of training runs + deployment diffs |
| Backend | Service code changes | Repo tooling, unit test harness | Requires approval per PR/patch |
| Frontend | UI code changes | Repo tooling, playwright/cypress runners | Requires approval per PR/patch |
| Cost Monitor | Budget alerts, reporting | Infracost, cloud billing APIs | Read-only; approvals only for automated remediation |
| Health Monitor | Telemetry dashboards, anomaly detection | Observability APIs | Read-only unless action requested |

## Implementation Plan

1. **Capability Registry**
   - Create `app/capabilities/registry.py` describing each capability (instructions, tools, schema, approval policy).
   - Surface metadata through an `/api/capabilities` endpoint for UI discovery.

2. **Workflow Refactor**
   - Replace the Terraform-specific workflow with a generic capability router.
   - Introduce `CapabilityDirective` / `CapabilityResponse` schemas plus shared approval metadata.

3. **Approval Service**
   - Expand `app/models/approval.py`, add `app/services/approval_store.py`, and expose `/api/approvals` endpoints.
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

## Documentation Requirements

- **ARCHITECTURE.md**: system design and evolution path. Update whenever workflows, orchestration, approvals, or infrastructure tooling change.
- **README.md**: onboarding guide and operational runbooks. Update when user-facing steps, env vars, or tooling behavior change.
- **IMPLEMENTATION_PLAN.md**: capability scope, specs, and checklists. Update when capabilities or execution plans change.

No pull request is complete until these documents reflect the current behavior.

## Execution Checklist

### Phase 1 – Foundations
- [x] Define capability data model and implement `app/capabilities/registry.py`.
- [x] Add `/api/capabilities` endpoint exposing registry metadata.
- [x] Update docs (Architecture + README) to describe the registry and API.

### Phase 2 – Workflow Refactor
- [ ] Design `CapabilityDirective` / `CapabilityResponse` schemas.
- [ ] Refactor `app/workflows/terraform_workflow.py` into a capability router (DevOps as first capability).
- [ ] Align supervisor instructions with the new routing logic.

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
