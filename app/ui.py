import streamlit as st
from pathlib import Path

from app.config import DATA_DIR
from app.ingest import ensure_data_dir, list_pdfs
from app.inngest import trigger_ingest_event
from app.job_state import IngestJobState, load_state, save_state
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
        save_state(IngestJobState(status="queued", filename=uploaded_file.name))
        st.info("Ingest kicked off.")
        try:
            save_state(IngestJobState(status="running", filename=uploaded_file.name))
            result = trigger_ingest_event(
                {"name": "app/pdf.uploaded", "data": {"filename": uploaded_file.name, "path": str(pdf_path)}}
            )
            save_state(IngestJobState(status="running", filename=uploaded_file.name, run_id=result.run_id))
            st.info("Ingest running.")
        except Exception as exc:
            save_state(IngestJobState(status="failed", filename=uploaded_file.name, message=str(exc)))
            st.error(f"Ingest failed to start: {exc}")

    indexed = list_pdfs(DATA_DIR)
    st.metric("Indexed PDFs", len(indexed))

    state = load_state()
    if state:
        if state.status == "queued":
            st.warning(f"{state.filename} queued")
        elif state.status == "running":
            st.info(f"{state.filename} running")
        elif state.status == "succeeded":
            st.success(f"{state.filename} complete ({state.chunks} chunks)")
        elif state.status == "failed":
            st.error(f"{state.filename} failed: {state.message}")

    question = st.chat_input("Ask about product manuals")
    if question:
        answer, sources = answer_question(question)
        st.chat_message("assistant").write(answer)
        _render_sources(sources)
