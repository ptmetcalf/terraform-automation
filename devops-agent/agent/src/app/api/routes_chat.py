"""Chat API for orchestrating workflow runs."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_executor import chat_service

router = APIRouter(prefix="", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    try:
        return await chat_service.run_chat(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - workflow runtime errors bubble up
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {exc}") from exc
