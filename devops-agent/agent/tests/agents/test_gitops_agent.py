from app.agents import gitops_agent
from app.agents.schemas import GitOpsResponse


def test_gitops_agent_configuration():
    assert gitops_agent.name == "GitOpsAgent"
    assert gitops_agent.chat_options.response_format is GitOpsResponse
    tools = gitops_agent.chat_options.tools or []
    assert len(tools) == 2
