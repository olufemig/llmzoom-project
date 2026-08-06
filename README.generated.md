## Arsenal FC RAG

Small Streamlit RAG app for questions about Arsenal FC wiki content.

## What it does

*   Ingests `https://en.wikipedia.org/wiki/Arsenal_F.C.` via MediaWiki API
*   Cleans image markup and whitespace
*   Chunks markdown with LlamaIndex `SentenceSplitter(chunk_size=512, chunk_overlap=75)`
*   Stores embeddings in local ChromaDB
*   Answers from indexed sources only
*   Shows answer and source excerpts on same Streamlit screen

## Stack

*   Python 3.13
*   Streamlit
*   LlamaIndex
*   ChromaDB
*   OpenRouter for embeddings and chat LLM
*   LangWatch for optional chat tracing

## Project Layout

*   `main.py` app entrypoint
*   `app/ui.py` Streamlit UI
*   `app/manual_ingest.py` manual ingest script
*   `app/ingest.py` markdown chunking
*   `app/rag.py` query engine and answer formatting
*   `app/vectorstore/chroma.py` Chroma helpers
*   `app/embeddings.py` embedding model setup
*   `app/observability.py` LangWatch setup
*   `app/config.py` path config
*   `tests/` unit tests

## Requirements

*   Python `&gt;=3.13`
*   `uv`
*   `OPENROUTER_API_KEY`
*   Optional: `OPENROUTER_MODEL`, `OPENROUTER_EMBEDDING_MODEL`, `OPENROUTER_BASE_URL`, `LANGWATCH_API_KEY`, `LANGWATCH_ENDPOINT`, `DATA_DIR`, `CHROMA_PATH`  
      
      
    Interface and UI considerations: i used a Streamlit UI for the chat interface

## Install

```plaintext
uv sync
```

## Run

```plaintext
uv run rag-project1
```

## Ingestion pipeline. 

Manual ingest fetches Arsenal FC wiki page, writes temporary markdown into `markdown/`, embeds chunks into ChromaDB, then deletes markdown files after ingest. This can be scheduled via a cron job, 

```plaintext
uv run python -m app.manual_ingest
```

## Test

```plaintext
uv run pytest
```

## Docker

Full ingest image uses `python:3.13-slim`.

```plaintext
docker build -t rag-project1 .
```

## Notes

*   Chat answers are limited to retrieved context
*   Source excerpts include section refs
*   Keep secrets in `.env`