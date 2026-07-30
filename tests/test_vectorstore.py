from pathlib import Path

from app.vectorstore.chroma import document_id


def test_document_id_changes_with_chunk_index(tmp_path):
    path = tmp_path / "manual.pdf"
    assert document_id(path, 1) != document_id(path, 2)
