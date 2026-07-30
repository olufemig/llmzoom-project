from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from app.config import ROOT


STATE_FILE = ROOT / "ingest_state.json"
Status = Literal["queued", "running", "succeeded", "failed"]


@dataclass(frozen=True)
class IngestJobState:
    status: Status
    filename: str
    chunks: int | None = None
    message: str | None = None
    run_id: str | None = None


def save_state(state: IngestJobState, state_file: Path = STATE_FILE) -> None:
    state_file.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")


def load_state(state_file: Path = STATE_FILE) -> IngestJobState | None:
    if not state_file.exists():
        return None
    data = json.loads(state_file.read_text(encoding="utf-8"))
    return IngestJobState(**data)
