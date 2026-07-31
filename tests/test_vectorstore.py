from pathlib import Path

from app.vectorstore.chroma import document_id, persist_document


def test_document_id_changes_with_chunk_index(tmp_path):
    path = tmp_path / "source.md"
    assert document_id(path, 1) != document_id(path, 2)


def test_persist_document_uses_upsert(tmp_path):
    calls = []

    class DummyCollection:
        def upsert(self, **kwargs):
            calls.append(kwargs)

    persist_document(
        collection=DummyCollection(),
        source_path=tmp_path / "source.md",
        text="hello",
        source_title="Arsenal F.C.",
        source_url="https://en.wikipedia.org/wiki/Arsenal_F.C.",
        section_ref="Intro",
        chunk_index=0,
        embedding=[0.1, 0.2],
    )

    assert calls and calls[0]["documents"] == ["hello"]
