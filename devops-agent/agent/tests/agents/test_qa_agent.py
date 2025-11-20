from app.agents import qa_agent
from app.agents.schemas import QAResponse


def test_qa_agent_configuration():
    assert qa_agent.name == "QAAgent"
    assert qa_agent.chat_options.response_format is QAResponse
    assert qa_agent.chat_options.tools in (None, [])
