from app.inngest import InngestTriggerResult
from app.job_state import IngestJobState


def test_ingest_job_state_serializes():
    state = IngestJobState(status="queued", filename="manual.pdf")
    assert state.status == "queued"


def test_inngest_result_shape():
    result = InngestTriggerResult(run_id="123", raw={})
    assert result.run_id == "123"
