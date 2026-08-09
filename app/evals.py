from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from app.config import EVAL_CANDIDATES_FILE


VALID_STATUSES = {"pending", "approved", "rejected"}


@dataclass(frozen=True)
class EvalCase:
    id: str
    status: str
    question: str
    expected_answer: str
    expected_context: str
    expected_section: str
    source_title: str
    source_url: str

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid eval status: {self.status}")


def load_eval_cases(path: Path = EVAL_CANDIDATES_FILE) -> list[EvalCase]:
    if not path.exists():
        return []

    data = json.loads(path.read_text(encoding="utf-8"))
    return [EvalCase(**item) for item in data]


def save_eval_cases(cases: list[EvalCase], path: Path = EVAL_CANDIDATES_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(case) for case in cases]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def update_eval_case_status(cases: list[EvalCase], case_id: str, status: str) -> list[EvalCase]:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid eval status: {status}")

    updated: list[EvalCase] = []
    for case in cases:
        if case.id == case_id:
            updated.append(EvalCase(**{**asdict(case), "status": status}))
        else:
            updated.append(case)
    return updated
