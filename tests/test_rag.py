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


def test_build_context_formats_sections():
    class Chunk:
        def __init__(self, text, section_ref):
            self.text = text
            self.section_ref = section_ref

    context = build_context([Chunk("text", "Intro")])
    assert "Intro" in context
