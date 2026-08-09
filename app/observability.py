import os

from langwatch.client import Client
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor


def setup_observability() -> None:
    if not os.getenv("LANGWATCH_API_KEY"):
        return

    setup_kwargs = {
        "api_key": os.environ["LANGWATCH_API_KEY"],
        "instrumentors": [LlamaIndexInstrumentor()],
        "ignore_global_tracer_provider_override_warning": True,
    }
    endpoint_url = os.getenv("LANGWATCH_ENDPOINT")
    if endpoint_url:
        setup_kwargs["endpoint_url"] = endpoint_url

    Client(**setup_kwargs)
