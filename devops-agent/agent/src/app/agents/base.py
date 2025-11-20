"""Agent factory helpers."""
from __future__ import annotations

from typing import Iterable, Sequence

from agent_framework import ChatAgent
from pydantic import BaseModel

from app.services.model_router import get_coding_chat_client, get_logic_chat_client


def build_logic_agent(
    *,
    name: str,
    instructions: str,
    tools: Sequence[object] | None = None,
    response_format: type[BaseModel] | None = None,
    middleware: Sequence[object] | None = None,
) -> ChatAgent:
    return ChatAgent(
        name=name,
        chat_client=get_logic_chat_client(),
        instructions=instructions,
        tools=list(tools or []),
        response_format=response_format,
        middleware=list(middleware or []),
    )


def build_coding_agent(
    *,
    name: str,
    instructions: str,
    tools: Sequence[object] | None = None,
    response_format: type[BaseModel] | None = None,
    middleware: Sequence[object] | None = None,
) -> ChatAgent:
    return ChatAgent(
        name=name,
        chat_client=get_coding_chat_client(),
        instructions=instructions,
        tools=list(tools or []),
        response_format=response_format,
        middleware=list(middleware or []),
    )
