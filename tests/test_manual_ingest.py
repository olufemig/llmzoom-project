from pathlib import Path

from app.manual_ingest import _clean_markdown, run_manual_ingest
import app.manual_ingest as manual_ingest


def test_manual_ingest_moves_markdown(tmp_path, monkeypatch):
    markdown_dir = tmp_path / "markdown"
    pages = [(
        "https://en.wikipedia.org/wiki/Arsenal_F.C.",
        "# Intro\nhello   world ![alt](image.png)\n\nmore text\n\n\n[img-ref]: image.png\n",
    )]

    class FakeCollection:
        def __init__(self):
            self.deleted = False

        def count(self):
            return {"ids": 0}

        def delete(self, **kwargs):
            self.deleted = True

        def get(self, include=None):
            return {"ids": []}

        def upsert(self, **kwargs):
            return None

    class FakeEmbedModel:
        def get_text_embedding(self, text):
            return [0.1, 0.2]

    monkeypatch.setattr("app.manual_ingest.get_collection", lambda: FakeCollection())
    monkeypatch.setattr("app.manual_ingest.get_embedding_model", lambda: FakeEmbedModel())
    monkeypatch.setattr("app.manual_ingest._existing_collections", lambda: [])
    monkeypatch.setattr("app.manual_ingest._crawl_pages", lambda _: pages)

    embedded = run_manual_ingest(markdown_dir=markdown_dir)

    assert embedded == 1
    assert not any(markdown_dir.glob("*.md"))
    cleaned = _clean_markdown(pages[0][1])
    assert "hello world" in cleaned
    assert "\n\n" in cleaned
    assert "[img-ref]" not in cleaned


def test_manual_ingest_clears_existing_collection(tmp_path, monkeypatch):
    markdown_dir = tmp_path / "markdown"
    pages = [("https://en.wikipedia.org/wiki/Arsenal_F.C.", "# Intro\nhello")]

    class FakeCollection:
        def __init__(self):
            self.deleted = False

        def count(self):
            return {"ids": 7}

        def delete(self, **kwargs):
            self.deleted = True

        def get(self, include=None):
            return {"ids": ["a", "b"]}

        def upsert(self, **kwargs):
            return None

    class FakeEmbedModel:
        def get_text_embedding(self, text):
            return [0.1, 0.2]

    collection = FakeCollection()
    monkeypatch.setattr("app.manual_ingest.get_collection", lambda: collection)
    monkeypatch.setattr("app.manual_ingest.get_embedding_model", lambda: FakeEmbedModel())
    monkeypatch.setattr("app.manual_ingest._existing_collections", lambda: ["manuals"])
    monkeypatch.setattr("app.manual_ingest._crawl_pages", lambda _: pages)

    embedded = run_manual_ingest(markdown_dir=markdown_dir)

    assert embedded == 0


def test_crawl_uses_mediawiki_api(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"parse": {"wikitext": "== Intro ==\nHello [[Arsenal F.C.|Arsenal]]"}}

    def fake_get(url, timeout=60, verify=None, headers=None):
        captured["url"] = url
        return FakeResponse()

    monkeypatch.setattr(manual_ingest.requests, "get", fake_get)

    pages = manual_ingest.asyncio.run(manual_ingest._crawl_pages("https://en.wikipedia.org/wiki/Arsenal_F.C."))

    assert pages == [("https://en.wikipedia.org/wiki/Arsenal_F.C.", "== Intro ==\nHello Arsenal")]
    assert "action=parse" in captured["url"]
