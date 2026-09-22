"""Unit tests for CodeChunker."""

from kip.core.chunking.code_chunker import CodeChunker


def test_code_chunker_python() -> None:
    code = """import os
import sys

def add(a: int, b: int) -> int:
    return a + b

class Calculator:
    def __init__(self):
        self.value = 0

    def multiply(self, x: int) -> int:
        return self.value * x
"""
    chunker = CodeChunker(target_chunk_lines=5, max_chunk_lines=10, overlap_lines=1)
    chunks = chunker.chunk_source_code(code, "calc.py")

    assert len(chunks) >= 1
    assert chunks[0].language == "python"
    assert "add" in chunks[0].content or "Calculator" in chunks[0].content
    assert chunks[0].start_line == 1
