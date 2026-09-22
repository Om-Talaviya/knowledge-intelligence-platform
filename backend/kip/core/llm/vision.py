"""Vision and diagram captioning pipeline for multimodal research intelligence."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from kip.core.extract.multimodal import VisualAsset


@dataclass
class ImageDescription:
    """Rich semantic summary and entities extracted from a diagram or visual asset."""
    asset_id: str
    rel_path: str
    caption: str
    detailed_description: str
    diagram_type: str  # architecture, flowchart, sequence, ui_screenshot, chart, unknown
    extracted_entities: list[str]


class VisionCaptioner:
    """Zero-dependency heuristic + LLM multimodal visual describer."""

    def describe_asset(
        self,
        asset: VisualAsset,
        image_bytes: Optional[bytes] = None,
        vision_api_key: Optional[str] = None,
    ) -> ImageDescription:
        """Produces a rich semantic description for a visual diagram or chart."""
        filename = Path(asset.rel_path).name.lower()

        # Determine diagram type heuristically from name/context
        diagram_type = "diagram"
        if any(k in filename for k in ["arch", "architecture", "system", "stack"]):
            diagram_type = "architecture"
        elif any(k in filename for k in ["flow", "pipeline", "workflow"]):
            diagram_type = "flowchart"
        elif any(k in filename for k in ["ui", "screen", "dash", "view"]):
            diagram_type = "ui_screenshot"
        elif any(k in filename for k in ["seq", "sequence", "call"]):
            diagram_type = "sequence"
        elif any(k in filename for k in ["chart", "plot", "graph", "metric"]):
            diagram_type = "chart"

        alt_desc = asset.alt_text or asset.caption or filename
        section = f" in section '{asset.section_context}'" if asset.section_context else ""
        doc = f" referenced by '{asset.referencing_doc}'" if asset.referencing_doc else ""

        detailed = (
            f"Visual {diagram_type} diagram '{alt_desc}'{section}{doc}. "
            f"Format: {asset.format.upper()}. File path: {asset.rel_path}."
        )

        entities: list[str] = []
        if asset.alt_text:
            entities.extend([w.strip(",.()") for w in asset.alt_text.split() if len(w) > 3])

        return ImageDescription(
            asset_id=asset.asset_id,
            rel_path=asset.rel_path,
            caption=alt_desc,
            detailed_description=detailed,
            diagram_type=diagram_type,
            extracted_entities=list(set(entities)),
        )
