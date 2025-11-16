"""FastAPI entrypoint wiring the Agent Framework workflow and Dev UI."""
from __future__ import annotations

import logging
from typing import Any, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import agents
from app.api.routes_admin import router as tickets_router
from app.api.routes_chat import router as chat_router
from app.config import settings
from app.services.database import init_database, shutdown_database
from app.workflows.terraform_workflow import workflow

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Terraform Agentic Orchestrator", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router)
app.include_router(tickets_router)

devui_app = None
agui_app = None

def _register_devui(app: FastAPI) -> None:
    global devui_app
    if not settings.agent_framework_devui_enabled:
        logger.info("DevUI disabled via configuration")
        return
    try:
        from agent_framework.devui import DevServer
    except ModuleNotFoundError:
        logger.warning("agent-framework-devui package not installed; skipping Dev UI mount")
        return

    entities: List[Any] = [
        workflow,
        agents.orchestrator_agent,
        agents.architect_agent,
        agents.naming_agent,
        agents.qa_agent,
        agents.coding_agent,
        agents.gitops_agent,
        agents.plan_agent,
        agents.plan_reviewer_agent,
        agents.security_agent,
        agents.cost_agent,
        agents.apply_agent,
        agents.documentation_agent,
        agents.drift_agent,
    ]
    server = DevServer(port=0, host="127.0.0.1", ui_enabled=True, mode="developer")
    server.register_entities(entities)
    devui_app = server.get_app()
    app.mount("/devui", devui_app)
    logger.info("Mounted Dev UI at /devui")


def _register_agui(app: FastAPI) -> None:
    global agui_app
    try:
        from agent_framework.ag_ui import add_agent_framework_fastapi_endpoint
    except ModuleNotFoundError:
        logger.warning("agent-framework-ag-ui package not installed; skipping AG-UI endpoint")
        return

    agui_app = FastAPI(title="AG-UI Gateway")
    add_agent_framework_fastapi_endpoint(agui_app, agents.orchestrator_agent, path="/")
    app.mount("/agui", agui_app)
    logger.info("Mounted AG-UI endpoint at /agui")


@app.on_event("startup")
async def on_startup() -> None:
    await init_database()
    _register_devui(app)
    _register_agui(app)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await shutdown_database()


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
