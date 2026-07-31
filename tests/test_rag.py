import os

from app import rag
from app.rag import SourceExcerpt, answer_question


def test_answer_question_returns_sources(monkeypatch):
    class FakeResponse:
        def __str__(self):
            return "answer"

        source_nodes = [
            type(
                "N",
                (),
                {
                    "node": type(
                        "X",
                        (),
                        {"get_content": lambda self: "doc 1", "metadata": {"section_ref": "Section 1"}},
                    )()
                },
            )()
        ]

    class FakeQueryEngine:
        def query(self, question):
            return FakeResponse()

    monkeypatch.setattr(rag, "_build_query_engine", lambda: FakeQueryEngine())

    answer, sources = answer_question("What is this?")
    assert answer == "answer"
    assert sources[0].section_ref == "Section 1"


def test_answer_question_no_sources_skips_llm(monkeypatch):
    class FakeResponse:
        def __str__(self):
            return "answer"

        source_nodes = []

    class FakeQueryEngine:
        def query(self, question):
            return FakeResponse()

    monkeypatch.setattr(rag, "_build_query_engine", lambda: FakeQueryEngine())
    answer, sources = answer_question("What is this?")
    assert answer == "No indexed sources found."
    assert sources == []


def test_answer_question_missing_openrouter_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(rag, "_build_query_engine", lambda: (_ for _ in ()).throw(KeyError("OPENROUTER_API_KEY")))

    answer, sources = answer_question("What is this?")

    assert answer == "OPENROUTER_API_KEY is not configured."
    assert sources == []


def test_answer_question_missing_packages(monkeypatch):
    monkeypatch.setattr(rag, "_build_query_engine", lambda: (_ for _ in ()).throw(ImportError()))

    answer, sources = answer_question("What is this?")

    assert answer == "Required RAG packages are not installed."
    assert sources == []
