"""Unit tests for VisionCaptioner."""

from kip.core.extract.multimodal import VisualAsset
from kip.core.llm.vision import VisionCaptioner


def test_vision_captioner_heuristic() -> None:
    asset = VisualAsset(
        asset_id="123",
        rel_path="docs/architecture_diagram.png",
        abs_path="/tmp/architecture_diagram.png",
        format="png",
        size_bytes=1024,
        alt_text="Microservice architecture overview",
        referencing_doc="docs/overview.md",
        section_context="System Design",
    )
    captioner = VisionCaptioner()
    desc = captioner.describe_asset(asset)

    assert desc.diagram_type == "architecture"
    assert "System Design" in desc.detailed_description
    assert "Microservice" in desc.extracted_entities or "architecture" in desc.extracted_entities
