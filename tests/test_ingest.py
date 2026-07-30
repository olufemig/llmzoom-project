from pathlib import Path

from app.ingest import chunk_markdown, ingest_pdf, list_pdfs


def test_list_pdfs_missing_dir(tmp_path):
    assert list_pdfs(tmp_path / "missing") == []


def test_chunk_markdown_tracks_sections():
    chunks = chunk_markdown("# Intro\nhello\n# Details\nworld")
    assert [chunk.section_ref for chunk in chunks] == ["Intro", "Details"]


def test_ingest_pdf_uses_chunk_count_and_upserts(monkeypatch, tmp_path):
    pdf_path = tmp_path / "manual.pdf"
    pdf_path.write_text("stub")

    monkeypatch.setattr("app.ingest.extract_markdown", lambda _: "# Intro\nhello")

    calls = []

    class DummyCollection:
        def upsert(self, **kwargs):
            calls.append(kwargs)

    assert ingest_pdf(pdf_path, collection=DummyCollection()) == 1
    assert len(calls) == 1
