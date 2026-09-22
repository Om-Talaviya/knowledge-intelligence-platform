"""Unit tests for MultimodalAssetExtractor."""

import tempfile
from pathlib import Path
from kip.core.extract/multimodal import MultimodalAssetExtractor if False else None
from kip.core.extract.multimodal import MultimodalAssetExtractor


def test_extract_markdown_images() -> None:
    extractor = MultimodalAssetExtractor()
    md = """# Architecture
Here is the system design diagram:
![KIP System Architecture](docs/architecture.png)

## Data Flow
![RAG Flow Diagram](assets/rag_flow.svg "Data Pipeline")
"""
    assets = extractor.extract_from_markdown(md, "README.md")
    assert len(assets) == 2
    assert assets[0].alt_text == "KIP System Architecture"
    assert assets[0].rel_path == "docs/architecture.png"
    assert assets[0].section_context == "Architecture"
    assert assets[1].alt_text == "RAG Flow Diagram"
    assert assets[1].section_context == "Data Flow"
