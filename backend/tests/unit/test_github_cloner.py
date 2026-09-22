"""Unit tests for GitHub cloner URL parsing and validation."""

import pytest
from kip.core.github.cloner import GitCloner


def test_parse_github_url_valid() -> None:
    cloner = GitCloner()

    owner, repo = cloner.parse_github_url("https://github.com/openai/tiktoken")
    assert owner == "openai"
    assert repo == "tiktoken"

    owner2, repo2 = cloner.parse_github_url("https://github.com/fastapi/fastapi.git")
    assert owner2 == "fastapi"
    assert repo2 == "fastapi"


def test_parse_github_url_invalid() -> None:
    cloner = GitCloner()
    with pytest.raises(ValueError):
        cloner.parse_github_url("https://google.com/search")
