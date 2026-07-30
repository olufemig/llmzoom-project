from app.inngest import InngestTriggerResult
from app.job_state import IngestJobState, load_state, save_state
from app.inngest import trigger_ingest_event


def test_ingest_job_state_serializes():
    state = IngestJobState(status="queued", filename="manual.pdf")
    assert state.status == "queued"


def test_inngest_result_shape():
    result = InngestTriggerResult(run_id="123", raw={})
    assert result.run_id == "123"


def test_job_state_roundtrip(tmp_path):
    path = tmp_path / "state.json"
    state = IngestJobState(status="running", filename="manual.pdf", run_id="run-1")
    save_state(state, path)
    loaded = load_state(path)
    assert loaded == state


def test_trigger_ingest_event_posts_payload(monkeypatch):
    calls = {}

    class DummyResponse:
        content = b'{"run_id":"abc"}'

        def raise_for_status(self):
            return None

        def json(self):
            return {"run_id": "abc"}

    def fake_post(url, json, headers, timeout):
        calls.update({"url": url, "json": json, "headers": headers, "timeout": timeout})
        return DummyResponse()

    monkeypatch.setattr("app.inngest.requests.post", fake_post)
    result = trigger_ingest_event({"name": "app/pdf.uploaded", "data": {"filename": "manual.pdf"}})

    assert result.run_id == "abc"
    assert calls["json"]["name"] == "app/pdf.uploaded"
