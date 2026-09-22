"""Unit tests for GitHub ingestion coordinator with mocked cloner."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from kip.core.github.cloner import ClonedRepo
from kip.services.github_ingest import GitHubIngestService


@patch("kip.services.github_ingest.GitCloner.clone_repository")
def test_github_ingest_service(mock_clone: MagicMock) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "app.py").write_text("def start():\n    return True\n", encoding="utf-8")

        mock_clone.return_value = ClonedRepo(
            owner="testorg",
            repo="demo-app",
            branch="main",
            local_path=root,
            is_temp=False,
        )

        service = GitHubIngestService()
        job = service.ingest_repository("https://github.com/testorg/demo-app")

        assert job.status == "completed"
        assert job.owner == "testorg"
        assert job.repo_name == "demo-app"
        assert job.total_files == 1
        assert job.total_chunks >= 1
