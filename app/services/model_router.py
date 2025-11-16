"""Model router mapping agent types to chat clients."""
from __future__ import annotations

import os
from functools import lru_cache

from agent_framework.openai import OpenAIChatClient

from app.config import settings


@lru_cache()
def get_logic_chat_client() -> OpenAIChatClient:
    """Return chat client targeting the OSS logic model."""

    return OpenAIChatClient(
        base_url=str(settings.oss_model_endpoint).rstrip("/"),
        api_key=settings.oss_model_api_key,
        model_id=os.environ.get("OSS_MODEL_ID", "chatgpt-20b"),
    )


@lru_cache()
def get_coding_chat_client() -> OpenAIChatClient:
    """Return chat client for Codex-style model."""

    return OpenAIChatClient(
        base_url=os.environ.get("CODEX_ENDPOINT", "https://api.openai.com/v1"),
        api_key=settings.codex_api_key,
        model_id=os.environ.get("CODEX_MODEL_ID", "codex-5.1"),
    )
