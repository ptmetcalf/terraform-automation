"""AI Engineer supervisor agent that orchestrates capability execution."""
from __future__ import annotations

from textwrap import dedent

from app.agents.base import build_logic_agent
from app.agents.schemas import SupervisorResponse
from app.capabilities import get_capabilities
from app.constants import APPLY_AUTHORIZED_FLAG, PLAN_APPROVED_FLAG
from app.tools.capability_router_tool import devops_capability_tool
from app.tools.drift_monitor_tool import drift_monitor_tool
from app.tools.mcp_clients import get_github_mcp_tools
from app.tools.project_onboarding_tool import project_onboarding_tool
from app.tools.repo_discovery_tool import repo_discovery_tool


def _capability_table() -> str:
    rows = []
    for capability in get_capabilities():
        rows.append(
            f"- **{capability.title}** (`{capability.slug}`): {capability.description} "
            f"(approval cmds: {', '.join(capability.approval_commands) or 'none'})"
        )
    return "\n".join(rows)


INSTRUCTIONS = dedent(
    f"""
    You are the AI Engineer supervisor agent. Hold a natural language conversation with the operator,
    understand their goals, and coordinate the specialist capabilities below. Always:

    {_capability_table()}

    Guardrails:
    - Never trigger coding/DevOps activities until the human unlocks `{PLAN_APPROVED_FLAG}` via `/approve plan`.
    - Never allow apply/deployment operations until `{APPLY_AUTHORIZED_FLAG}` is set via `/approve apply`.
    - SRE remediation (running scripts that modify state) requires `/approve sre-action`, but READ-ONLY diagnostics such as drift monitoring do not require approval.
    - Collect missing context (repo URL, workspace path, environment, etc.) before invoking any capability tool.
    - Use the configured GitHub MCP server to discover repositories, inspect code, and open pull requests when needed. Prefer these MCP-native tools over custom scripts for repo-level tasks. If the MCP server is not available, fall back to the built-in `discover_repos` tool to list accessible repositories.
    - Use `drift_monitor` for read-only Terraform drift/health checks. Use `run_devops_capability` only when code changes or GitOps actions are needed.
    - When the operator wants to onboard a new repository, first inspect available repos (if needed), then collect repo/workspace/env/branch metadata and call `create_project` to clone/register it before running other capabilities.
    - After running a capability, summarize the outcome, outstanding approvals, and next recommended steps.
    - If a capability cannot run (missing data/permissions), explain what the human must provide.
    - Invoke at most one tool per user turn; if more than one action is required, summarize the plan and ask for confirmation.
    - Maintain a helpful conversational tone and always respond with plain language plus bullet lists when appropriate.
    """
).strip()


_GITHUB_TOOLS = get_github_mcp_tools()
_TOOLS = [devops_capability_tool, drift_monitor_tool, project_onboarding_tool, *(_GITHUB_TOOLS or [repo_discovery_tool])]


def create_agent():
    return build_logic_agent(
        name="SupervisorAgent",
        instructions=INSTRUCTIONS,
        tools=_TOOLS,
        response_format=SupervisorResponse,
    )


agent = create_agent()
