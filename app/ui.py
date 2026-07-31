import streamlit as st

from app.rag import answer_question


def _render_sources(sources) -> None:
    for index, source in enumerate(sources, start=1):
        with st.expander(f"Source {index}: {source.section_ref}"):
            st.write(source.text)


def run_app() -> None:
    st.set_page_config(page_title="RAG Manuals", layout="wide")
    st.title("Arsenal FC Wiki RAG")
    st.caption("Ingest Arsenal FC wiki from crawl4ai, then chat on same screen.")

    question = st.chat_input("Ask about Arsenal FC wiki")
    result_slot = st.container()

    if question:
        with result_slot:
            with st.spinner("Generating response..."):
                answer, sources = answer_question(question)

        with result_slot:
            st.chat_message("assistant").write(answer)
            _render_sources(sources)
