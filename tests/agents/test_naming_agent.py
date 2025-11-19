from app.agents import naming_agent
from app.agents.schemas import NamingResponse


def test_naming_agent_configuration():
    assert naming_agent.name == "NamingAgent"
    assert naming_agent.chat_options.response_format is NamingResponse
    tools = naming_agent.chat_options.tools or []
    assert len(tools) >= 1
