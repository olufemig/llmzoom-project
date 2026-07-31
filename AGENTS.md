# AGENTS.md

- Repo is Python app. Main entrypoint: `main.py`.
- Python target: `>=3.13` from `pyproject.toml`; `.python-version` is present, so honor repo-pinned interpreter when running tools.
- `README.md` is empty, so treat source files and manifests as source of truth.
- App goal: small RAG app for Arsenal FC wiki pages.
- Use `llamaindex` for markdown ingest, retrieval, and chat LLM calls.
- Use `crawl4ai` to crawl Arsenal FC wiki, then save markdown into `markdown/` and move into `backup/markdown/` after ingest.
- Use local `ChromaDB` for persisted embeddings/vectors.
- Chat retrieval should use LlamaIndex query engine over ChromaDB.
- Use OpenRouter for LLMs.
- Keep secrets/config in `.env`.
- Ingestion stays a single plain Python script.
- Streamlit UI shows crawl ingest status and chat stays on same screen.
- Manual ingest script crawls `https://en.wikipedia.org/wiki/Arsenal_F.C.` at depth 0, embeds chunks into ChromaDB, writes page count, then moves markdown into `backup/markdown/`.
- Source excerpts should include section refs.
- LangWatch only wraps chat LLM response path.
- Use `uv sync` and `uv run` for env/deps; keep tests minimal and code minimal.
