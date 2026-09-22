"""Unit tests for local folder and codebase scanner."""

import tempfile
from pathlib import Path
from kip.core.ingest.local_scanner import LocalScanner


def test_local_scanner_basic() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "main.py").write_text("print('hello')", encoding="utf-8")
        (root / "README.md").write_text("# Project\nDocumentation here.", encoding="utf-8")
        (root / ".gitignore").write_text("ignored_folder/\n*.log", encoding="utf-8")
        
        sub = root / "ignored_folder"
        sub.mkdir()
        (sub / "secret.txt").write_text("secret", encoding="utf-8")
        (root / "app.log").write_text("log data", encoding="utf-8")

        scanner = LocalScanner()
        result = scanner.scan(root)

        rel_paths = [f.rel_path for f in result.files]
        assert "main.py" in rel_paths
        assert "README.md" in rel_paths
        assert "ignored_folder/secret.txt" not in rel_paths
        assert "app.log" not in rel_paths
        assert result.total_files == 3  # main.py, README.md, .gitignore
