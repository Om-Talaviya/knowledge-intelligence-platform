"""Unit tests for MultimodalContextBuilder."""

from kip.core.llm.vision import ImageDescription
from kip.core.rag.multimodal_context import MultimodalContextBuilder, RetrievedItem


def test_multimodal_context_builder() -> None:
    builder = MultimodalContextBuilder()
    items = [
        RetrievedItem(
            item_id="1",
            item_type="code",
            source_path="backend/app.py",
            content="def hello(): return 'world'",
            start_line=1,
            end_line=2,
        ),
        RetrievedItem(
            item_id="2",
            item_type="text",
            source_path="docs/README.md",
            content="This is documentation text.",
        ),
    ]
    img = ImageDescription(
        asset_id="fig1",
        rel_path="docs/arch.png",
        caption="System architecture",
        detailed_description="Architecture diagram with frontend, backend, and DB",
        diagram_type="architecture",
        extracted_entities=["frontend", "backend"],
    )

    ctx = builder.build_context(items, [img])
    assert ctx.code_count == 1
    assert ctx.text_count == 1
    assert ctx.figure_count == 1
    assert "[Code Block 1: backend/app.py:L1-L2]" in ctx.formatted_prompt_context
    assert "[Figure 3: docs/arch.png" in ctx.formatted_prompt_context
