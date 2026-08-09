from app.ingest import chunk_markdown
import app.ingest as ingest


def test_chunk_markdown_tracks_sections():
    class FakeEmbedModel:
        pass

    ingest.get_embedding_model = lambda: FakeEmbedModel()
    chunks = chunk_markdown("# Intro\nhello\n# Details\nworld")
    assert [chunk.section_ref for chunk in chunks] == ["Intro", "Details"]


def test_chunk_markdown_splits_paragraphs():
    class FakeEmbedModel:
        pass

    ingest.get_embedding_model = lambda: FakeEmbedModel()
    chunks = chunk_markdown("# Intro\npara one\n\npara two")
    assert [chunk.section_ref for chunk in chunks] == ["Intro", "Intro"]
    assert all(chunk.text for chunk in chunks)
