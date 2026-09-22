"""Unit tests for ResearchPlanner."""

from kip.core.agent.planner import ResearchPlanner


def test_research_planner_decomposition() -> None:
    planner = ResearchPlanner()
    plan = planner.create_plan("How does JWT authentication work with password hashing?")

    assert len(plan.sub_goals) == 4
    assert plan.estimated_steps == 4
    assert plan.sub_goals[0].goal_id == "g1-architecture"
    assert "JWT" in plan.sub_goals[0].search_queries[0]
