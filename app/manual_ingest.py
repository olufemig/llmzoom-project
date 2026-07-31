from __future__ import annotations

import asyncio
import re
import urllib.parse
from pathlib import Path

import certifi
import requests

from app.config import CHROMA_DIR, MARKDOWN_DIR
from app.embeddings import get_embedding_model
from app.ingest import chunk_markdown
from app.vectorstore.chroma import get_client, get_collection, persist_document


ARSENAL_WIKI_URL = "https://en.wikipedia.org/wiki/Arsenal_F.C."
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
REQUEST_HEADERS = {
    "User-Agent": "rag-project1/0.1.0 (https://en.wikipedia.org/wiki/Arsenal_F.C.)"
}
IMAGE_MARKDOWN_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
IMAGE_REF_RE = re.compile(r"^\s*\[[^\]]+\]:\s+\S+\s*$", re.MULTILINE)
IMAGE_HTML_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)


def _source_name(url: str) -> str:
    tail = url.rstrip("/").rsplit("/", 1)[-1] or "arsenal-fc"
    return tail.replace("?", "_").replace("&", "_")


def _extract_page_title(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.unquote(parsed.path.rsplit("/", 1)[-1] or "Arsenal_F.C.")


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


def _fetch_mediawiki_page(title: str) -> tuple[str, str]:
    params = {
        "action": "parse",
        "page": title,
        "prop": "wikitext",
        "format": "json",
        "formatversion": "2",
    }
    url = f"{WIKIPEDIA_API_URL}?{urllib.parse.urlencode(params)}"
    try:
        response = requests.get(
            url,
            timeout=60,
            verify=certifi.where(),
            headers=REQUEST_HEADERS,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise RuntimeError("MediaWiki fetch failed. Check HTTPS, certs, or User-Agent.") from exc

    wikitext = data.get("parse", {}).get("wikitext", "")
    return f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title)}", wikitext


def _wikitext_to_markdown(wikitext: str) -> str:
    lines: list[str] = []
    for line in wikitext.splitlines():
        line = re.sub(r"'''''(.*?)'''''", r"### \1", line)
        line = re.sub(r"'''(.*?)'''", r"**\1**", line)
        line = re.sub(r"''(.*?)''", r"*\1*", line)
        line = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]", r"\1", line)
        line = re.sub(r"\{\{[^{}]*\}\}", "", line)
        line = re.sub(r"^\*+\s*", "- ", line)
        lines.append(line)
    return "\n".join(lines)


def _save_markdown(markdown: str, source_name: str, markdown_dir: Path) -> Path:
    markdown_dir.mkdir(parents=True, exist_ok=True)
    target = markdown_dir / f"{source_name}.md"
    target.write_text(markdown, encoding="utf-8")
    return target


def _delete_markdown_files(markdown_dir: Path) -> None:
    if not markdown_dir.exists():
        return

    for path in markdown_dir.glob("*.md"):
        path.unlink()


def _existing_collections() -> list[str]:
    if not CHROMA_DIR.exists():
        return []

    client = get_client()
    try:
        collections = client.list_collections()
        return [collection.name for collection in collections]
    except Exception:
        return []


def _page_markdown(result) -> str:
    markdown = getattr(result, "markdown", None)
    if markdown and getattr(markdown, "raw_markdown", None):
        return markdown.raw_markdown
    return getattr(result, "clean_markdown", None) or getattr(result, "text", None) or ""


async def _crawl_pages(start_url: str) -> list[tuple[str, str]]:
    title = _extract_page_title(start_url)
    url, wikitext = _fetch_mediawiki_page(title)
    markdown = _wikitext_to_markdown(wikitext)
    return [(url, markdown)] if markdown else []


def run_manual_ingest(markdown_dir: Path = MARKDOWN_DIR) -> int:
    collections = _existing_collections()
    if collections:
        print(f"Chroma collection exists ({', '.join(collections)}). Abort ingest.")
        return 0

    collection = get_collection()
    embed_model = get_embedding_model()
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
            embedding = embed_model.get_text_embedding(chunk.text)
            persist_document(
                collection=collection,
                source_path=Path(url),
                text=chunk.text,
                source_title=source_name,
                source_url=url,
                section_ref=chunk.section_ref,
                chunk_index=chunk.chunk_index,
                embedding=embedding,
            )
        embedded_pages += 1

    _delete_markdown_files(markdown_dir)

    print(f"Embedded {embedded_pages} page(s).")
    return embedded_pages


if __name__ == "__main__":
    run_manual_ingest()
