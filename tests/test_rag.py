from app import rag
from app.rag import answer_question, build_context


def test_answer_question_returns_sources():
    class DummyCollection:
        def query(self, **kwargs):
            return {
                "documents": [["doc 1"]],
                "metadatas": [[{"section_ref": "Section 1"}]],
            }

    rag.synthesize_answer = lambda question, context: "answer"
    answer, sources = answer_question("What is this?", collection=DummyCollection())
    assert answer
    assert sources[0].section_ref == "Section 1"


def test_answer_question_no_sources_skips_llm(monkeypatch):
    monkeypatch.setattr(rag, "trace_chat", lambda: __import__("contextlib").nullcontext())
    called = {"value": False}

    def fake_synthesize_answer(question, context):
        called["value"] = True
        return "answer"

    monkeypatch.setattr(rag, "synthesize_answer", fake_synthesize_answer)

    class EmptyCollection:
        def query(self, **kwargs):
            return {"documents": [[]], "metadatas": [[]]}

    answer, sources = answer_question("What is this?", collection=EmptyCollection())
    assert answer == "No indexed sources found."
    assert sources == []
    assert called["value"] is False


def test_build_context_formats_sections():
    class Chunk:
        def __init__(self, text, section_ref):
            self.text = text
            self.section_ref = section_ref

    context = build_context([Chunk("text", "Intro")])
    assert "Intro" in context
