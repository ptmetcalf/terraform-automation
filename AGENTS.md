# AGENTS Guidelines

These instructions describe how to work on this repository when using an interactive coding agent (e.g., Codex CLI). Follow them to keep the developer experience fast, safe, and consistent.

## 1. Preferred Development Flow

- Run the combined UI + agent stack from the `devops-agent` workspace:
  ```bash
  cd devops-agent
  npm install      # installs UI deps + uv env for the agent
  npm run dev      # starts Next.js + FastAPI (via scripts/run-agent.sh)
  ```
- Use the `just` helpers when you only need the backend:
  ```bash
  just setup   # npm install with agent bootstrap
  just serve   # cd devops-agent/agent && uv run src/main.py
  just test    # cd devops-agent/agent && uv run pytest -q
  ```
- Prefer `just fullstack` once dependencies are installed—it wraps `npm run dev`, powers the ticket dashboard, and streams CopilotKit/AG-UI chats through the Terraform workflow (set `NEXT_PUBLIC_API_BASE_URL` when the backend is remote).
- The CopilotKit runtime talks to the FastAPI AG‑UI endpoint at `AGENT_FRAMEWORK_PYTHON_URL` (default `http://localhost:8000/agui/agentic_chat`). Override this env var (or `NEXT_PUBLIC_AGENT_FRAMEWORK_URL`) if your backend runs elsewhere, otherwise chat requests will 405 on `/`.
- The AG-UI developer console connects to `http://localhost:8000/agui/agentic_chat`; keep `npm run dev` or `just serve` running before launching the reference frontend (see `devops-agent/README.md`).
- Configure either `DEFAULT_PROJECT_ID` (after registering a project) or `DEFAULT_REPO_URL` + `DEFAULT_TERRAFORM_WORKSPACE` so AG-UI sessions have repo/workspace context; without these values the workflow will reject requests.
- When testing the Docker image, build once with `docker build -f infra/Dockerfile -t terraform-orchestrator .` and run containers outside the agent session unless container tests are explicitly required.
- Do **not** run destructive Terraform/GitOps commands automatically—simulate or mock them unless a human has explicitly approved the change.
- For UI work, point the [AG-UI reference frontend](https://github.com/ag-ui-protocol/ag-ui) at the local endpoint: `AGENT_FRAMEWORK_PYTHON_URL=http://localhost:8000/agui/agentic_chat pnpm turbo run dev --filter=demo-viewer`.
- Install `pnpm` (e.g., `corepack enable pnpm`) before running AG-UI-related commands.

## 2. Tools and Dependencies

- Python dependencies live under `devops-agent/agent/pyproject.toml` and are installed with `uv sync` (triggered automatically by `npm install` or `scripts/setup-agent.sh`).
- Use `uv run ...` for backend tasks so the managed environment is reused.
- UI dependencies are installed with your Node.js package manager (default `npm` via `devops-agent/package.json`).
- CLI tools (Terraform, Checkov, tfsec, Infracost) are auto-installed into `.tools/bin` or baked into the Docker image. Ensure `TOOLS_INSTALL_DIR` stays on `PATH` when invoking subprocesses.
- The Terraform MCP server is launched via `npx terraform-mcp-server`. Node.js/npm are required; install them through the Dockerfile or host package manager—avoid vendoring extra binaries into the repo.

## 3. Testing and QA

- Prefer `pytest -q` (or targeted test files) before submitting changes. Add new tests for workflows, capability routing, and approval logic as features expand.
- For linting/formatting, follow existing project conventions (PEP8/black-style). Introduce new tooling only after documenting it in `README.md`.

## 4. Documentation Discipline

- Any change that affects architecture, user-facing behavior, or capability scope **must** revalidate and update:
  - `ARCHITECTURE.md`
  - `README.md`
  - `IMPLEMENTATION_PLAN.md`
- Use `AGENTS.md` solely for these agent workflow instructions. Keep specs, plans, and capability details in the dedicated docs above.

## 5. Building or Updating Agents

- Follow the sub-agent specification in [`CONTRIBUTING.md`](CONTRIBUTING.md) whenever you add tools/capabilities (typed responses, HIL approvals, scoped responsibilities, tool reuse, etc.).
- Register new capabilities in `devops-agent/agent/src/app/capabilities/registry.py`, export their tools via `devops-agent/agent/src/app/tools/__init__.py`, and wire them into the supervisor agent so AG‑UI can discover them.
- Prefer `agent_framework.AIFunction` wrappers with `max_invocations` set to prevent runaway tool calls; read-only diagnostics should avoid approvals while write operations must require them.
- Use the `/api/projects` endpoints (and `project_store`) to onboard infrastructure repos—this lets the supervisor inject repo/workspace context automatically whenever `project_id` is provided in `/api/chat` requests. For GitHub interactions, rely on the configured GitHub MCP server (list repos, inspect files, open PRs) plus the `create_project` tool to clone + register new projects. If the MCP server is not configured, fall back to the built-in `discover_repos` tool so operators can still see accessible repos via the REST API.

## 6. Helpful Commands

| Command | Purpose |
| --- | --- |
| `cd devops-agent && npm run dev` | Start UI + FastAPI with live reload |
| `just fullstack` | Same as above (npm run dev wrapper) |
| `cd devops-agent/agent && uv run src/main.py` | Start the FastAPI dev server only |
| `cd devops-agent/agent && uv run --group dev pytest -q` | Run the Python test suite |
| `docker build -f infra/Dockerfile -t terraform-orchestrator .` | Build container image with baked tools |
| `docker run --env-file devops-agent/agent/.env -p 8000:8000 terraform-orchestrator` | Launch containerized API |

Following these guidelines keeps the agent-assisted workflow reliable and ensures documentation stays authoritative.
