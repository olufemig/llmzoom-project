from __future__ import annotations

import hashlib
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from app.config import CHROMA_DIR


def get_client(chroma_dir: Path = CHROMA_DIR) -> chromadb.PersistentClient:
    chroma_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(chroma_dir))


def get_collection(name: str = "manuals", chroma_dir: Path = CHROMA_DIR):
    client = get_client(chroma_dir)
    return client.get_or_create_collection(
        name=name,
        embedding_function=DefaultEmbeddingFunction(),
    )


def document_id(source_path: Path, chunk_index: int) -> str:
    return hashlib.sha1(f"{source_path}:{chunk_index}".encode("utf-8")).hexdigest()


def persist_document(
    *,
    collection,
    source_path: Path,
    text: str,
    section_ref: str,
    chunk_index: int,
) -> None:
    collection.upsert(
        ids=[document_id(source_path, chunk_index)],
        documents=[text],
        metadatas=[{
            "source_path": str(source_path),
            "section_ref": section_ref,
            "chunk_index": chunk_index,
        }],
    )
