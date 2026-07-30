from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.config import DATA_DIR
from app.extract import extract_markdown
from app.vectorstore.chroma import get_collection, persist_document


@dataclass(frozen=True)
class IngestedChunk:
    text: str
    section_ref: str
    chunk_index: int


def list_pdfs(data_dir: Path = DATA_DIR) -> list[Path]:
    if not data_dir.exists():
        return []
    return sorted(data_dir.glob("*.pdf"))


def ensure_data_dir(data_dir: Path = DATA_DIR) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def chunk_markdown(markdown: str) -> list[IngestedChunk]:
    chunks: list[IngestedChunk] = []
    current_section = "Unknown section"
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            chunks.append(
                IngestedChunk(
                    text="\n".join(buffer).strip(),
                    section_ref=current_section,
                    chunk_index=len(chunks),
                )
            )
            buffer.clear()

    for line in markdown.splitlines():
        if line.startswith("#"):
            flush()
            current_section = line.lstrip("#").strip() or "Unknown section"
            continue
        if line.strip():
            buffer.append(line)

    flush()
    return [chunk for chunk in chunks if chunk.text]


def ingest_pdf(pdf_path: Path, collection=None) -> int:
    collection = collection or get_collection()
    markdown = extract_markdown(pdf_path)
    chunks = chunk_markdown(markdown)
    for chunk in chunks:
        persist_document(
            collection=collection,
            source_path=pdf_path,
            text=chunk.text,
            section_ref=chunk.section_ref,
            chunk_index=chunk.chunk_index,
        )
    return len(chunks)


def ingest_all(data_dir: Path = DATA_DIR, collection=None) -> dict[str, int]:
    ensure_data_dir(data_dir)
    collection = collection or get_collection()
    results: dict[str, int] = {}
    for pdf_path in list_pdfs(data_dir):
        results[str(pdf_path)] = ingest_pdf(pdf_path, collection=collection)
    return results
