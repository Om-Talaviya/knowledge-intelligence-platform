"""API Router for GitHub repository ingestion and webhook triggers."""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from kip.services.github_ingest import github_ingest_service

router = APIRouter(prefix="/api/github", tags=["github"])


class GitHubIngestRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL (https://github.com/owner/repo)")
    branch: Optional[str] = Field(None, description="Branch to checkout (defaults to main)")
    auth_token: Optional[str] = Field(None, description="GitHub Personal Access Token for private repos")


class GitHubJobResponse(BaseModel):
    job_id: str
    repo_url: str
    branch: str
    status: str
    owner: str
    repo_name: str
    total_files: int
    processed_files: int
    total_chunks: int
    total_symbols: int
    errors: List[str]


class GitHubWebhookPayload(BaseModel):
    repository: Optional[dict] = None
    ref: Optional[str] = None
    commits: Optional[List[dict]] = None


@router.post("/ingest", response_model=GitHubJobResponse)
def ingest_github_repository(req: GitHubIngestRequest) -> GitHubJobResponse:
    """Trigger background clone, analysis, and indexing of a GitHub repository."""
    job = github_ingest_service.ingest_repository(
        repo_url=req.repo_url,
        branch=req.branch,
        auth_token=req.auth_token,
    )
    return GitHubJobResponse(
        job_id=job.job_id,
        repo_url=job.repo_url,
        branch=job.branch,
        status=job.status,
        owner=job.owner,
        repo_name=job.repo_name,
        total_files=job.total_files,
        processed_files=job.processed_files,
        total_chunks=job.total_chunks,
        total_symbols=job.total_symbols,
        errors=job.errors,
    )


@router.get("/status/{job_id}", response_model=GitHubJobResponse)
def get_github_job_status(job_id: str) -> GitHubJobResponse:
    """Get the current progress and results of a GitHub ingestion job."""
    job = github_ingest_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="GitHub ingestion job not found")
    return GitHubJobResponse(
        job_id=job.job_id,
        repo_url=job.repo_url,
        branch=job.branch,
        status=job.status,
        owner=job.owner,
        repo_name=job.repo_name,
        total_files=job.total_files,
        processed_files=job.processed_files,
        total_chunks=job.total_chunks,
        total_symbols=job.total_symbols,
        errors=job.errors,
    )


@router.post("/webhook")
def github_webhook(payload: GitHubWebhookPayload) -> dict:
    """Webhook listener for automated re-indexing on repository push events."""
    if payload.repository and "html_url" in payload.repository:
        repo_url = payload.repository["html_url"]
        branch = payload.ref.replace("refs/heads/", "") if payload.ref else "main"
        job = github_ingest_service.ingest_repository(repo_url=repo_url, branch=branch)
        return {"received": True, "job_id": job.job_id}
    return {"received": True, "status": "ignored"}
