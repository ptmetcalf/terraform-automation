from app.agents import orchestrator_agent
from app.agents.schemas import OrchestratorDirective


def test_orchestrator_agent_configuration():
    assert orchestrator_agent.name == "OrchestratorAgent"
    assert orchestrator_agent.chat_options.response_format is OrchestratorDirective
    assert orchestrator_agent.chat_options.tools in (None, [])
