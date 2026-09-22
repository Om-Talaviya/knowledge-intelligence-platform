"""Service for scanning and ingesting local codebases and directory trees."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from kip.core.chunking.code_chunker import CodeChunker
from kip.core.ingest.local_scanner import LocalScanner, ScanResult
from kip.core.ingest.symbol_extractor import SymbolExtractor


@dataclass
class IngestionJob:
    """Tracks status and metrics for an ongoing or completed ingestion job."""
    job_id: str
    target_path: str
    status: str  # pending, scanning, chunking, indexing, completed, failed
    total_files: int = 0
    processed_files: int = 0
    total_chunks: int = 0
    errors: List[str] = field(default_factory=list)


class LocalFolderIngestService:
    """Coordinates directory scanning, code chunking, symbol indexing, and vector storage."""

    def __init__(self) -> None:
        self.jobs: Dict[str, IngestionJob] = {}
        self.scanner = LocalScanner()
        self.code_chunker = CodeChunker()
        self.symbol_extractor = SymbolExtractor()

    def start_ingestion(self, folder_path: str) -> IngestionJob:
        """Starts synchronous/asynchronous ingestion of a local folder."""
        job_id = str(uuid.uuid4())
        job = IngestionJob(job_id=job_id, target_path=folder_path, status="pending")
        self.jobs[job_id] = job

        path = Path(folder_path)
        if not path.exists() or not path.is_dir():
            job.status = "failed"
            job.errors.append(f"Directory does not exist or is not a folder: {folder_path}")
            return job

        try:
            job.status = "scanning"
            scan_result: ScanResult = self.scanner.scan(path)
            job.total_files = scan_result.total_files

            job.status = "indexing"
            for discovered in scan_result.files:
                if discovered.is_binary:
                    continue
                try:
                    content = Path(discovered.abs_path).read_text(encoding="utf-8", errors="ignore")
                    chunks = self.code_chunker.chunk_source_code(content, discovered.rel_path)
                    job.total_chunks += len(chunks)
                    job.processed_files += 1
                except Exception as e:
                    job.errors.append(f"Failed processing {discovered.rel_path}: {e}")

            job.status = "completed"
        except Exception as ex:
            job.status = "failed"
            job.errors.append(str(ex))

        return job

    def get_job(self, job_id: str) -> Optional[IngestionJob]:
        """Retrieves job state by id."""
        return self.jobs.get(job_id)


# Global singleton instance
ingest_service = LocalFolderIngestService()
