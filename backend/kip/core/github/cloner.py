"""Git repository cloner, branch resolver, and safe sandbox manager."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ClonedRepo:
    """Represents a locally checked out clone of a remote repository."""
    owner: str
    repo: str
    branch: str
    local_path: Path
    is_temp: bool = True

    def cleanup(self) -> None:
        """Removes the cloned temporary directory if is_temp is True."""
        if self.is_temp and self.local_path.exists():
            shutil.rmtree(self.local_path, ignore_errors=True)


class GitCloner:
    """Safely clones and checks out remote Git repositories."""

    GITHUB_URL_REGEX = re.compile(
        r"^(?:https?://github\.com/|git@github\.com:)(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$"
    )

    def parse_github_url(self, url: str) -> tuple[str, str]:
        """Parses repository URL into (owner, repo). Raises ValueError if invalid."""
        cleaned = url.strip()
        match = self.GITHUB_URL_REGEX.match(cleaned)
        if not match:
            raise ValueError(f"Invalid GitHub repository URL: {url}")
        return match.group("owner"), match.group("repo")

    def clone_repository(
        self,
        repo_url: str,
        branch: Optional[str] = None,
        auth_token: Optional[str] = None,
        target_dir: Optional[Path | str] = None,
        depth: int = 1,
    ) -> ClonedRepo:
        """Clones a GitHub repository to a local directory with shallow depth."""
        owner, repo_name = self.parse_github_url(repo_url)

        # Construct authenticated URL if token provided
        if auth_token:
            clone_url = f"https://x-access-token:{auth_token}@github.com/{owner}/{repo_name}.git"
        else:
            clone_url = f"https://github.com/{owner}/{repo_name}.git"

        is_temp = False
        if target_dir is None:
            temp_dir = tempfile.mkdtemp(prefix=f"kip_repo_{owner}_{repo_name}_")
            dest_path = Path(temp_dir)
            is_temp = True
        else:
            dest_path = Path(target_dir).resolve()
            dest_path.mkdir(parents=True, exist_ok=True)

        cmd = ["git", "clone", "--depth", str(depth)]
        if branch:
            cmd.extend(["--branch", branch, "--single-branch"])
        cmd.extend([clone_url, str(dest_path)])

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=120,
            )
        except subprocess.CalledProcessError as err:
            if is_temp:
                shutil.rmtree(dest_path, ignore_errors=True)
            # Mask auth token in error message if present
            err_msg = err.stderr or err.stdout or "Git clone failed."
            if auth_token:
                err_msg = err_msg.replace(auth_token, "***")
            raise RuntimeError(f"Failed to clone repository: {err_msg}") from err
        except subprocess.TimeoutExpired:
            if is_temp:
                shutil.rmtree(dest_path, ignore_errors=True)
            raise TimeoutError(f"Clone timed out after 120s for {owner}/{repo_name}")

        resolved_branch = branch or "main"
        return ClonedRepo(
            owner=owner,
            repo=repo_name,
            branch=resolved_branch,
            local_path=dest_path,
            is_temp=is_temp,
        )
