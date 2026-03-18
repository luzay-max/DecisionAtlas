from __future__ import annotations

import json
from pathlib import Path


def test_benchmark_fixtures_have_matching_ids_and_citation_targets() -> None:
    root = Path(__file__).resolve().parents[4]
    queries = json.loads((root / "examples" / "demo-workspace" / "queries.json").read_text(encoding="utf-8"))
    expected_answers = json.loads(
        (root / "examples" / "demo-workspace" / "expected-answers.json").read_text(encoding="utf-8")
    )

    assert [item["id"] for item in queries] == [item["id"] for item in expected_answers]
    assert all(item["question"].strip() for item in queries)
    assert all(item["min_citations"] >= 1 for item in expected_answers)
