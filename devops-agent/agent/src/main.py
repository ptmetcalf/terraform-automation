"""Entrypoint that exposes the Terraform Orchestrator FastAPI app under uvicorn."""

from __future__ import annotations

import os

import uvicorn
from dotenv import load_dotenv

from app.main import app as terraform_orchestrator_app

load_dotenv()

app = terraform_orchestrator_app


if __name__ == "__main__":  # pragma: no cover
    host = os.getenv("AGENT_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
