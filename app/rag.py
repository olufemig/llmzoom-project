from __future__ import annotations

from dataclasses import dataclass

from app.sources import SourceExcerpt
from app.observability import trace_chat
from app.vectorstore.chroma import get_collection


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    section_ref: str


def retrieve_chunks(question: str, *, collection=None, top_k: int = 3) -> list[RetrievedChunk]:
    collection = collection or get_collection()
    result = collection.query(query_texts=[question], n_results=top_k)
    chunks: list[RetrievedChunk] = []

    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]

    for document, metadata in zip(documents, metadatas, strict=False):
        chunks.append(
            RetrievedChunk(
                text=document,
                section_ref=(metadata or {}).get("section_ref", "Unknown section"),
            )
        )
    return chunks


def build_context(chunks: list[RetrievedChunk]) -> str:
    return "\n\n".join(
        f"[{index + 1}] {chunk.section_ref}\n{chunk.text}"
        for index, chunk in enumerate(chunks)
    )


def synthesize_answer(question: str, context: str) -> str:
    from llama_index.llms.openai import OpenAI
    import os

    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    api_key = os.getenv("OPENROUTER_API_KEY")
    llm = OpenAI(model=model, api_key=api_key, api_base=base_url)
    prompt = (
        "Answer question using only context. If context lacks answer, say so.\n\n"
        f"Question:\n{question}\n\nContext:\n{context}"
    )
    response = llm.complete(prompt)
    return getattr(response, "text", str(response))


def answer_question(question: str, *, collection=None) -> tuple[str, list[SourceExcerpt]]:
    chunks = retrieve_chunks(question, collection=collection)
    context = build_context(chunks)
    with trace_chat():
        answer = synthesize_answer(question, context) if context else "No indexed sources found."
    sources = [SourceExcerpt(text=chunk.text, section_ref=chunk.section_ref) for chunk in chunks]
    return answer, sources
