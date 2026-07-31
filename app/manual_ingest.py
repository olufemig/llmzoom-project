from __future__ import annotations

import asyncio
import re
from pathlib import Path

from crawl4ai import AsyncWebCrawler, BrowserConfig, BFSDeepCrawlStrategy, CrawlerRunConfig

from app.config import BACKUP_DIR, MARKDOWN_DIR
from app.ingest import chunk_markdown
from app.vectorstore.chroma import get_collection, persist_document


ARSENAL_WIKI_URL = "https://en.wikipedia.org/wiki/Arsenal_F.C."
IMAGE_MARKDOWN_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
IMAGE_REF_RE = re.compile(r"^\s*\[[^\]]+\]:\s+\S+\s*$", re.MULTILINE)
IMAGE_HTML_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)


def _source_name(url: str) -> str:
    tail = url.rstrip("/").rsplit("/", 1)[-1] or "arsenal-fc"
    return tail.replace("?", "_").replace("&", "_")


def _clean_markdown(markdown: str) -> str:
    markdown = IMAGE_MARKDOWN_RE.sub("", markdown)
    markdown = IMAGE_REF_RE.sub("", markdown)
    markdown = IMAGE_HTML_RE.sub("", markdown)

    cleaned_lines: list[str] = []
    previous_blank = False
    for line in markdown.splitlines():
        normalized = " ".join(line.split())
        if not normalized:
            if not previous_blank:
                cleaned_lines.append("")
            previous_blank = True
            continue

        cleaned_lines.append(normalized)
        previous_blank = False

    return "\n".join(cleaned_lines).strip()


def _save_markdown(markdown: str, source_name: str, markdown_dir: Path) -> Path:
    markdown_dir.mkdir(parents=True, exist_ok=True)
    target = markdown_dir / f"{source_name}.md"
    target.write_text(markdown, encoding="utf-8")
    return target


def _backup_markdown(markdown_path: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / markdown_path.name
    markdown_path.replace(target)
    return target


def _reset_collection(collection) -> None:
    count = collection.count()
    if isinstance(count, dict):
        count = count.get("ids", 0)
    if count:
        ids = collection.get(include=[]).get("ids", [])
        if ids:
            collection.delete(ids=ids)


def _page_markdown(result) -> str:
    markdown = getattr(result, "markdown", None)
    if markdown and getattr(markdown, "raw_markdown", None):
        return markdown.raw_markdown
    return getattr(result, "clean_markdown", None) or getattr(result, "text", None) or ""


async def _crawl_pages(start_url: str) -> list[tuple[str, str]]:
    browser_config = BrowserConfig(headless=True)
    crawl_config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=0, max_pages=100),
        verbose=False,
    )
    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun(start_url, config=crawl_config)

    pages: list[tuple[str, str]] = []
    if isinstance(results, list):
        for result in results:
            url = getattr(result, "url", start_url)
            markdown = _page_markdown(result)
            if markdown:
                pages.append((url, markdown))
    else:
        markdown = _page_markdown(results)
        if markdown:
            pages.append((getattr(results, "url", start_url), markdown))
    return pages


def run_manual_ingest(markdown_dir: Path = MARKDOWN_DIR, backup_dir: Path = BACKUP_DIR) -> int:
    collection = get_collection()
    _reset_collection(collection)
    pages_result = _crawl_pages(ARSENAL_WIKI_URL)
    pages = asyncio.run(pages_result) if asyncio.iscoroutine(pages_result) else pages_result
    embedded_pages = 0

    for url, markdown in pages:
        source_name = _source_name(url)
        markdown = _clean_markdown(markdown)
        markdown_path = _save_markdown(markdown, source_name, markdown_dir)
        chunks = chunk_markdown(markdown)
        if not chunks:
            continue

        for chunk in chunks:
            persist_document(
                collection=collection,
                source_path=Path(url),
                text=chunk.text,
                section_ref=chunk.section_ref,
                chunk_index=chunk.chunk_index,
            )

        _backup_markdown(markdown_path, backup_dir / "markdown")
        embedded_pages += 1

    print(f"Embedded {embedded_pages} page(s).")
    return embedded_pages


if __name__ == "__main__":
    run_manual_ingest()
