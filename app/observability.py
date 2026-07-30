from __future__ import annotations

import os


def setup_observability() -> None:
    try:
        import langwatch
    except ImportError:
        return

    if not os.getenv("LANGWATCH_API_KEY"):
        return
    langwatch.setup(
        api_key=os.getenv("LANGWATCH_API_KEY"),
        project_id=os.getenv("LANGWATCH_PROJECT_ID") or os.getenv("LANGWATCH_PROJECT"),
        endpoint_url=os.getenv("LANGWATCH_ENDPOINT"),
        disable_sending=False,
    )


def trace_chat(name: str = "rag-chat"):
    try:
        import langwatch
    except ImportError:
        from contextlib import nullcontext

        return nullcontext()

    return langwatch.trace(name=name)
