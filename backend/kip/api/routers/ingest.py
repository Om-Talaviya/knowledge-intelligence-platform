"""API Router for local folder and workspace codebase ingestion."""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from kip.services.ingest import ingest_service

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


class LocalIngestRequest(BaseModel):
    folder_path: str = Field(..., description="Absolute or relative path to local directory")
    ignore_patterns: Optional[List[str]] = Field(None, description="Additional glob patterns to ignore")


class IngestJobResponse(BaseModel):
    job_id: str
    target_path: str
    status: str
    total_files: int
    processed_files: int
    total_chunks: int
    errors: List[str]


@router.post("/local", response_model=IngestJobResponse)
def ingest_local_folder(req: LocalIngestRequest) -> IngestJobResponse:
    """Scans and indexes a local codebase or directory tree."""
    job = ingest_service.start_ingestion(req.folder_path)
    return IngestJobResponse(
        job_id=job.job_id,
        target_path=job.target_path,
        status=job.status,
        total_files=job.total_files,
        processed_files=job.processed_files,
        total_chunks=job.total_chunks,
        errors=job.errors,
    )


@router.get("/status/{job_id}", response_model=IngestJobResponse)
def get_ingestion_status(job_id: str) -> IngestJobResponse:
    """Polls progress of a folder or repository ingestion task."""
    job = ingest_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Ingestion job not found")
    return IngestJobResponse(
        job_id=job.job_id,
        target_path=job.target_path,
        status=job.status,
        total_files=job.total_files,
        processed_files=job.processed_files,
        total_chunks=job.total_chunks,
        errors=job.errors,
    )
