from app.agents import coding_agent
from app.agents.schemas import CodingResponse


def test_coding_agent_configuration():
    assert coding_agent.name == "CodingAgent"
    assert coding_agent.chat_options.response_format is CodingResponse
    tools = coding_agent.chat_options.tools or []
    assert len(tools) >= 1
