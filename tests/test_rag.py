from app.rag import answer_question


def test_answer_question_returns_sources():
    answer, sources = answer_question("What is this?")
    assert answer
    assert sources[0].section_ref
