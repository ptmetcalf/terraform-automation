import importlib

from agent_framework._agents import ChatAgent

from app import agents
from app.capabilities import get_capabilities


def test_agents_have_response_format():
    for name in agents.__all__:
        agent = getattr(agents, name)
        assert isinstance(agent, ChatAgent), f"{name} is not a ChatAgent"
        assert agent.chat_options.response_format is not None, f"{name} missing response_format"


def test_capabilities_declare_approval_commands():
    for capability in get_capabilities():
        if capability.approval_required:
            assert capability.approval_commands, f"{capability.slug} requires approval but has no commands"
