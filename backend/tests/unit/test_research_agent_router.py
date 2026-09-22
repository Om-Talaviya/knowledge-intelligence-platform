"""Unit tests for Research Agent API endpoint."""

from fastapi.testclient import TestClient
from kip.api import app

client = TestClient(app)


def test_agent_research_endpoint() -> None:
    resp = client.post("/api/agent/research", json={"query": "How is document chunking performed?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "document chunking" in data["query"]
    assert len(data["goals"]) == 4
    assert len(data["markdown_body"]) > 50
