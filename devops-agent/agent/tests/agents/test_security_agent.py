from app.agents import security_agent
from app.agents.schemas import SecurityResponse


def test_security_agent_configuration():
    assert security_agent.name == "SecurityAgent"
    assert security_agent.chat_options.response_format is SecurityResponse
    tools = security_agent.chat_options.tools or []
    assert len(tools) == 1
