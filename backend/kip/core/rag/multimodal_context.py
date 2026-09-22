"""Cross-modal context builder combining source code, documentation, and visual diagram descriptions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from kip.core.llm.vision import ImageDescription


@dataclass
class RetrievedItem:
    """A retrieved piece of evidence (code chunk, document paragraph, or visual diagram)."""
    item_id: str
    item_type: str  # code, text, figure
    source_path: str
    content: str
    score: float = 1.0
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    diagram_type: Optional[str] = None


@dataclass
class MultimodalContext:
    """Packaged context with citations for the research agent."""
    formatted_prompt_context: str
    items: List[RetrievedItem] = field(default_factory=list)
    total_token_approx: int = 0
    code_count: int = 0
    text_count: int = 0
    figure_count: int = 0


class MultimodalContextBuilder:
    """Constructs grounded context containing text passages, code snippets, and visual diagram figures."""

    def __init__(self, max_tokens: int = 3500) -> None:
        self.max_tokens = max_tokens

    def build_context(
        self,
        retrieved_items: List[RetrievedItem],
        image_descriptions: Optional[List[ImageDescription]] = None,
    ) -> MultimodalContext:
        """Builds structured Markdown context with labeled passage and figure citations."""
        ctx_blocks: List[str] = []
        all_items: List[RetrievedItem] = list(retrieved_items)
        code_count = sum(1 for x in all_items if x.item_type == "code")
        text_count = sum(1 for x in all_items if x.item_type == "text")
        figure_count = sum(1 for x in all_items if x.item_type == "figure")

        if image_descriptions:
            for desc in image_descriptions:
                fig_item = RetrievedItem(
                    item_id=desc.asset_id,
                    item_type="figure",
                    source_path=desc.rel_path,
                    content=desc.detailed_description,
                    diagram_type=desc.diagram_type,
                )
                all_items.append(fig_item)
                figure_count += 1

        for idx, item in enumerate(all_items, start=1):
            if item.item_type == "code":
                lines_info = f":L{item.start_line}-L{item.end_line}" if item.start_line else ""
                block = f"--- [Code Block {idx}: {item.source_path}{lines_info}] ---\n```{item.source_path.split('.')[-1]}\n{item.content}\n```"
            elif item.item_type == "figure":
                block = f"--- [Figure {idx}: {item.source_path} ({item.diagram_type})] ---\nDescription: {item.content}"
            else:
                block = f"--- [Document Passage {idx}: {item.source_path}] ---\n{item.content}"

            ctx_blocks.append(block)

        joined = "\n\n".join(ctx_blocks)
        return MultimodalContext(
            formatted_prompt_context=joined,
            items=all_items,
            total_token_approx=len(joined.split()),
            code_count=code_count,
            text_count=text_count,
            figure_count=figure_count,
        )
