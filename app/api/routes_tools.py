"""API routes reporting tool availability/health."""
from fastapi import APIRouter

from app.models.tooling import ToolsHealthResponse
from app.services.tool_health import list_tool_statuses


router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/health", response_model=ToolsHealthResponse)
async def get_tools_health() -> ToolsHealthResponse:
    return ToolsHealthResponse(items=list_tool_statuses())
