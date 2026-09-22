"""Unit tests for GitHub REST client with mocked responses."""

from unittest.mock import MagicMock, patch
from kip.core.github.client import GitHubClient


@patch("urllib.request.urlopen")
def test_github_client_get_repo(mock_urlopen: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"full_name": "owner/test-repo", "default_branch": "main", "stargazers_count": 42, "open_issues_count": 2}'
    mock_urlopen.return_value.__enter__.return_value = mock_response

    client = GitHubClient()
    repo_info = client.get_repo("owner", "test-repo")

    assert repo_info.full_name == "owner/test-repo"
    assert repo_info.default_branch == "main"
    assert repo_info.stars_count == 42
