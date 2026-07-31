from __future__ import annotations

import os
from functools import lru_cache


@lru_cache(maxsize=1)
def get_embedding_model():
    from llama_index.embeddings.openai import OpenAIEmbedding

    return OpenAIEmbedding(
        model=os.getenv("OPENROUTER_EMBEDDING_MODEL", "text-embedding-3-small"),
        api_base=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=os.environ["OPENROUTER_API_KEY"],
    )
