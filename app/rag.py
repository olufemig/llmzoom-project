from __future__ import annotations

import os
from functools import lru_cache

from app.sources import SourceExcerpt


SYSTEM_PROMPT = """
Answer only from the retrieved context.

Do not guess or use outside knowledge.
If the answer is not present in the context, say:
"I do not know based on the indexed sources."
""".strip()


def _source_excerpt(source_node) -> SourceExcerpt:
    node = source_node.node

    return SourceExcerpt(
        text=node.get_content(),
        source_title=node.metadata.get("source_title", "Arsenal F.C."),
        source_url=node.metadata.get("source_url", "https://en.wikipedia.org/wiki/Arsenal_F.C."),
        section_ref=node.metadata.get("section_ref", "Unknown section"),
    )


@lru_cache(maxsize=1)
def _build_query_engine():
    from llama_index.core import VectorStoreIndex
    from llama_index.llms.openai_like import OpenAILike
    from llama_index.vector_stores.chroma import ChromaVectorStore

    from app.embeddings import get_embedding_model
    from app.vectorstore.chroma import get_client

    collection = get_client().get_or_create_collection("manuals")

    vector_store = ChromaVectorStore(
        chroma_collection=collection,
    )

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=get_embedding_model(),
    )

    llm = OpenAILike(
        model=os.getenv(
            "OPENROUTER_MODEL",
            "google/gemma-4-26b-a4b-it:free",
        ),
        api_base=os.getenv(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1",
        ),
        api_key=os.environ["OPENROUTER_API_KEY"],
        is_chat_model=True,
    )

    return index.as_query_engine(
        llm=llm,
        similarity_top_k=3,
        system_prompt=SYSTEM_PROMPT,
    )


def answer_question(
    question: str,
) -> tuple[str, list[SourceExcerpt]]:
    try:
        response = _build_query_engine().query(question)
    except ImportError:
        return "Required RAG packages are not installed.", []
    except KeyError:
        return "OPENROUTER_API_KEY is not configured.", []

    sources = [
        _source_excerpt(source_node)
        for source_node in response.source_nodes
    ]

    if not sources:
        return "No indexed sources found.", []

    source = sources[0]
    citation = f"[1] {source.source_title} — {source.section_ref} ({source.source_url})"
    return f"{response}\n\nSources:\n{citation}", sources[:1]
