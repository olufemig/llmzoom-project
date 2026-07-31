# AGENTS.md

- Repo is Python app. Main entrypoint: `main.py`.
- Python target: `>=3.13` from `pyproject.toml`; `.python-version` is present, so honor repo-pinned interpreter when running tools.
- `README.md` is empty, so treat source files and manifests as source of truth.
- App goal: small RAG app for Arsenal FC wiki pages.
- Use `llamaindex` for markdown ingest, retrieval, and chat LLM calls.
- Use MediaWiki API for Arsenal FC wiki ingest, then save markdown into `markdown/` only while ingest runs and delete markdown files after ingestion.
- Use local `ChromaDB` for persisted embeddings/vectors.
- Chat retrieval should use LlamaIndex query engine over ChromaDB.
- Use OpenRouter for LLMs.
- Keep secrets/config in `.env`.
- Ingestion stays a single plain Python script.
- Streamlit UI shows crawl ingest status and chat stays on same screen.
- Manual ingest script fetches `https://en.wikipedia.org/wiki/Arsenal_F.C.` via MediaWiki API, cleans images/whitespace, chunks with `SentenceSplitter(chunk_size=512, chunk_overlap=75)`, embeds chunks into ChromaDB, writes page count, then deletes markdown files.
- Source excerpts should include section refs.
- LangWatch only wraps chat LLM response path.
- Use `uv sync` and `uv run` for env/deps; keep tests minimal and code minimal.
- Full ingest Docker image uses `python:3.13-slim`.
