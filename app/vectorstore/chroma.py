from __future__ import annotations

import hashlib
from pathlib import Path

import chromadb

from app.config import CHROMA_DIR


def get_client(chroma_dir: Path = CHROMA_DIR) -> chromadb.PersistentClient:
    chroma_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(chroma_dir))


def get_collection(name: str = "manuals", chroma_dir: Path = CHROMA_DIR):
    client = get_client(chroma_dir)
    return client.get_or_create_collection(name=name)


def reset_collection(name: str = "manuals", chroma_dir: Path = CHROMA_DIR):
    client = get_client(chroma_dir)
    try:
        client.delete_collection(name=name)
    except Exception:
        pass
    return client.get_or_create_collection(name=name)


def document_id(source_path: Path, chunk_index: int) -> str:
    return hashlib.sha1(f"{source_path}:{chunk_index}".encode("utf-8")).hexdigest()


def persist_document(
    *,
    collection,
    source_path: Path,
    text: str,
    source_title: str,
    source_url: str,
    section_ref: str,
    chunk_index: int,
    embedding: list[float],
) -> None:
    collection.upsert(
        ids=[document_id(source_path, chunk_index)],
        documents=[text],
        embeddings=[embedding],
        metadatas=[{
            "source_path": str(source_path),
            "source_title": source_title,
            "source_url": source_url,
            "section_ref": section_ref,
            "chunk_index": chunk_index,
        }],
    )
