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


def test_live_benchmark_repository_set_has_repeatable_expectations() -> None:
    root = Path(__file__).resolve().parents[4]
    repositories = json.loads((root / "examples" / "live-benchmarks" / "repositories.json").read_text(encoding="utf-8"))

    assert len(repositories) >= 3
    assert all("/" in item["repo"] for item in repositories)
    assert all(item["workspace_slug"].startswith("github-") for item in repositories)
    assert all(item["expectations"]["minimum_candidate_decisions"] >= 0 for item in repositories)
    assert all(item["expectations"]["expected_outcomes"] for item in repositories)
