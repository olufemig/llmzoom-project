## RAG Project

This is a Streamlit RAG app for Arsenal FC , built from data extracted from the wiki page for Arsenal FC. https://en.wikipedia.org/wiki/Arsenal_F.C.

I have followed this club for years and is a favorite of mine and my family. It is a simple dedicated way to find information about the club, ask questions and get answers.

The RAG Application has been deployed to the cloud and can be tested live at ;  
 

[https://rag.tokenreaper.com/](https://rag.tokenreaper.com/)


## Retrieval Flow

1.  `app.manual_ingest` fetches Arsenal FC page via MediaWiki API.
2.  Markdown is cleaned, refs/images removed, and text is chunked with SemanticSplitter
3.  Chunks are embedded and stored in local ChromaDB.
4.  `app.rag.answer_question()` builds LlamaIndex `VectorStoreIndex` over ChromaDB.
5.  Streamlit `app.ui.run_app()` calls retrieval + LLM and renders answer with source excerpts.

## Retrieval Evaluation

This has been done using Langwatch. Query output was by semantic search and results were reranked

## LLM Evaluation

LLM response path uses OpenRouter through `llama-index-llms-openai-like`.  
Answer prompt: answer only from retrieved context, do not guess and return a citation block.

## Interface

*   Streamlit single-screen chat UI
*   Source excerpts shown in expanders under answer
*   App entrypoint: `uv run streamlit run main.py`

## Ingestion Pipeline

I created a Manual ingest script that can be scheduled. ideally i could have done this using Prefect, Airflow or a cron job. Waht this script does is extract the data from the wiki page to markdown, cleans and removes all HTML tags, chunks the data and embeds the vector represenation into Chromadb. All initial chromadb collections are dropped before successful ingestion.

```plaintext
uv run python -m app.manual_ingest
```

Behavior:

*   fetch `https://en.wikipedia.org/wiki/Arsenal_F.C.` through MediaWiki API
*   clean markdown, strip images and refs
*   save markdown only during ingest
*   embed chunks into ChromaDB
*   delete markdown files after ingest
*   wipe local `chromadb/` first if present

## Monitoring

*   LangWatch attaches only when `LANGWATCH_API_KEY` is set
*   `app.observability.setup_observability()` runs before LlamaIndex imports
*   warning about existing global tracer provider is suppressed

## Containerization

Application is deployed to a cloud VPS using Coolify. The Dockerfile was used to create a Dockerfile and Base image: `python:3.13-slim`

Run container:

```plaintext
uv run streamlit run main.py
```

## Reproducibility

*   Python `&gt;=3.13`
*   `uv sync` installs locked deps from `uv.lock`
*   workspace temp wrapper used for pytest on Windows

## Best Practices

*   Keep `.env` for secrets:
    *   `OPENROUTER_API_KEY`
    *   optional `OPENROUTER_MODEL`
    *   optional `OPENROUTER_BASE_URL`
    *   optional `LANGWATCH_API_KEY`
    *   optional `LANGWATCH_ENDPOINT`

## Run

```plaintext
uv sync
uv run python -m app.manual_ingest
uv run streamlit run main.py
```

## Testing

```plaintext
uv run pytest --basetemp=tmp
```

On Windows, use `./scripts/test.ps1` if temp/cache permissions fail.

## Project Structure

*   `main.py` Streamlit entrypoint
*   `app/manual_ingest.py` ingest pipeline
*   `app/rag.py` retrieval + LLM query engine
*   `app/ui.py` Streamlit UI
*   `app/vectorstore/chroma.py` Chroma helpers
*   `app/observability.py` LangWatch wiring
*   `docs/eval-schema.md` eval JSON shape
*   `scripts/test.ps1` and `scripts/test.sh` Windows/Linux pytest wrappers

## Technical Stack

*   Python 3.13
*   Streamlit
*   LlamaIndex
*   ChromaDB
*   OpenRouter for embeddings and chat LLM
*   LangWatch for optional chat tracing
