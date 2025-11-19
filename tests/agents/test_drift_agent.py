from app.agents import drift_agent
from app.agents.schemas import DriftResponse


def test_drift_agent_configuration():
    assert drift_agent.name == "DriftAgent"
    assert drift_agent.chat_options.response_format is DriftResponse
    tools = drift_agent.chat_options.tools or []
    assert len(tools) == 1
