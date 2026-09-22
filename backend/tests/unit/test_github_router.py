"""Unit tests for GitHub API router endpoints."""

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from kip.api import app
from kip.services.github_ingest import GitHubIngestJob

client = TestClient(app)


@patch("kip.api.routers.github.github_ingest_service.ingest_repository")
def test_github_ingest_endpoint(mock_ingest: MagicMock) -> None:
    mock_ingest.return_value = GitHubIngestJob(
        job_id="test-job-123",
        repo_url="https://github.com/org/repo",
        branch="main",
        status="completed",
        owner="org",
        repo_name="repo",
        total_files=5,
        processed_files=5,
        total_chunks=15,
        total_symbols=8,
    )

    resp = client.post("/api/github/ingest", json={"repo_url": "https://github.com/org/repo"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["job_id"] == "test-job-123"
    assert data["total_chunks"] == 15
