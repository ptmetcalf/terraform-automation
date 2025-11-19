from app.agents import plan_agent
from app.agents.schemas import PlanResponse


def test_plan_agent_configuration():
    assert plan_agent.name == "PlanAgent"
    assert plan_agent.chat_options.response_format is PlanResponse
    tools = plan_agent.chat_options.tools or []
    assert len(tools) == 1
