"""Code-aware and syntactic block chunker for repository intelligence."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".php": "php",
    ".rb": "ruby",
    ".sql": "sql",
    ".md": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
}


@dataclass
class CodeChunk:
    """A semantic chunk of source code or structured file."""
    content: str
    language: str
    start_line: int
    end_line: int
    symbol_name: Optional[str] = None
    symbol_type: Optional[str] = None
    chunk_index: int = 0
    token_count_approx: int = 0


class CodeChunker:
    """Chunks source code preserving logical boundaries, functions, classes, and comments."""

    def __init__(
        self,
        target_chunk_lines: int = 45,
        max_chunk_lines: int = 90,
        overlap_lines: int = 5,
    ) -> None:
        self.target_chunk_lines = target_chunk_lines
        self.max_chunk_lines = max_chunk_lines
        self.overlap_lines = overlap_lines

    def detect_language(self, filename_or_ext: str) -> str:
        """Determines programming language from filename or extension."""
        ext = "." + filename_or_ext.split(".")[-1].lower() if "." in filename_or_ext else filename_or_ext.lower()
        return EXTENSION_LANGUAGE_MAP.get(ext, "generic")

    def _find_boundaries(self, lines: List[str], language: str) -> List[int]:
        """Finds line indices where top-level symbols/blocks start."""
        boundaries: List[int] = [0]
        re_pattern = None

        if language == "python":
            re_pattern = re.compile(r"^(?:async\s+)?(?:def|class)\s+([A-Za-z0-9_]+)")
        elif language in ("typescript", "javascript"):
            re_pattern = re.compile(r"^(?:export\s+)?(?:async\s+)?(?:function|class|const|interface|type)\s+([A-Za-z0-9_]+)")
        elif language == "go":
            re_pattern = re.compile(r"^func\s+")
        elif language == "rust":
            re_pattern = re.compile(r"^(?:pub\s+)?(?:fn|struct|enum|trait|impl)\s+")

        if re_pattern:
            for idx, line in enumerate(lines):
                if idx > 0 and re_pattern.match(line):
                    boundaries.append(idx)

        return sorted(list(set(boundaries)))

    def chunk_source_code(self, source_code: str, filename_or_ext: str) -> List[CodeChunk]:
        """Chunks source code into structured CodeChunk objects."""
        lines = source_code.splitlines()
        if not lines:
            return []

        language = self.detect_language(filename_or_ext)
        boundaries = self._find_boundaries(lines, language)
        boundaries.append(len(lines))

        chunks: List[CodeChunk] = []
        curr_start = 0

        for i in range(len(boundaries) - 1):
            block_start = boundaries[i]
            block_end = boundaries[i + 1]
            block_len = block_end - block_start

            if curr_start < block_start and (block_end - curr_start) > self.max_chunk_lines:
                chunk_lines = lines[curr_start:block_start]
                if chunk_lines:
                    content = "\n".join(chunk_lines)
                    chunks.append(CodeChunk(
                        content=content,
                        language=language,
                        start_line=curr_start + 1,
                        end_line=block_start,
                        chunk_index=len(chunks),
                        token_count_approx=len(content.split()),
                    ))
                curr_start = max(0, block_start - self.overlap_lines)

            if block_len > self.max_chunk_lines:
                sub_start = block_start
                while sub_start < block_end:
                    sub_end = min(block_end, sub_start + self.target_chunk_lines)
                    sub_lines = lines[sub_start:sub_end]
                    content = "\n".join(sub_lines)
                    chunks.append(CodeChunk(
                        content=content,
                        language=language,
                        start_line=sub_start + 1,
                        end_line=sub_end,
                        chunk_index=len(chunks),
                        token_count_approx=len(content.split()),
                    ))
                    if sub_end >= block_end:
                        break
                    sub_start = max(sub_start + 1, sub_end - self.overlap_lines)
                curr_start = block_end
            else:
                if (block_end - curr_start) >= self.target_chunk_lines:
                    chunk_lines = lines[curr_start:block_end]
                    content = "\n".join(chunk_lines)
                    chunks.append(CodeChunk(
                        content=content,
                        language=language,
                        start_line=curr_start + 1,
                        end_line=block_end,
                        chunk_index=len(chunks),
                        token_count_approx=len(content.split()),
                    ))
                    curr_start = max(0, block_end - self.overlap_lines)

        if curr_start < len(lines):
            chunk_lines = lines[curr_start:]
            if chunk_lines:
                content = "\n".join(chunk_lines)
                chunks.append(CodeChunk(
                    content=content,
                    language=language,
                    start_line=curr_start + 1,
                    end_line=len(lines),
                    chunk_index=len(chunks),
                    token_count_approx=len(content.split()),
                ))

        return chunks
