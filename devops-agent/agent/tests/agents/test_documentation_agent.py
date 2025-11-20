from app.agents import documentation_agent
from app.agents.schemas import DocumentationResponse


def test_documentation_agent_configuration():
    assert documentation_agent.name == "DocumentationAgent"
    assert documentation_agent.chat_options.response_format is DocumentationResponse
    assert documentation_agent.chat_options.tools in (None, [])
