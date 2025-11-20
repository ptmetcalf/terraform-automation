from app.agents import cost_agent
from app.agents.schemas import CostResponse


def test_cost_agent_configuration():
    assert cost_agent.name == "CostAgent"
    assert cost_agent.chat_options.response_format is CostResponse
    tools = cost_agent.chat_options.tools or []
    assert len(tools) == 1
