"""Unit tests for ResearchToolOrchestrator."""

from kip.core.agent.tools import ResearchToolOrchestrator
from kip.core.ingest.symbol_extractor import RepoSymbolGraph


def test_research_tools_file_view_and_grep() -> None:
    files = {
        "src/auth.py": "def login(user, pwd):\n    return True\n",
        "src/user.py": "class User:\n    pass\n",
    }
    graph = RepoSymbolGraph(symbol_to_files={"login": ["src/auth.py"]})

    tools = ResearchToolOrchestrator(symbol_graph=graph, files_map=files)

    # 1. Symbol search
    res1 = tools.symbol_search("login")
    assert res1.output["defined_in"] == ["src/auth.py"]

    # 2. File view
    res2 = tools.file_view("src/auth.py", 1, 2)
    assert "1: def login" in res2.output
    assert not res2.is_error

    # 3. Grep code
    res3 = tools.grep_code("return True")
    assert len(res3.output["matches"]) == 1
    assert res3.output["matches"][0]["file"] == "src/auth.py"
