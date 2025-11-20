"""Capability metadata API."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.capabilities import Capability, get_capabilities, get_capability

router = APIRouter(prefix="/capabilities", tags=["capabilities"])


@router.get("/", response_model=list[Capability])
async def list_capabilities() -> list[Capability]:
    """Return all defined coworker capabilities."""

    return get_capabilities()


@router.get("/{slug}", response_model=Capability)
async def get_capability_detail(slug: str) -> Capability:
    capability = get_capability(slug)
    if capability is None:
        raise HTTPException(status_code=404, detail=f"Capability '{slug}' not found")
    return capability
