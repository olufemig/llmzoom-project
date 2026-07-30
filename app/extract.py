from __future__ import annotations

from pathlib import Path


def extract_markdown(pdf_path: Path) -> str:
    import pymupdf4llm

    return pymupdf4llm.to_markdown(str(pdf_path))
