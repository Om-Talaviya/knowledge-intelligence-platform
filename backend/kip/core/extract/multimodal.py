"""Extracts visual assets, architecture diagrams, and images from documents and repositories."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class VisualAsset:
    """Represents an extracted image, flowchart, architecture diagram, or visual plot."""
    asset_id: str
    rel_path: str
    abs_path: str
    format: str  # png, jpg, webp, svg, etc.
    size_bytes: int
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    referencing_doc: Optional[str] = None
    section_context: Optional[str] = None
    md5_hash: str = ""


class MultimodalAssetExtractor:
    """Extracts visual assets and embedded diagrams from files and markdown."""

    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".bmp"}
    MD_IMAGE_REGEX = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)")
    HTML_IMAGE_REGEX = re.compile(r"<img\s+[^>]*src=[\"'](?P<src>[^\"']+)[\"'][^>]*>", re.IGNORECASE)

    def extract_from_markdown(self, markdown_content: str, doc_rel_path: str, base_dir: Optional[Path] = None) -> List[VisualAsset]:
        """Extracts referenced images and alt descriptions from Markdown text."""
        assets: List[VisualAsset] = []
        lines = markdown_content.splitlines()

        current_heading = "Top Level"
        for line in lines:
            if line.startswith("#"):
                current_heading = line.lstrip("#").strip()

            for match in self.MD_IMAGE_REGEX.finditer(line):
                alt = match.group("alt")
                src = match.group("path").split()[0]  # strip optional title
                abs_p = str((base_dir / src).resolve()) if base_dir else src
                asset_id = hashlib.md5(f"{doc_rel_path}:{src}".encode("utf-8")).hexdigest()[:12]
                ext = Path(src).suffix.lower().lstrip(".") or "png"

                assets.append(VisualAsset(
                    asset_id=asset_id,
                    rel_path=src,
                    abs_path=abs_p,
                    format=ext,
                    size_bytes=0,
                    alt_text=alt,
                    caption=alt,
                    referencing_doc=doc_rel_path,
                    section_context=current_heading,
                ))

        return assets

    def extract_directory_images(self, directory: Path | str) -> List[VisualAsset]:
        """Finds all standalone image and diagram files in a directory."""
        dir_path = Path(directory)
        assets: List[VisualAsset] = []
        if not dir_path.is_dir():
            return assets

        for p in dir_path.rglob("*"):
            if p.is_file() and p.suffix.lower() in self.IMAGE_EXTENSIONS:
                try:
                    data = p.read_bytes()
                    h = hashlib.md5(data).hexdigest()
                    rel_p = str(p.relative_to(dir_path)).replace("\\", "/")
                    assets.append(VisualAsset(
                        asset_id=h[:12],
                        rel_path=rel_p,
                        abs_path=str(p.resolve()),
                        format=p.suffix.lower().lstrip("."),
                        size_bytes=len(data),
                        md5_hash=h,
                    ))
                except Exception:
                    continue
        return assets
