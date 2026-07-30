from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "data"))
CHROMA_DIR = Path(os.getenv("CHROMA_PATH", ROOT / "chromadb"))
