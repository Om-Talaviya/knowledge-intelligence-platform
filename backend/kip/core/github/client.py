"""GitHub REST API client for fetching repo trees, file contents, and commit metadata."""

from __future__ import annotations

import base64
import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GitHubRepoInfo:
    """Metadata about a GitHub repository."""
    owner: str
    name: str
    full_name: str
    description: Optional[str]
    default_branch: str
    stars_count: int
    open_issues_count: int
    language: Optional[str]


@dataclass
class GitHubTreeEntry:
    """An entry in a GitHub recursive tree response."""
    path: str
    mode: str
    type: str  # blob or tree
    sha: str
    size: Optional[int] = None


class GitHubClient:
    """Lightweight zero-external-dependency GitHub REST API client."""

    BASE_URL = "https://api.github.com"

    def __init__(self, auth_token: Optional[str] = None) -> None:
        self.auth_token = auth_token

    def _request(self, endpoint: str) -> Dict[str, Any]:
        """Makes an HTTP GET request to GitHub API."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "KIP-Intelligence-Agent/1.0",
        }
        if self.auth_token:
            headers["Authorization"] = f"token {self.auth_token}"

        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                return json.loads(data.decode("utf-8"))
        except urllib.error.HTTPError as err:
            err_body = err.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"GitHub API Error {err.code}: {err_body}") from err
        except urllib.error.URLError as err:
            raise RuntimeError(f"Network error contacting GitHub API: {err.reason}") from err

    def get_repo(self, owner: str, repo: str) -> GitHubRepoInfo:
        """Fetches repository metadata."""
        data = self._request(f"repos/{owner}/{repo}")
        return GitHubRepoInfo(
            owner=owner,
            name=repo,
            full_name=data.get("full_name", f"{owner}/{repo}"),
            description=data.get("description"),
            default_branch=data.get("default_branch", "main"),
            stars_count=data.get("stargazers_count", 0),
            open_issues_count=data.get("open_issues_count", 0),
            language=data.get("language"),
        )

    def get_tree(self, owner: str, repo: str, branch: str = "main") -> List[GitHubTreeEntry]:
        """Fetches full recursive file tree for a branch."""
        data = self._request(f"repos/{owner}/{repo}/git/trees/{branch}?recursive=1")
        tree_items = data.get("tree", [])
        return [
            GitHubTreeEntry(
                path=item.get("path", ""),
                mode=item.get("mode", ""),
                type=item.get("type", "blob"),
                sha=item.get("sha", ""),
                size=item.get("size"),
            )
            for item in tree_items
        ]

    def get_raw_file(self, owner: str, repo: str, path: str, branch: str = "main") -> str:
        """Fetches and decodes the contents of a file in the repository."""
        data = self._request(f"repos/{owner}/{repo}/contents/{path}?ref={branch}")
        if "content" in data and data.get("encoding") == "base64":
            raw_bytes = base64.b64decode(data["content"])
            return raw_bytes.decode("utf-8", errors="ignore")
        return ""
