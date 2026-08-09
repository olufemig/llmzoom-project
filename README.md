# RAG Project

Small RAG app for Arsenal FC wiki pages.

## What It Does

- Ingests Arsenal FC wiki content through MediaWiki API
- Cleans and chunks markdown
- Stores embeddings in local ChromaDB
- Chats on same screen in Streamlit
- Uses LangWatch tracing for LlamaIndex calls when configured
- Generates offline eval cases from chunk text for manual review

## Ingest

Run manual ingest:

```bash
uv run python -m app.manual_ingest
```

Ingest behavior:

- fetches Arsenal FC wiki page
- cleans markdown
- chunks text with LlamaIndex splitter
- embeds chunks into ChromaDB
- saves chunk markdown only during ingest, then deletes markdown files
- seeds eval candidates in `data/evals/candidates.json`

Chunking stays in `app/ingest.py`. Eval case generation stays separate in `app/eval_generate.py`.

When `LANGWATCH_API_KEY` is set, LangWatch traces LlamaIndex calls automatically.

## Files

- `chromadb/` stores persisted vectors
- `data/evals/candidates.json` stores eval cases and status
- `markdown/` exists only during ingest
- `docs/eval-schema.md` shows eval JSON shape

## Env

Set secrets in `.env`:

- `OPENROUTER_API_KEY`
- optional `OPENROUTER_MODEL`
- optional `OPENROUTER_BASE_URL`
- optional `LANGWATCH_API_KEY`
- optional `LANGWATCH_ENDPOINT`

## Tests On Windows

If pytest temp/cache permissions fail, run tests with workspace temp wrapper:

```bash
./scripts/test.ps1
./scripts/test.sh
```

Those scripts set `TMP` and `TEMP` to workspace-local `tmp/` before running pytest.
