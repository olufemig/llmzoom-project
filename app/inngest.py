from __future__ import annotations

import os
from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class InngestTriggerResult:
    run_id: str | None
    raw: dict


def trigger_ingest_event(payload: dict) -> InngestTriggerResult:
    url = os.getenv("INNGEST_EVENT_URL", "https://api.inngest.com/v1/events")
    key = os.getenv("INNGEST_EVENT_KEY")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json() if response.content else {}
    return InngestTriggerResult(run_id=data.get("run_id") or data.get("id"), raw=data)
