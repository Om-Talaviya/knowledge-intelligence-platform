"""API Router for Autonomous Deep Research Agent executions."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from kip.core.agent.planner import ResearchPlan, ResearchPlanner
from kip.core.agent.synthesizer import ResearchReport, ResearchSynthesizer
from kip.core.agent.tools import ResearchToolOrchestrator

router = APIRouter(prefix="/api/agent", tags=["agent"])


class ResearchRequest(BaseModel):
    query: str = Field(..., description="Technical engineering question or research prompt")
    repo_url: Optional[str] = Field(None, description="Optional target GitHub repository")
    folder_path: Optional[str] = Field(None, description="Optional local folder path")


class ResearchGoalDTO(BaseModel):
    goal_id: str
    description: str
    target_domains: List[str]
    status: str


class CitationDTO(BaseModel):
    citation_id: str
    source_path: str
    lines: Optional[str]
    summary: str


class ResearchResponse(BaseModel):
    query: str
    executive_summary: str
    markdown_body: str
    goals: List[ResearchGoalDTO]
    citations: List[CitationDTO]
    steps_executed: int


@router.post("/research", response_model=ResearchResponse)
def execute_deep_research(req: ResearchRequest) -> ResearchResponse:
    """Decomposes, investigates, and synthesizes a grounded research report."""
    planner = ResearchPlanner()
    plan: ResearchPlan = planner.create_plan(req.query)

    tools = ResearchToolOrchestrator()
    # Execute deterministic exploratory tool calls
    tools.grep_code(req.query.split()[0] if req.query else "def")
    tools.file_view("README.md", 1, 30)

    synthesizer = ResearchSynthesizer()
    report: ResearchReport = synthesizer.synthesize(plan, tools.execution_history)

    return ResearchResponse(
        query=report.query,
        executive_summary=report.executive_summary,
        markdown_body=report.markdown_body,
        goals=[
            ResearchGoalDTO(
                goal_id=g.goal_id,
                description=g.description,
                target_domains=g.target_domains,
                status=g.status,
            )
            for g in plan.sub_goals
        ],
        citations=[
            CitationDTO(
                citation_id=c.citation_id,
                source_path=c.source_path,
                lines=c.lines,
                summary=c.summary,
            )
            for c in report.citations
        ],
        steps_executed=report.tool_steps_executed,
    )
