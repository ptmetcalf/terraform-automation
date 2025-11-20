"""Azure naming conventions helper."""
from __future__ import annotations

import hashlib
from typing import Annotated

from pydantic import BaseModel, Field


class NamingRequest(BaseModel):
    resource_type: str
    environment: str
    business_unit: str
    suffix: str | None = None
    max_length: int = 24


class NamingSuggestion(BaseModel):
    name: str
    rationale: str


def generate_resource_name(
    request: Annotated[NamingRequest, Field(description="Azure naming request context")]
) -> NamingSuggestion:
    """Produce deterministic Azure-compliant resource names."""

    base = f"{request.business_unit}-{request.environment}-{request.resource_type}".lower()
    base = base.replace("_", "-").replace(" ", "-")
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:4]
    name = f"{base}-{digest}"
    if request.suffix:
        name = f"{name}-{request.suffix.lower()}"
    name = name[: request.max_length]
    rationale = f"Name derived from BU={request.business_unit}, env={request.environment}, type={request.resource_type}."
    return NamingSuggestion(name=name, rationale=rationale)
