from pathlib import Path

from app.ingest import chunk_markdown, list_pdfs


def test_list_pdfs_missing_dir(tmp_path):
    assert list_pdfs(tmp_path / "missing") == []


def test_chunk_markdown_tracks_sections():
    chunks = chunk_markdown("# Intro\nhello\n# Details\nworld")
    assert [chunk.section_ref for chunk in chunks] == ["Intro", "Details"]
