from app.agents import supervisor_agent
from app.agents.schemas import SupervisorResponse


def test_supervisor_agent_configuration():
    assert supervisor_agent.name == "SupervisorAgent"
    assert supervisor_agent.chat_options.response_format is SupervisorResponse
    tools = supervisor_agent.chat_options.tools or []
    assert len(tools) >= 3
