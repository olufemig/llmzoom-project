import streamlit as st

from app.rag import answer_question


def _render_sources(sources) -> None:
    for index, source in enumerate(sources, start=1):
        with st.expander(f"Source {index}: {source.source_title} — {source.section_ref}"):
            st.caption(source.source_url)
            st.write(source.text)


def run_app() -> None:
    st.set_page_config(page_title="Arsenal FC RAG ", layout="wide")
    st.title("Arsenal FC Wiki RAG")
    st.caption("Arsenal FC wiki has been ingested, you can now chat on this screen.")

    question = st.chat_input("Ask a question about Arsenal FC")
    result_slot = st.container()

    if question:
        with result_slot:
            with st.spinner("Generating response..."):
                answer, sources = answer_question(question)

        with result_slot:
            st.chat_message("assistant").write(answer)
            _render_sources(sources)
