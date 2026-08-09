from __future__ import annotations

import re
from dataclasses import dataclass

from llama_index.core import Document
from llama_index.core.node_parser import SemanticSplitterNodeParser, SentenceSplitter

from app.embeddings import get_embedding_model


@dataclass(frozen=True)
class IngestedChunk:
    text: str
    section_ref: str
    chunk_index: int


REF_TAG_RE = re.compile(r"<ref\b[^>]*/?>.*?</ref>|<ref\b[^>]*/?>", re.IGNORECASE | re.DOTALL)


def strip_refs(text: str) -> str:
    return REF_TAG_RE.sub("", text)


def chunk_markdown(markdown: str) -> list[IngestedChunk]:
    chunks: list[IngestedChunk] = []
    current_section = "Unknown section"
    buffer: list[str] = []
    try:
        splitter = SemanticSplitterNodeParser.from_defaults(
            embed_model=get_embedding_model(),
            buffer_size=1,
            breakpoint_percentile_threshold=95,
        )
        semantic = True
    except Exception:
        splitter = SentenceSplitter(chunk_size=512, chunk_overlap=75)
        semantic = False

    def flush() -> None:
        paragraph: list[str] = []
        for line in buffer:
            if line.strip():
                paragraph.append(line)
            elif paragraph:
                chunks.append(
                    IngestedChunk(
                        text="\n".join(paragraph).strip(),
                        section_ref=current_section,
                        chunk_index=len(chunks),
                    )
                )
                paragraph.clear()
        if paragraph:
            paragraph_text = "\n".join(paragraph).strip()
            if semantic:
                nodes = splitter.get_nodes_from_documents([Document(text=paragraph_text)])
                split_texts = [node.get_content() for node in nodes]
            else:
                split_texts = splitter.split_text(paragraph_text)
            for split_text in split_texts:
                chunks.append(
                    IngestedChunk(
                        text=split_text.strip(),
                        section_ref=current_section,
                        chunk_index=len(chunks),
                    )
                )
        buffer.clear()

    for line in markdown.splitlines():
        if line.startswith("#"):
            flush()
            current_section = line.lstrip("#").strip() or "Unknown section"
            continue
        if line.strip():
            buffer.append(line)
        elif buffer and buffer[-1].strip():
            buffer.append("")

    flush()
    return [chunk for chunk in chunks if chunk.text]
