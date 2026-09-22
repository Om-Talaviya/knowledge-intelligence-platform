"""Extracts code symbols, exports, imports, and cross-file relationships."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class CodeSymbol:
    """Represents a defined function, class, type, or variable in code."""
    name: str
    kind: str  # function, class, method, interface, type, constant
    line_number: int
    docstring: Optional[str] = None
    is_exported: bool = True
    parent_scope: Optional[str] = None


@dataclass
class FileSymbols:
    """Symbols and imports extracted from a single file."""
    rel_path: str
    language: str
    symbols: List[CodeSymbol] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)

    @property
    def exported_symbols(self) -> List[CodeSymbol]:
        return [s for s in self.symbols if s.is_exported]


@dataclass
class RepoSymbolGraph:
    """Symbol table and dependency graph across an entire repository."""
    files: Dict[str, FileSymbols] = field(default_factory=dict)
    symbol_to_files: Dict[str, List[str]] = field(default_factory=dict)


class SymbolExtractor:
    """Extracts symbols and import dependencies across polyglot source files."""

    def extract_python_symbols(self, code: str, rel_path: str) -> FileSymbols:
        """Extracts Python AST symbols and imports."""
        file_syms = FileSymbols(rel_path=rel_path, language="python")
        try:
            tree = ast.parse(code)
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    doc = ast.get_docstring(node)
                    file_syms.symbols.append(CodeSymbol(
                        name=node.name,
                        kind="function",
                        line_number=node.lineno,
                        docstring=doc,
                        is_exported=not node.name.startswith("_"),
                    ))
                elif isinstance(node, ast.ClassDef):
                    doc = ast.get_docstring(node)
                    file_syms.symbols.append(CodeSymbol(
                        name=node.name,
                        kind="class",
                        line_number=node.lineno,
                        docstring=doc,
                        is_exported=not node.name.startswith("_"),
                    ))
                    # Nested methods
                    for sub in node.body:
                        if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            sub_doc = ast.get_docstring(sub)
                            file_syms.symbols.append(CodeSymbol(
                                name=sub.name,
                                kind="method",
                                line_number=sub.lineno,
                                docstring=sub_doc,
                                is_exported=not sub.name.startswith("_"),
                                parent_scope=node.name,
                            ))
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        file_syms.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    file_syms.imports.append(mod)
        except Exception:
            for match in re.finditer(r"^(?:async\s+)?def\s+([A-Za-z0-9_]+)", code, re.M):
                line_no = code[:match.start()].count("\n") + 1
                name = match.group(1)
                file_syms.symbols.append(CodeSymbol(
                    name=name, kind="function", line_number=line_no, is_exported=not name.startswith("_")
                ))
            for match in re.finditer(r"^class\s+([A-Za-z0-9_]+)", code, re.M):
                line_no = code[:match.start()].count("\n") + 1
                name = match.group(1)
                file_syms.symbols.append(CodeSymbol(
                    name=name, kind="class", line_number=line_no, is_exported=not name.startswith("_")
                ))
        return file_syms

    def extract_typescript_symbols(self, code: str, rel_path: str) -> FileSymbols:
        """Extracts TypeScript / JavaScript symbols and imports via pattern matching."""
        file_syms = FileSymbols(rel_path=rel_path, language="typescript")

        for match in re.finditer(
            r"^(?:export\s+)?(?:async\s+)?(?:function|class|interface|type|enum)\s+([A-Za-z0-9_]+)",
            code,
            re.M
        ):
            line_no = code[:match.start()].count("\n") + 1
            full_match = match.group(0)
            name = match.group(1)
            is_exported = "export" in full_match
            kind = "function"
            if "class" in full_match:
                kind = "class"
            elif "interface" in full_match:
                kind = "interface"
            elif "type" in full_match:
                kind = "type"
            elif "enum" in full_match:
                kind = "enum"

            file_syms.symbols.append(CodeSymbol(
                name=name, kind=kind, line_number=line_no, is_exported=is_exported
            ))

        for match in re.finditer(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]", code):
            file_syms.imports.append(match.group(1))

        return file_syms

    def extract_file(self, content: str, rel_path: str) -> FileSymbols:
        """Extracts symbols according to file extension."""
        ext = "." + rel_path.split(".")[-1].lower() if "." in rel_path else ""
        if ext == ".py":
            return self.extract_python_symbols(content, rel_path)
        elif ext in (".ts", ".tsx", ".js", ".jsx"):
            return self.extract_typescript_symbols(content, rel_path)
        else:
            return FileSymbols(rel_path=rel_path, language="text")

    def build_graph(self, files_dict: Dict[str, str]) -> RepoSymbolGraph:
        """Builds a global symbol and dependency graph for a collection of files."""
        graph = RepoSymbolGraph()
        for rel_path, content in files_dict.items():
            syms = self.extract_file(content, rel_path)
            graph.files[rel_path] = syms
            for sym in syms.symbols:
                if sym.name not in graph.symbol_to_files:
                    graph.symbol_to_files[sym.name] = []
                graph.symbol_to_files[sym.name].append(rel_path)
        return graph
