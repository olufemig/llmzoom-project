import streamlit as st

from app.config import DATA_DIR


def run_app() -> None:
    st.set_page_config(page_title="RAG Manuals", layout="wide")
    st.title("Product Manual RAG")
    st.caption(f"Watching PDFs in {DATA_DIR}")
    st.info("UI scaffold ready. Ingestion and chat wiring comes next.")
