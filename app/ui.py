import streamlit as st
from pathlib import Path

from app.config import DATA_DIR
from app.ingest import ensure_data_dir, ingest_pdf, list_pdfs
from app.rag import answer_question


def _save_upload(uploaded_file, data_dir: Path) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    target = data_dir / uploaded_file.name
    target.write_bytes(uploaded_file.getbuffer())
    return target


def _render_sources(sources) -> None:
    for index, source in enumerate(sources, start=1):
        with st.expander(f"Source {index}: {source.section_ref}"):
            st.write(source.text)


def run_app() -> None:
    st.set_page_config(page_title="RAG Manuals", layout="wide")
    st.title("Product Manual RAG")
    st.caption(f"Watching PDFs in {DATA_DIR}")

    ensure_data_dir(DATA_DIR)

    uploaded_file = st.file_uploader("Upload PDF manual", type=["pdf"])
    if uploaded_file and st.button("Ingest"):
        pdf_path = _save_upload(uploaded_file, DATA_DIR)
        with st.spinner("Indexing manual..."):
            chunks = ingest_pdf(pdf_path)
        st.success(f"Indexed {uploaded_file.name} with {chunks} chunks.")

    indexed = list_pdfs(DATA_DIR)
    st.metric("Indexed PDFs", len(indexed))

    question = st.chat_input("Ask about product manuals")
    if question:
        answer, sources = answer_question(question)
        st.chat_message("assistant").write(answer)
        _render_sources(sources)
