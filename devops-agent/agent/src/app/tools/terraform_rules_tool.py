"""Expose Terraform standards to agents."""
from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pydantic import Field

RULES_PATH = Path(__file__).resolve().parents[2] / "docs" / "terraform-standards.md"


def get_terraform_standards(
    request: Annotated[dict | None, Field(description="Optional context (unused)")] = None
) -> str:
    """Return the current Terraform module standards document."""

    if not RULES_PATH.exists():
        raise FileNotFoundError("Terraform standards document missing; ensure docs/terraform-standards.md exists")
    return RULES_PATH.read_text(encoding="utf-8")
