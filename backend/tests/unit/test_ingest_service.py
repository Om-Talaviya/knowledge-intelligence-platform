"""Unit tests for LocalFolderIngestService."""

import tempfile
from pathlib import Path
from kip.services.ingest import LocalFolderIngestService


def test_ingest_service_directory() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "module.py").write_text("def run():\n    return 42\n", encoding="utf-8")
        (root / "README.md").write_text("# Demo Project\nContent here.", encoding="utf-8")

        service = LocalFolderIngestService()
        job = service.start_ingestion(str(root))

        assert job.status == "completed"
        assert job.total_files == 2
        assert job.processed_files == 2
        assert job.total_chunks >= 2
        assert len(job.errors) == 0
