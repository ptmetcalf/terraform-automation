# Terraform Agentic Orchestrator

Agent Framework-powered multi-agent system that manages Terraform infrastructure changes with strong GitOps controls, layered reviews, and Dev UI/AG-UI support.

## Features

- **Microsoft Agent Framework** workflow with orchestrator + 12 specialist agents (architect, naming, coding, gitops, plan, review, security, cost, apply, documentation, drift).
- **Model routing** between an OSS OpenAI-compatible endpoint for logic/review agents and Codex 5.1 for coding.
- **Tools & services** for Terraform CLI, Checkov/tfsec, Infracost, MCP (Terraform + Microsoft Learn), GitOps enforcement, workspace locks, and ticket/audit persistence using SQLite.
- **FastAPI** server with `/api/chat` and `/api/tickets/*` APIs plus optional Dev UI mount at `/devui` when `agent-framework-devui` is installed and enabled.
- **Containerization** via `infra/Dockerfile` and `infra/docker-compose.dev.yml` for Podman/Docker workflows.

## Project Layout

```
terraform-automation/
├── app/
│   ├── api/                # REST endpoints
│   ├── agents/             # Agent definitions + schemas
│   ├── models/             # Pydantic domain models
│   ├── services/           # Persistence, locks, audit, model router
│   ├── tools/              # Terraform/Checkov/Cost/GitOps/MCP helpers
│   ├── workflows/          # Terraform workflow graph definition
│   ├── config.py           # Settings via environment variables
│   └── main.py             # FastAPI entrypoint + Dev UI mount
├── infra/
│   ├── Dockerfile
│   └── docker-compose.dev.yml
├── tests/
├── pyproject.toml / requirements.txt
└── README.md
```

## Project Documentation

- `README.md` – this file, covers onboarding and day-to-day operations.
- `ARCHITECTURE.md` – system design and workflow overview.
- `IMPLEMENTATION_PLAN.md` – capability roadmap and execution checklist.
- `AGENTS.md` – guidelines for working on the repo using agent-based tooling (e.g., Codex CLI).

## Capabilities API

Inspect available coworker capabilities via the REST API:

```
GET /api/capabilities          # list all capabilities with metadata
GET /api/capabilities/{slug}   # fetch a single capability definition
GET /api/tools/health          # report MCP/REST connectivity status for slash commands
```

The metadata is sourced from `app/capabilities/registry.py` and fuels both the supervisor workflow and future UI surfaces.

## Projects API

Register Terraform/Git projects so the supervisor can reuse defaults (repo URL, workspace directory, environments) without repeatedly prompting for context.

```
POST /api/projects
{
  "name": "Homelab Dev",
  "description": "Azure homelab stack",
  "repo_url": "https://github.com/acme/homelab.git",
  "workspace_dir": "/workspaces/homelab",
  "default_environment": "dev",
  "default_branch": "main",
  "project_type": "terraform"
}
```

Use `GET /api/projects` to list entries, `PUT /api/projects/{project_id}` to update, and `DELETE /api/projects/{project_id}` to remove. When calling `/api/chat`, pass `project_id` to automatically inject this context into the supervisor’s prompt (the agent will still accept explicit workspace/repo overrides when needed).

### Repository discovery & onboarding

Provide a GitHub token (`GITHUB_TOKEN`) and, when available, point `GITHUB_MCP_COMMAND`/`GITHUB_MCP_ARGS` at a GitHub MCP server binary (left disabled by default). The supervisor consumes those MCP tools directly, so it can:

1. Ask the GitHub MCP server for repositories the token can access (highlighting which ones are not yet onboarded). If the MCP server is not configured, the supervisor falls back to the built-in `discover_repos` REST helper so you can still list accessible repos.
2. Use the `create_project` tool to clone a repo into `PROJECTS_ROOT` (default `./projects`) and register the new project with default branch/environment metadata. Once registered, the GitOps agent manages commits/PRs for that repo using the same MCP connection.

Project types currently supported:
- `terraform` – Terraform codebases (default).
- `python-container` – Python app container projects (reserved for future agents).

The SupervisorAgent can invoke capabilities via tools (e.g., the DevOps tool wraps the existing `/api/chat` Terraform workflow), so the same APIs remain available programmatically.

## AG-UI Developer Console

The API exposes an AG-UI-compatible streaming endpoint at `/agui/agentic_chat` (mounted when `agent-framework-ag-ui` is installed and `AGENT_FRAMEWORK_AGUI_ENABLED=true`). It connects directly to the SupervisorAgent (AI Engineer) so you can chat with the coworker while it orchestrates sub-capabilities. Use the [AG-UI reference frontend](https://github.com/ag-ui-protocol/ag-ui) to visualize conversations, approvals, and capability state:

1. Start this API locally: `uvicorn app.main:app --reload`.
2. Clone and set up AG-UI (requires `pnpm`; install via `corepack enable pnpm` if needed):
   ```bash
   git clone https://github.com/ag-ui-protocol/ag-ui
   cd ag-ui
   pnpm install
   ```
3. Point AG-UI at your `/agui/agentic_chat` endpoint (served directly by FastAPI) and launch the dojo viewer:
   ```bash
   AGENT_FRAMEWORK_PYTHON_URL=http://localhost:8000/agui/agentic_chat pnpm turbo run dev --filter=demo-viewer
   ```
4. Open `http://localhost:3000` to interact with the coworker UI. The new `/api/capabilities` metadata and approval commands can be surfaced in AG-UI panels for richer context.

## Configuration

Environment variables are loaded via `app/config.py` using `pydantic-settings`. Key values:

| Variable | Description |
| --- | --- |
| `OSS_MODEL_ENDPOINT`, `OSS_MODEL_API_KEY`, `OSS_MODEL_ID` | OpenAI-compatible endpoint for logic/review agents. |
| `CODEX_API_KEY` / `OPENAI_API_KEY`, `CODEX_ENDPOINT`, `CODEX_MODEL_ID` | Codex 5.1 coding agent credentials. |
| `AGENT_FRAMEWORK_DEVUI_ENABLED` | Toggle Dev UI mount at `/devui`. Requires `agent-framework-devui` extra. |
| `AGENT_FRAMEWORK_AGUI_ENABLED` | Toggle AG-UI streaming endpoint at `/agui/agentic_chat`. Requires `agent-framework-ag-ui` extra. |
| `TF_CLI_PATH`, `TF_BACKEND_*` | Terraform CLI binary and backend settings. |
| `GITOPS_REPO_PATH` | Local path to the managed GitOps checkout. |
| `PROJECTS_ROOT` | Base directory where new projects are cloned during onboarding (default `./projects`). |
| `DATABASE_URL` | SQLAlchemy/Databases connection string (defaults to SQLite). |
| `TERRAFORM_MCP_COMMAND`, `TERRAFORM_MCP_ARGS` | Command/args used to start the Terraform MCP server (default `npx -y terraform-mcp-server`). |
| `GITHUB_MCP_COMMAND`, `GITHUB_MCP_ARGS`, `GITHUB_TOKEN` | (Optional) GitHub MCP stdio server configuration. Leave `GITHUB_MCP_COMMAND` empty to disable, or set it to e.g. `npx` with args for your chosen MCP implementation. |
| `MSLEARN_MCP_URL`, `MSLEARN_MCP_KEY` | Microsoft Learn MCP streamable HTTP endpoint (default public endpoint; key optional). |
| `TOOLS_INSTALL_DIR`, `TOOLS_AUTO_INSTALL` | Control where pinned CLI tools (Terraform, Checkov, tfsec, Infracost) are installed and whether auto-install runs on startup. |
| `TERRAFORM_VERSION`, `TERRAFORM_DOWNLOAD_URL`, etc. | Optional overrides for the auto-installer. Provide `<TOOL>_VERSION`/`<TOOL>_DOWNLOAD_URL` for Terraform, Checkov, tfsec, or Infracost to pin to alternative releases or mirrors. |

Create a `.env` file with these variables when running locally.

## Running Locally

Use the `justfile` targets to streamline common workflows:

1. Install dependencies:

   ```bash
   just setup
   just bootstrap-tools
   ```

2. Start the FastAPI server with reload:

   ```bash
   just serve
   ```

3. Run tests:

   ```bash
   just test
   ```

4. Send chat requests:

   ```bash
   http POST :8000/api/chat message="Add AKS cluster" requested_by="alice" terraform_workspace="aks-dev" repo_url="https://github.com/org/repo" branch="main"
   ```

5. Inspect tickets:

   ```bash
   http :8000/api/tickets/{ticket_id}
   ```

6. If `AGENT_FRAMEWORK_DEVUI_ENABLED=true` and the Dev UI extra is installed, open `http://localhost:8000/devui` for the debugging UI. To run the AG-UI frontend, use `just agui` (after cloning the AG-UI repo adjacent to this project).

### Tool installation

On startup the app downloads pinned versions of Terraform (1.9.5), Checkov (3.2.332), tfsec (1.28.3), and Infracost (0.10.42) into `TOOLS_INSTALL_DIR` (default `.tools/bin`). The directory is added to `PATH`, so you can rely on those binaries both locally and inside containers without baking them into the base image. Set `TOOLS_AUTO_INSTALL=false` or pre-populate the directory to skip downloads.

### Docker / Podman

The Dockerfile in `infra/Dockerfile` now bakes in the pinned CLI tools (Terraform, Checkov, tfsec, Infracost) and installs Node.js/npm so the Terraform MCP server can be launched via `npx` with no extra setup.

Build and run locally:

```bash
docker build -t terraform-orchestrator -f infra/Dockerfile .
docker run --env-file .env -p 8000:8000 \
  -v /home/batman/code/homelab-monorepo/terraform/azure:/workspace \
  -e GITOPS_REPO_PATH=/workspace \
  terraform-orchestrator
```

Or use Podman Compose for the dev stack:

```bash
podman compose -f infra/docker-compose.dev.yml up --build
```

The compose stack mounts the repository for iterative development.

## Agents & Workflows

Each agent is a `ChatAgent` with dedicated instructions and structured output models defined in `app/agents/schemas.py`. Highlights:

- **SupervisorAgent (AI Engineer)**: Conversational entry point that chats with humans, enforces guardrails, and invokes specialist capabilities (e.g., DevOps) via tools.
- **OrchestratorAgent**: Maintains `DeploymentTicket` state, routes phases, emits `OrchestratorDirective` for the DevOps capability.
- **Architect/Naming**: Use Terraform + Microsoft Learn MCP tools plus Azure naming helper.
- **CodingAgent**: Uses Codex 5.1 to write Terraform diffs and emits `GitOpsChangeRequest` objects; the GitOps agent is solely responsible for git activity.
- **Plan/Security/Cost/PlanReviewer**: Manage terraform plan, Checkov/tfsec, Infracost, and review fan-in before approvals.
- **ApplyAgent**: Handles human approval loops and Terraform apply invocations.
- **Drift Monitor**: Provides read-only Terraform drift checks on demand (no approval required) and hands results to the documentation agent.
- **Documentation Agent**: Compiles change summaries, runbooks, and artifacts after workflows complete.

`app/workflows/terraform_workflow.py` encodes the workflow graph using `WorkflowBuilder` with conditional routing from the orchestrator to each phase, plus sequential/fan-in edges mirroring the lifecycle described in the requirements.

### Supervisor guardrails

The supervisor refuses to advance to coding or apply until you explicitly unlock those stages. Use slash commands in `/api/chat` messages (or via the Dev UI / AG-UI) to flip the guardrails:

- `/approve plan` unlocks the coding phase once you are happy with the proposed design/plan.
- `/reset plan` (or `/lock coding`) re-locks coding if you want to revisit the plan.
- `/approve apply` unlocks the apply/approval phases once you are ready to run Terraform.
- `/hold apply` (or `/reset apply` / `/lock apply`) re-locks apply so changes are never executed without explicit human consent.
- `/approve sre-action` grants the SRE/Health responders permission to run remediation commands. `/reset sre-action` re-locks it.

The supervisor summarizes the current guardrail state in every prompt so you always see which stages are permitted.

## Persistence & Services

- `services/database.py` defines shared metadata/tables and async connection helpers (SQLite by default).
- `TicketStore`, `ArtifactStore`, `LockManager`, `AuditLogService` interact with this database.
- `ModelRouter` centralizes creation of `OpenAIChatClient` instances for logic vs coding models.

## Tools

- `tools/terraform_cli_tool.py`: Pydantic requests + wrappers around `terraform init/plan/show/apply` plus drift detection.
- `tools/checkov_tool.py`, `tools/cost_tool.py`, `tools/gitops_tool.py`, and `tools/azure_naming_tool.py` expose structured functions for agents to call.
- `tools/mcp_clients.py` provisions Terraform + Microsoft Learn MCP tool instances.
- `tools/terraform_rules_tool.py` exposes the living Terraform module standards (`docs/terraform-standards.md`) so agents consistently reuse and maintain modules.

## Testing

`tests/` is ready for unit/integration coverage (e.g., mocking Terraform/Checkov binaries and validating agent/tool glue). Add `pytest`-based suites to exercise agent schemas, tool behaviors, and workflow happy paths with fake stores.

## Development Notes

- Requires Python 3.11+.
- GitOps functions rely on clean working trees; ensure repositories are cloned locally or inside the container before invoking GitOps operations.
- Terraform/Checkov/Infracost binaries are optional at startup but required for real plan/apply/cost flows.
- Dev UI and AG-UI extras are optional; install `agent-framework-devui` and `agent-framework-ag-ui` to enable those integrations.
