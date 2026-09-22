"""Tool orchestrator providing symbol search, file slicing, code grep, and diagram lookup."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from kip.core.ingest.symbol_extractor import RepoSymbolGraph


@dataclass
class ToolExecutionResult:
    """Outcome of an agent tool execution."""
    tool_name: str
    arguments: Dict[str, Any]
    output: Any
    is_error: bool = False
    error_message: Optional[str] = None


class ResearchToolOrchestrator:
    """Executes deterministic investigation tools against codebase and knowledge indices."""

    def __init__(
        self,
        symbol_graph: Optional[RepoSymbolGraph] = None,
        files_map: Optional[Dict[str, str]] = None,
    ) -> None:
        self.symbol_graph = symbol_graph or RepoSymbolGraph()
        self.files_map = files_map or {}
        self.execution_history: List[ToolExecutionResult] = []

    def symbol_search(self, symbol_name: str) -> ToolExecutionResult:
        """Finds all files defining or importing the given symbol."""
        matching_files = self.symbol_graph.symbol_to_files.get(symbol_name, [])
        output = {
            "symbol": symbol_name,
            "defined_in": matching_files,
            "count": len(matching_files),
        }
        res = ToolExecutionResult(tool_name="symbol_search", arguments={"symbol_name": symbol_name}, output=output)
        self.execution_history.append(res)
        return res

    def file_view(self, file_path: str, start_line: int = 1, end_line: Optional[int] = None) -> ToolExecutionResult:
        """Extracts a slice of source code from a file with line numbers."""
        content = self.files_map.get(file_path)
        if content is None:
            res = ToolExecutionResult(
                tool_name="file_view",
                arguments={"file_path": file_path},
                output="",
                is_error=True,
                error_message=f"File not found in index: {file_path}",
            )
            self.execution_history.append(res)
            return res

        lines = content.splitlines()
        max_line = len(lines)
        end = min(end_line or max_line, max_line)
        start = max(1, min(start_line, max_line))

        sliced = lines[start - 1 : end]
        annotated = [f"{start + i}: {line}" for i, line in enumerate(sliced)]
        output = "\n".join(annotated)

        res = ToolExecutionResult(
            tool_name="file_view",
            arguments={"file_path": file_path, "start_line": start, "end_line": end},
            output=output,
        )
        self.execution_history.append(res)
        return res

    def grep_code(self, pattern: str) -> ToolExecutionResult:
        """Greps across all indexed files for a string or regex."""
        matches: List[Dict[str, Any]] = []
        for path, text in self.files_map.items():
            for line_no, line in enumerate(text.splitlines(), start=1):
                if pattern.lower() in line.lower():
                    matches.append({"file": path, "line": line_no, "content": line.strip()})

        output = {"pattern": pattern, "matches": matches[:50], "total_matches": len(matches)}
        res = ToolExecutionResult(tool_name="grep_code", arguments={"pattern": pattern}, output=output)
        self.execution_history.append(res)
        return res
