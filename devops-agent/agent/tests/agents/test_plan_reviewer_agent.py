from app.agents import plan_reviewer_agent
from app.agents.schemas import PlanReviewResponse


def test_plan_reviewer_agent_configuration():
    assert plan_reviewer_agent.name == "PlanReviewerAgent"
    assert plan_reviewer_agent.chat_options.response_format is PlanReviewResponse
    assert plan_reviewer_agent.chat_options.tools in (None, [])
