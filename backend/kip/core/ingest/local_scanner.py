"""Local directory and repository filesystem scanner with gitignore awareness."""

from __future__ import annotations

import fnmatch
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set

DEFAULT_IGNORED_PATTERNS = [
    ".git",
    ".git/**",
    ".github",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "var",
    "*.egg-info",
    ".DS_Store",
    "Thumbs.db",
]

BINARY_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".iso", ".zip", ".tar", ".gz",
    ".7z", ".rar", ".pdf", ".docx", ".xlsx", ".pptx", ".pyc", ".pyd",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".mp4", ".mp3",
    ".wav", ".ogg", ".mov", ".avi", ".sqlite", ".sqlite3", ".db",
}

TEXT_CODE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".txt", ".rst",
    ".html", ".css", ".scss", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".sh", ".bash", ".ps1", ".rs", ".go", ".c", ".cpp", ".h", ".hpp",
    ".java", ".kt", ".swift", ".sql", ".graphql", ".proto", ".xml",
}


@dataclass
class DiscoveredFile:
    """Represents a discovered file from a local directory or repository."""
    rel_path: str
    abs_path: str
    extension: str
    size_bytes: int
    is_binary: bool
    is_code: bool
    line_count: Optional[int] = None


@dataclass
class ScanResult:
    """Summary result of scanning a local folder."""
    root_path: str
    files: List[DiscoveredFile] = field(default_factory=list)
    total_files: int = 0
    total_bytes: int = 0
    skipped_count: int = 0
    ignored_patterns: List[str] = field(default_factory=list)


class LocalScanner:
    """Recursively scans a local directory, applying ignore rules and extracting metadata."""

    def __init__(
        self,
        max_files: int = 2000,
        max_file_size_bytes: int = 5 * 1024 * 1024,  # 5MB per file limit
        max_total_bytes: int = 100 * 1024 * 1024,   # 100MB overall limit
        extra_ignore_patterns: Optional[List[str]] = None,
    ) -> None:
        self.max_files = max_files
        self.max_file_size_bytes = max_file_size_bytes
        self.max_total_bytes = max_total_bytes
        self.ignore_patterns = list(DEFAULT_IGNORED_PATTERNS)
        if extra_ignore_patterns:
            self.ignore_patterns.extend(extra_ignore_patterns)

    def is_binary_content(self, file_path: Path) -> bool:
        """Heuristic check for binary content via null bytes."""
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(4096)
                if b"\x00" in chunk:
                    return True
            return False
        except Exception:
            return True

    def parse_gitignore(self, root_dir: Path) -> List[str]:
        """Loads additional ignore patterns from .gitignore if present."""
        patterns: List[str] = []
        gitignore_path = root_dir / ".gitignore"
        if gitignore_path.is_file():
            try:
                for line in gitignore_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                    cleaned = line.strip()
                    if cleaned and not cleaned.startswith("#"):
                        patterns.append(cleaned)
            except Exception:
                pass
        return patterns

    def should_ignore(self, rel_path: str, patterns: List[str]) -> bool:
        """Determines if a path matches any ignore rule."""
        normalized = rel_path.replace("\\", "/")
        parts = normalized.split("/")

        for pat in patterns:
            cleaned_pat = pat.rstrip("/")
            if fnmatch.fnmatch(normalized, pat) or fnmatch.fnmatch(normalized, f"*/{pat}"):
                return True
            if fnmatch.fnmatch(normalized, f"{cleaned_pat}/*") or fnmatch.fnmatch(normalized, f"*/{cleaned_pat}/*"):
                return True
            for part in parts:
                if fnmatch.fnmatch(part, cleaned_pat):
                    return True
        return False

    def scan(self, directory: Path | str) -> ScanResult:
        """Scans the given directory path and returns a ScanResult."""
        root = Path(directory).resolve()
        if not root.is_dir():
            raise ValueError(f"Specified path is not a directory: {directory}")

        all_patterns = list(self.ignore_patterns) + self.parse_gitignore(root)
        result = ScanResult(root_path=str(root), ignored_patterns=all_patterns)

        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = os.path.relpath(dirpath, root)
            if rel_dir != "." and self.should_ignore(rel_dir, all_patterns):
                dirnames.clear()
                continue

            # Filter out ignored directories in-place
            dirnames[:] = [
                d for d in dirnames
                if not self.should_ignore(os.path.join(rel_dir, d) if rel_dir != "." else d, all_patterns)
            ]

            for filename in filenames:
                rel_file = os.path.join(rel_dir, filename) if rel_dir != "." else filename
                if self.should_ignore(rel_file, all_patterns):
                    result.skipped_count += 1
                    continue

                abs_file = Path(dirpath) / filename
                try:
                    stat = abs_file.stat()
                    size = stat.st_size
                except OSError:
                    result.skipped_count += 1
                    continue

                if size > self.max_file_size_bytes:
                    result.skipped_count += 1
                    continue

                if result.total_bytes + size > self.max_total_bytes or len(result.files) >= self.max_files:
                    result.skipped_count += 1
                    continue

                ext = abs_file.suffix.lower()
                is_bin = ext in BINARY_EXTENSIONS or self.is_binary_content(abs_file)
                is_code = ext in TEXT_CODE_EXTENSIONS and not is_bin

                line_count: Optional[int] = None
                if not is_bin:
                    try:
                        line_count = len(abs_file.read_text(encoding="utf-8", errors="ignore").splitlines())
                    except Exception:
                        line_count = None

                disc = DiscoveredFile(
                    rel_path=rel_file.replace("\\", "/"),
                    abs_path=str(abs_file),
                    extension=ext,
                    size_bytes=size,
                    is_binary=is_bin,
                    is_code=is_code,
                    line_count=line_count,
                )
                result.files.append(disc)
                result.total_bytes += size

        result.total_files = len(result.files)
        return result
