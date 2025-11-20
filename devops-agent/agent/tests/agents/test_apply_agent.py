from app.agents import apply_agent
from app.agents.schemas import ApplyResponse


def test_apply_agent_configuration():
    assert apply_agent.name == "ApplyAgent"
    assert apply_agent.chat_options.response_format is ApplyResponse
    tools = apply_agent.chat_options.tools or []
    assert len(tools) == 1
