"""Autonomous Research Planner for breaking complex technical queries into targeted sub-investigations."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ResearchGoal:
    """A targeted sub-investigation goal."""
    goal_id: str
    description: str
    target_domains: List[str]  # e.g., ["architecture", "models", "api", "security", "tests"]
    search_queries: List[str]
    status: str = "pending"  # pending, executing, completed, failed


@dataclass
class ResearchPlan:
    """A structured multi-step deep research strategy."""
    research_query: str
    hypotheses: List[str]
    sub_goals: List[ResearchGoal] = field(default_factory=list)
    estimated_steps: int = 0


class ResearchPlanner:
    """Decomposes engineering questions into structured multi-hop search plans."""

    def create_plan(self, query: str) -> ResearchPlan:
        """Analyzes query keywords and builds a multi-phase research plan."""
        cleaned_query = query.strip()
        goals: List[ResearchGoal] = []

        # Goal 1: Repository architecture & high-level design
        goals.append(ResearchGoal(
            goal_id="g1-architecture",
            description="Investigate system architecture, directory topology, and core contracts",
            target_domains=["architecture", "documentation"],
            search_queries=[
                f"architecture {cleaned_query}",
                "overview design structure README",
            ],
        ))

        # Goal 2: Data models, schemas, and state representations
        goals.append(ResearchGoal(
            goal_id="g2-schemas-models",
            description="Identify primary data structures, entity schemas, and persistent state",
            target_domains=["models", "database"],
            search_queries=[
                f"class model schema entity {cleaned_query}",
                "table migration database type definition",
            ],
        ))

        # Goal 3: Core execution logic, services, and APIs
        goals.append(ResearchGoal(
            goal_id="g3-logic-apis",
            description="Examine API handlers, algorithmic workflows, and service implementations",
            target_domains=["api", "services", "logic"],
            search_queries=[
                f"service handler router controller {cleaned_query}",
                f"function implementation {cleaned_query}",
            ],
        ))

        # Goal 4: Test coverage and edge cases
        goals.append(ResearchGoal(
            goal_id="g4-verification-tests",
            description="Verify test suites, mock configurations, and failure guardrails",
            target_domains=["tests", "verification"],
            search_queries=[
                f"test {cleaned_query}",
                "unit test integration assertion fixture",
            ],
        ))

        return ResearchPlan(
            research_query=cleaned_query,
            hypotheses=[
                f"The implementation of '{cleaned_query}' spans core schemas, API services, and test verification.",
                f"Key design constraints are documented in architecture specs and ADRs.",
            ],
            sub_goals=goals,
            estimated_steps=len(goals),
        )
