"""FastAPI entrypoint wiring the Agent Framework workflow and Dev UI."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app import agents
from app.api.routes_admin import router as tickets_router
from app.api.routes_chat import router as chat_router
from app.api.routes_capabilities import router as capabilities_router
from app.config import settings
from app.services.database import init_database, shutdown_database
from app.services.tool_installer import ensure_tool_binaries
from app.workflows.terraform_workflow import workflow

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

api_app = FastAPI(
    title="Terraform Agentic Orchestrator API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_app.include_router(chat_router)
api_app.include_router(capabilities_router)
api_app.include_router(tickets_router)

app = FastAPI(title="Terraform Agentic Orchestrator", docs_url=None, redoc_url=None)
app.mount("/api", api_app)

devui_app = None

def _register_devui(app: FastAPI) -> None:
    global devui_app
    if not settings.agent_framework_devui_enabled:
        logger.info("DevUI disabled via configuration")
        if not any(route.path == "/" for route in app.router.routes):
            @app.get("/")
            async def devui_disabled() -> dict[str, str]:
                return {"detail": "Dev UI disabled"}
        return
    try:
        from agent_framework.devui import DevServer
    except ModuleNotFoundError:
        logger.warning("agent-framework-devui package not installed; skipping Dev UI mount")
        if not any(route.path == "/" for route in app.router.routes):
            @app.get("/")
            async def devui_missing() -> dict[str, str]:
                return {"detail": "Dev UI dependencies missing"}
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
    app.mount("/", devui_app)
    logger.info("Mounted Dev UI at root path")


def _register_agui(app: FastAPI) -> None:
    if not settings.agent_framework_agui_enabled:
        logger.info("AG-UI disabled via configuration")
        return
    try:
        from agent_framework.ag_ui import add_agent_framework_fastapi_endpoint
    except ModuleNotFoundError:
        logger.warning("agent-framework-ag-ui package not installed; skipping AG-UI endpoint")
        return

    logger.info("Registering AG-UI endpoint on /agui/agentic_chat")
    add_agent_framework_fastapi_endpoint(app, agents.supervisor_agent, path="/agui/agentic_chat")
    logger.info("Registered AG-UI endpoint at /agui/agentic_chat")

_register_agui(app)


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Starting application bootstrap")
    if settings.tools_auto_install:
        await asyncio.to_thread(ensure_tool_binaries)
    await init_database()
    _register_devui(app)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await shutdown_database()


@app.get("/devui")
async def devui_entrypoint():
    if not settings.agent_framework_devui_enabled or devui_app is None:
        raise HTTPException(status_code=404, detail="Dev UI not available")
    return RedirectResponse("/")


@app.get("/docs")
async def global_docs() -> RedirectResponse:
    return RedirectResponse("/api/docs")


@app.get("/openapi.json")
async def global_openapi() -> RedirectResponse:
    return RedirectResponse("/api/openapi.json")


@api_app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
