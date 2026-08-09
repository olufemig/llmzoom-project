from app.evals import EvalCase, save_eval_cases, load_eval_cases, update_eval_case_status


def test_eval_case_roundtrip(tmp_path):
    path = tmp_path / "candidates.json"
    cases = [
        EvalCase(
            id="arsenal-001",
            status="pending",
            question="When was Arsenal founded?",
            expected_answer="1886",
            expected_context="Arsenal Football Club was founded in 1886.",
            expected_section="History",
            source_title="Arsenal_F.C.",
            source_url="https://en.wikipedia.org/wiki/Arsenal_F.C.",
        )
    ]

    save_eval_cases(cases, path)
    loaded = load_eval_cases(path)

    assert loaded == cases


def test_update_eval_case_status():
    case = EvalCase(
        id="arsenal-001",
        status="pending",
        question="When was Arsenal founded?",
        expected_answer="1886",
        expected_context="Arsenal Football Club was founded in 1886.",
        expected_section="History",
        source_title="Arsenal_F.C.",
        source_url="https://en.wikipedia.org/wiki/Arsenal_F.C.",
    )

    updated = update_eval_case_status([case], "arsenal-001", "approved")

    assert updated[0].status == "approved"
