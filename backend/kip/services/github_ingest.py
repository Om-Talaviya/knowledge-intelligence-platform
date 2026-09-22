"""GitHub repository ingestion coordinator and background indexer service."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from kip.core.chunking.code_chunker import CodeChunker
from kip.core.github.cloner import ClonedRepo, GitCloner
from kip.core.ingest.local_scanner import LocalScanner, ScanResult
from kip.core.ingest.symbol_extractor import RepoSymbolGraph, SymbolExtractor


@dataclass
class GitHubIngestJob:
    """State and progress for a GitHub repository ingestion task."""
    job_id: str
    repo_url: str
    branch: str
    status: str  # pending, cloning, scanning, analyzing_symbols, chunking, completed, failed
    owner: str = ""
    repo_name: str = ""
    total_files: int = 0
    processed_files: int = 0
    total_chunks: int = 0
    total_symbols: int = 0
    errors: List[str] = field(default_factory=list)


class GitHubIngestService:
    """Handles end-to-end ingestion of GitHub repositories into KIP's index."""

    def __init__(self) -> None:
        self.jobs: Dict[str, GitHubIngestJob] = {}
        self.cloner = GitCloner()
        self.scanner = LocalScanner()
        self.code_chunker = CodeChunker()
        self.symbol_extractor = SymbolExtractor()

    def ingest_repository(
        self,
        repo_url: str,
        branch: Optional[str] = None,
        auth_token: Optional[str] = None,
    ) -> GitHubIngestJob:
        """Executes clone, code extraction, symbol mapping, and indexing."""
        job_id = str(uuid.uuid4())
        job = GitHubIngestJob(
            job_id=job_id,
            repo_url=repo_url,
            branch=branch or "main",
            status="pending",
        )
        self.jobs[job_id] = job

        cloned: Optional[ClonedRepo] = None
        try:
            job.status = "cloning"
            cloned = self.cloner.clone_repository(
                repo_url=repo_url,
                branch=branch,
                auth_token=auth_token,
            )
            job.owner = cloned.owner
            job.repo_name = cloned.repo

            job.status = "scanning"
            scan_res: ScanResult = self.scanner.scan(cloned.local_path)
            job.total_files = scan_res.total_files

            job.status = "analyzing_symbols"
            file_contents: Dict[str, str] = {}
            for f in scan_res.files:
                if f.is_code:
                    try:
                        content = Path(f.abs_path).read_text(encoding="utf-8", errors="ignore")
                        file_contents[f.rel_path] = content
                    except Exception:
                        pass

            graph: RepoSymbolGraph = self.symbol_extractor.build_graph(file_contents)
            job.total_symbols = len(graph.symbol_to_files)

            job.status = "chunking"
            for rel_path, content in file_contents.items():
                chunks = self.code_chunker.chunk_source_code(content, rel_path)
                job.total_chunks += len(chunks)
                job.processed_files += 1

            job.status = "completed"
        except Exception as exc:
            job.status = "failed"
            job.errors.append(str(exc))
        finally:
            if cloned:
                cloned.cleanup()

        return job

    def get_job(self, job_id: str) -> Optional[GitHubIngestJob]:
        """Retrieves status of a GitHub ingestion job."""
        return self.jobs.get(job_id)


github_ingest_service = GitHubIngestService()
