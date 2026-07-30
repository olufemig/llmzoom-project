from app.sources import SourceExcerpt


def answer_question(question: str) -> tuple[str, list[SourceExcerpt]]:
    return (
        f"Stub answer for: {question}",
        [SourceExcerpt(text="Example excerpt", section_ref="Section 1")],
    )
