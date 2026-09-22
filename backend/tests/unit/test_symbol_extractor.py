"""Unit tests for SymbolExtractor."""

from kip.core.ingest.symbol_extractor import SymbolExtractor


def test_symbol_extractor_python() -> None:
    code = """import os
from math import sqrt

def calculate_distance(x: int, y: int) -> float:
    \"\"\"Calculates Euclidean distance.\"\"\"
    return sqrt(x*x + y*y)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
"""
    extractor = SymbolExtractor()
    syms = extractor.extract_python_symbols(code, "points.py")

    assert len(syms.exported_symbols) == 2
    assert syms.exported_symbols[0].name == "calculate_distance"
    assert syms.exported_symbols[0].kind == "function"
    assert syms.exported_symbols[1].name == "Point"
    assert syms.exported_symbols[1].kind == "class"
    assert "os" in syms.imports
    assert "math" in syms.imports


def test_symbol_graph_builder() -> None:
    files = {
        "a.py": "def foo(): pass",
        "b.py": "from a import foo\ndef bar(): pass",
    }
    extractor = SymbolExtractor()
    graph = extractor.build_graph(files)

    assert "foo" in graph.symbol_to_files
    assert "a.py" in graph.symbol_to_files["foo"]
    assert "bar" in graph.symbol_to_files
