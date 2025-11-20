"""AG-UI adapter that routes chat requests through the Terraform workflow service."""
from __future__ import annotations

import json
from typing import Iterable, Sequence
from uuid import uuid4

from agent_framework import AgentRunResponse, AgentRunResponseUpdate, AgentThread, BaseAgent, ChatMessage, Role

from app.config import settings
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_executor import chat_service


class WorkflowChatAgent(BaseAgent):
    """AgentProtocol implementation that invokes the Terraform workflow."""

    def __init__(self) -> None:
        super().__init__(
            name="WorkflowController",
            description="Routes AG-UI chat requests through the Terraform deployment workflow.",
        )
        self._thread_ids: dict[int, str] = {}

    async def run(
        self,
        messages: str | ChatMessage | Sequence[str | ChatMessage] | None = None,
        *,
        thread: AgentThread | None = None,
        **kwargs,
    ) -> AgentRunResponse:  # noqa: ANN003
        normalized = self._normalize_messages(messages)
        thread = thread or self.get_new_thread()
        assistant_message, response = await self._invoke_workflow(normalized, thread)
        await self._notify_thread_of_new_messages(thread, normalized, [assistant_message])
        return AgentRunResponse(
            messages=[assistant_message],
            response_id=response.thread_id,
            value=response.model_dump(),
        )

    def run_stream(
        self,
        messages: str | ChatMessage | Sequence[str | ChatMessage] | None = None,
        *,
        thread: AgentThread | None = None,
        **kwargs,
    ) -> Iterable[AgentRunResponseUpdate]:  # noqa: ANN003
        normalized = self._normalize_messages(messages)
        thread = thread or self.get_new_thread()

        async def _stream():
            assistant_message, response = await self._invoke_workflow(normalized, thread)
            await self._notify_thread_of_new_messages(thread, normalized, [assistant_message])
            yield AgentRunResponseUpdate(
                text=assistant_message.text,
                role=assistant_message.role,
                response_id=response.thread_id,
            )

        return _stream()

    async def _invoke_workflow(
        self,
        messages: Sequence[ChatMessage],
        thread: AgentThread,
    ) -> tuple[ChatMessage, "ChatResponse"]:
        if not messages:
            raise ValueError("No user messages provided")
        user_message = self._latest_user_message(messages)
        if not user_message:
            raise ValueError("Unable to locate the latest user message")

        try:
            payload = self._build_chat_request(user_message, thread)
        except ValueError as exc:
            assistant_message, response = await self._run_supervisor_fallback(messages, thread, str(exc))
            return assistant_message, response

        response = await chat_service.run_chat(payload)
        assistant_message = ChatMessage(role=Role.ASSISTANT, text=self._format_response(response))
        return assistant_message, response

    def _build_chat_request(self, message: ChatMessage, thread: AgentThread) -> ChatRequest:
        request_kwargs: dict[str, object] = {
            "message": message.text,
            "intent_summary": message.text[:280],
            "requested_by": settings.agui_requested_by,
            "thread_id": self._get_thread_id(thread),
        }

        if settings.default_project_id:
            request_kwargs["project_id"] = settings.default_project_id
            request_kwargs["environment"] = settings.default_environment
            request_kwargs["branch"] = settings.default_branch
        else:
            missing = [
                name
                for name, value in (
                    ("DEFAULT_REPO_URL", settings.default_repo_url),
                    ("DEFAULT_TERRAFORM_WORKSPACE", settings.default_terraform_workspace),
                )
                if value is None
            ]
            if missing:
                raise ValueError(
                    "Missing required defaults for AG-UI workflow execution. "
                    "Set DEFAULT_PROJECT_ID or provide " + ", ".join(missing)
                )
            request_kwargs.update(
                {
                    "repo_url": settings.default_repo_url,
                    "workspace_dir": settings.default_workspace_dir,
                    "terraform_workspace": settings.default_terraform_workspace,
                    "branch": settings.default_branch,
                    "environment": settings.default_environment,
                }
            )

        return ChatRequest.model_validate(request_kwargs)

    def _format_response(self, response) -> str:  # noqa: ANN001
        lines = [
            f"Ticket {response.ticket_id} (status: {response.status})",
            f"Thread ID: {response.thread_id}",
        ]
        if response.workflow_outputs:
            lines.append("Workflow outputs:")
            for idx, output in enumerate(response.workflow_outputs, start=1):
                lines.append(f"{idx}. {self._stringify_output(output)}")
        else:
            lines.append("Workflow did not return any structured outputs.")
        return "\n".join(lines)

    @staticmethod
    def _stringify_output(output: object) -> str:
        if isinstance(output, (dict, list)):
            return json.dumps(output, indent=2)
        return str(output)

    @staticmethod
    def _normalize_messages(
        messages: str | ChatMessage | Sequence[str | ChatMessage] | None,
    ) -> list[ChatMessage]:
        if messages is None:
            return []
        if isinstance(messages, ChatMessage):
            return [messages]
        if isinstance(messages, str):
            return [ChatMessage(role=Role.USER, text=messages)]
        normalized: list[ChatMessage] = []
        for item in messages:
            if isinstance(item, ChatMessage):
                normalized.append(item)
            elif isinstance(item, str):
                normalized.append(ChatMessage(role=Role.USER, text=item))
            else:
                normalized.append(ChatMessage.from_dict(item))
        return normalized

    @staticmethod
    def _latest_user_message(messages: Sequence[ChatMessage]) -> ChatMessage | None:
        for message in reversed(messages):
            if message.role == Role.USER:
                return message
        return messages[-1] if messages else None

    def _get_thread_id(self, thread: AgentThread) -> str:
        thread_key = id(thread)
        if thread_key not in self._thread_ids:
            self._thread_ids[thread_key] = str(uuid4())
        return self._thread_ids[thread_key]

    async def _run_supervisor_fallback(
        self,
        messages: Sequence[ChatMessage],
        thread: AgentThread,
        error_message: str,
    ) -> tuple[ChatMessage, ChatResponse]:
        """If workflow context is missing, fall back to the supervisor agent so users can still interact."""
        from app.agents.supervisor_agent import agent as supervisor_agent

        supervisor_response = await supervisor_agent.run(messages=list(messages), thread=thread)
        if supervisor_response.messages:
            supervisor_message = supervisor_response.messages[-1]
        else:
            supervisor_message = ChatMessage(
                role=Role.ASSISTANT,
                text="The workflow requires repo/workspace context. "
                "Register a project via /api/projects or set DEFAULT_PROJECT_ID/DEFAULT_REPO_URL in the backend .env.",
            )

        assistant_message = ChatMessage(role=Role.ASSISTANT, text=supervisor_message.text)
        fallback_chat_response = ChatResponse(
            ticket_id="workflow-context-missing",
            thread_id=self._get_thread_id(thread),
            status="context_missing",
            workflow_outputs=[{"message": supervisor_message.text, "detail": error_message}],
        )
        return assistant_message, fallback_chat_response
