# AGENTS Guidelines

These instructions describe how to work on this repository when using an interactive coding agent (e.g., Codex CLI). Follow them to keep the developer experience fast, safe, and consistent.

## 1. Preferred Development Flow

- Use the local FastAPI dev server while iterating:
  ```bash
  . .venv/bin/activate
  uvicorn app.main:app --reload
  ```
- Or use the `just` scripts to streamline workflows:
  ```bash
  just setup   # install deps
  just serve   # run dev server
  just test    # run pytest
  ```
- The AG-UI developer console connects to the SupervisorAgent at `http://localhost:8000/agui/agentic_chat`; keep `just serve` running before `just agui`.
- When testing the Docker image, build once with `docker build -f infra/Dockerfile -t terraform-orchestrator .` and run containers outside the agent session unless container tests are explicitly required.
- Do **not** run destructive Terraform/GitOps commands automatically—simulate or mock them unless a human has explicitly approved the change.
- For UI work, point the [AG-UI reference frontend](https://github.com/ag-ui-protocol/ag-ui) at the local endpoint: `AGENT_FRAMEWORK_PYTHON_URL=http://localhost:8000/agui/agentic_chat pnpm turbo run dev --filter=demo-viewer`.
- Install `pnpm` (e.g., `corepack enable pnpm`) before running AG-UI-related commands.

## 2. Tools and Dependencies

- Python dependencies are managed via `requirements.txt`; keep the lockstep with `pip install -r requirements.txt` inside `.venv/`.
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
- Register new capabilities in `app/capabilities/registry.py`, export their tools via `app/tools/__init__.py`, and wire them into the supervisor agent so AG‑UI can discover them.
- Prefer `agent_framework.AIFunction` wrappers with `max_invocations` set to prevent runaway tool calls; read-only diagnostics should avoid approvals while write operations must require them.
- Use the `/api/projects` endpoints (and `project_store`) to onboard infrastructure repos—this lets the supervisor inject repo/workspace context automatically whenever `project_id` is provided in `/api/chat` requests. For GitHub interactions, rely on the configured GitHub MCP server (list repos, inspect files, open PRs) plus the `create_project` tool to clone + register new projects. If the MCP server is not configured, fall back to the built-in `discover_repos` tool so operators can still see accessible repos via the REST API.

## 6. Helpful Commands

| Command | Purpose |
| --- | --- |
| `. .venv/bin/activate && uvicorn app.main:app --reload` | Start FastAPI dev server with reload |
| `. .venv/bin/activate && pytest tests -q` | Run the Python test suite |
| `docker build -f infra/Dockerfile -t terraform-orchestrator .` | Build container image with baked tools |
| `docker run --env-file .env -p 8000:8000 terraform-orchestrator` | Launch containerized API |

Following these guidelines keeps the agent-assisted workflow reliable and ensures documentation stays authoritative.
