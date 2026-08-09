# Eval Schema

`data/evals/candidates.json` stores one JSON array of cases.

Each case:

```json
{
  "id": "arsenal-founded-001",
  "status": "pending",
  "question": "When was Arsenal founded?",
  "expected_answer": "1886",
  "expected_context": "Arsenal Football Club was founded in 1886.",
  "expected_section": "History",
  "source_title": "Arsenal_F.C.",
  "source_url": "https://en.wikipedia.org/wiki/Arsenal_F.C."
}
```

Status values:

- `pending`
- `approved`
- `rejected`

Use `uv run python -m app.eval_review` to update status.
Use `uv run python -m app.eval_run` to score `approved` cases.
