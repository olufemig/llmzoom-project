from app.config import CHROMA_DIR, DATA_DIR


def test_default_paths_exist_as_paths():
    assert DATA_DIR.name == "data"
    assert CHROMA_DIR.name == "chromadb"
