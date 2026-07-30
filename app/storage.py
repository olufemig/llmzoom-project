from pathlib import Path

from app.config import CHROMA_DIR


def chroma_path() -> Path:
    CHROMA_DIR.mkdir(exist_ok=True)
    return CHROMA_DIR
