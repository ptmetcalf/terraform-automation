from app.agents import architect_agent
from app.agents.schemas import DesignResponse


def test_architect_agent_configuration():
    assert architect_agent.name == "ArchitectAgent"
    assert architect_agent.chat_options.response_format is DesignResponse
    tools = architect_agent.chat_options.tools or []
    assert len(tools) >= 1
