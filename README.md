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

## Configuration

Environment variables are loaded via `app/config.py` using `pydantic-settings`. Key values:

| Variable | Description |
| --- | --- |
| `OSS_MODEL_ENDPOINT`, `OSS_MODEL_API_KEY`, `OSS_MODEL_ID` | OpenAI-compatible endpoint for logic/review agents. |
| `CODEX_API_KEY` / `OPENAI_API_KEY`, `CODEX_ENDPOINT`, `CODEX_MODEL_ID` | Codex 5.1 coding agent credentials. |
| `AGENT_FRAMEWORK_DEVUI_ENABLED` | Toggle Dev UI mount at `/devui`. Requires `agent-framework-devui` extra. |
| `TF_CLI_PATH`, `TF_BACKEND_*` | Terraform CLI binary and backend settings. |
| `GIT_PROVIDER`, `GIT_USERNAME`, `GIT_TOKEN` | GitOps configuration. |
| `DATABASE_URL` | SQLAlchemy/Databases connection string (defaults to SQLite). |
| `TERRAFORM_MCP_COMMAND`, `TERRAFORM_MCP_ARGS` | Launch Terraform MCP server via stdio. |
| `MSLEARN_MCP_URL`, `MSLEARN_MCP_KEY` | Microsoft Learn MCP streamable HTTP endpoint. |

Create a `.env` file with these variables when running locally.

## Running Locally

1. Install dependencies (preferably in a virtual environment):

   ```bash
   pip install -r requirements.txt
   ```

2. Export required environment variables (see table above) and ensure Terraform/Checkov/Infracost binaries are available.

3. Start the API:

   ```bash
   uvicorn app.main:app --reload
   ```

4. Send chat requests:

   ```bash
   http POST :8000/api/chat message="Add AKS cluster" requested_by="alice" terraform_workspace="aks-dev" repo_url="https://github.com/org/repo" branch="main"
   ```

5. Inspect tickets:

   ```bash
   http :8000/api/tickets/{ticket_id}
   ```

6. If `AGENT_FRAMEWORK_DEVUI_ENABLED=true` and the Dev UI extra is installed, open `http://localhost:8000/devui` for the debugging UI.

### Docker / Podman

```bash
podman compose -f infra/docker-compose.dev.yml up --build
```

The compose stack mounts the repository for iterative development.

## Agents & Workflows

Each agent is a `ChatAgent` with dedicated instructions and structured output models defined in `app/agents/schemas.py`. Highlights:

- **OrchestratorAgent**: Maintains `DeploymentTicket` state, routes phases, emits `OrchestratorDirective`.
- **Architect/Naming**: Use Terraform + Microsoft Learn MCP tools plus Azure naming helper.
- **CodingAgent**: Uses Codex 5.1 to write Terraform diffs and emits `GitOpsChangeRequest` objects; the GitOps agent is solely responsible for git activity.
- **Plan/Security/Cost/PlanReviewer**: Manage terraform plan, Checkov/tfsec, Infracost, and review fan-in before approvals.
- **ApplyAgent**: Handles human approval loops and Terraform apply invocations.
- **Drift/Documentation**: Post-apply drift detection and documentation artifacts.

`app/workflows/terraform_workflow.py` encodes the workflow graph using `WorkflowBuilder` with conditional routing from the orchestrator to each phase, plus sequential/fan-in edges mirroring the lifecycle described in the requirements.

## Persistence & Services

- `services/database.py` defines shared metadata/tables and async connection helpers (SQLite by default).
- `TicketStore`, `ArtifactStore`, `LockManager`, `AuditLogService` interact with this database.
- `ModelRouter` centralizes creation of `OpenAIChatClient` instances for logic vs coding models.

## Tools

- `tools/terraform_cli_tool.py`: Pydantic requests + wrappers around `terraform init/plan/show/apply` plus drift detection.
- `tools/checkov_tool.py`, `tools/cost_tool.py`, `tools/gitops_tool.py`, and `tools/azure_naming_tool.py` expose structured functions for agents to call.
- `tools/mcp_clients.py` provisions Terraform + Microsoft Learn MCP tool instances.

## Testing

`tests/` is ready for unit/integration coverage (e.g., mocking Terraform/Checkov binaries and validating agent/tool glue). Add `pytest`-based suites to exercise agent schemas, tool behaviors, and workflow happy paths with fake stores.

## Development Notes

- Requires Python 3.11+.
- GitOps functions rely on clean working trees; ensure repositories are cloned locally or inside the container before invoking GitOps operations.
- Terraform/Checkov/Infracost binaries are optional at startup but required for real plan/apply/cost flows.
- Dev UI and AG-UI extras are optional; install `agent-framework-devui` and `agent-framework-ag-ui` to enable those integrations.
