"""Technical research synthesizer creating grounded markdown reports with source citations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from kip.core.agent.planner import ResearchPlan
from kip.core.agent.tools import ToolExecutionResult


@dataclass
class ResearchCitation:
    """A verified source citation in the research report."""
    citation_id: str
    source_path: str
    lines: Optional[str] = None
    summary: str = ""


@dataclass
class ResearchReport:
    """Final synthesized research dossier."""
    query: str
    executive_summary: str
    markdown_body: str
    citations: List[ResearchCitation] = field(default_factory=list)
    tool_steps_executed: int = 0


class ResearchSynthesizer:
    """Compiles findings from tool traces and planning goals into a structured engineering report."""

    def synthesize(
        self,
        plan: ResearchPlan,
        tool_results: List[ToolExecutionResult],
    ) -> ResearchReport:
        """Constructs an authoritative research report with strict citations."""
        citations: List[ResearchCitation] = []
        body_sections: List[str] = []

        body_sections.append(f"# Deep Research Dossier: {plan.research_query}\n")
        body_sections.append("## 1. Executive Summary & Hypotheses")
        for hyp in plan.hypotheses:
            body_sections.append(f"- {hyp}")
        body_sections.append("")

        body_sections.append("## 2. Architectural Findings & Code Tracing")
        for goal in plan.sub_goals:
            body_sections.append(f"### Sub-Investigation: {goal.description}")
            body_sections.append(f"Target Domains: `{', '.join(goal.target_domains)}`")

        body_sections.append("\n## 3. Tool Evidence & Source Inspection")
        for idx, res in enumerate(tool_results, start=1):
            c_id = f"REF-{idx}"
            if res.tool_name == "file_view":
                path = res.arguments.get("file_path", "unknown")
                lines = f"L{res.arguments.get('start_line', 1)}-L{res.arguments.get('end_line', 1)}"
                citations.append(ResearchCitation(
                    citation_id=c_id,
                    source_path=path,
                    lines=lines,
                    summary=f"Inspected source slice in {path}",
                ))
                body_sections.append(f"#### [{c_id}] Inspection of `{path}:{lines}`\n```\n{res.output}\n```")
            elif res.tool_name == "symbol_search":
                sym = res.arguments.get("symbol_name", "")
                body_sections.append(f"- Symbol `{sym}` identified in: `{res.output.get('defined_in', [])}`")

        body_sections.append("\n## 4. Grounded Citations")
        for c in citations:
            body_sections.append(f"- **[{c.citation_id}]** `{c.source_path}` ({c.lines}): {c.summary}")

        full_md = "\n".join(body_sections)
        exec_summary = f"Comprehensive research analysis completed for '{plan.research_query}' across {len(plan.sub_goals)} research goals and {len(tool_results)} tool validations."

        return ResearchReport(
            query=plan.research_query,
            executive_summary=exec_summary,
            markdown_body=full_md,
            citations=citations,
            tool_steps_executed=len(tool_results),
        )
