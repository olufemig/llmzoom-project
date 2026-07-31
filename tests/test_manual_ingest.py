from pathlib import Path

from app.manual_ingest import run_manual_ingest
import app.manual_ingest as manual_ingest


def test_manual_ingest_moves_markdown(tmp_path, monkeypatch):
    markdown_dir = tmp_path / "markdown"
    backup_dir = tmp_path / "backup"
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

    monkeypatch.setattr("app.manual_ingest.get_collection", lambda: FakeCollection())
    monkeypatch.setattr("app.manual_ingest._crawl_pages", lambda _: pages)

    embedded = run_manual_ingest(markdown_dir=markdown_dir, backup_dir=backup_dir)

    assert embedded == 1
    assert not (markdown_dir / "Arsenal_F.C..md").exists()
    assert (backup_dir / "markdown" / "Arsenal_F.C..md").exists()
    assert "image.png" not in (backup_dir / "markdown" / "Arsenal_F.C..md").read_text(encoding="utf-8")
    cleaned = (backup_dir / "markdown" / "Arsenal_F.C..md").read_text(encoding="utf-8")
    assert "hello world" in cleaned
    assert "\n\n" in cleaned
    assert "[img-ref]" not in cleaned


def test_manual_ingest_clears_existing_collection(tmp_path, monkeypatch):
    markdown_dir = tmp_path / "markdown"
    backup_dir = tmp_path / "backup"
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

    collection = FakeCollection()
    monkeypatch.setattr("app.manual_ingest.get_collection", lambda: collection)
    monkeypatch.setattr("app.manual_ingest._crawl_pages", lambda _: pages)

    embedded = run_manual_ingest(markdown_dir=markdown_dir, backup_dir=backup_dir)

    assert embedded == 1
    assert collection.deleted is True


def test_crawl_uses_depth_zero(monkeypatch):
    captured = {}

    class FakeCrawler:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def arun(self, start_url, config):
            captured["config"] = config
            return type("R", (), {"url": start_url, "clean_markdown": "# Intro"})()

    monkeypatch.setattr(manual_ingest, "AsyncWebCrawler", lambda config: FakeCrawler())

    pages = manual_ingest.asyncio.run(manual_ingest._crawl_pages("https://example.com"))

    assert pages == [("https://example.com", "# Intro")]
    assert captured["config"].deep_crawl_strategy.max_depth == 0
