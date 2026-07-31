from app.ingest import chunk_markdown


def test_chunk_markdown_tracks_sections():
    chunks = chunk_markdown("# Intro\nhello\n# Details\nworld")
    assert [chunk.section_ref for chunk in chunks] == ["Intro", "Details"]


def test_chunk_markdown_splits_paragraphs():
    chunks = chunk_markdown("# Intro\npara one\n\npara two")
    assert [chunk.text for chunk in chunks] == ["para one", "para two"]
