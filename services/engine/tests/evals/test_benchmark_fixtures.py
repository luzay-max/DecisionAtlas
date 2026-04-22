from __future__ import annotations

import json
import importlib.util
from pathlib import Path


def _load_benchmark_module():
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / "run_benchmark.py"
    spec = importlib.util.spec_from_file_location("run_benchmark", module_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


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
    assert all(item["expectations"].get("minimum_reviewable_candidates", 0) >= 0 for item in repositories)
    assert all(item["expectations"].get("minimum_screened_in_artifacts", 0) >= 0 for item in repositories)
    assert all(item["expectations"]["expected_outcomes"] for item in repositories)
    assert all(item["expectations"]["expected_readiness_states"] for item in repositories)
    assert all(item["expectations"]["expected_why_states"] for item in repositories)
    assert all(item["expectations"]["expected_drift_states"] for item in repositories)
    assert next(item for item in repositories if item["id"] == "n8n")["expectations"]["minimum_reviewable_candidates"] == 1

    benchmark = _load_benchmark_module()
    assert benchmark.validate_live_repo_set(repositories) == 0
    malformed_repository = dict(repositories[0])
    malformed_repository["repo"] = "invalid"
    assert benchmark.validate_live_repo_set([malformed_repository]) == 1


def test_live_benchmark_why_cases_have_repeatable_expectations() -> None:
    root = Path(__file__).resolve().parents[4]
    repositories = json.loads((root / "examples" / "live-benchmarks" / "repositories.json").read_text(encoding="utf-8"))
    why_cases = json.loads((root / "examples" / "live-benchmarks" / "why-cases.json").read_text(encoding="utf-8"))

    assert any(item["repo_id"] == "browser-use" for item in why_cases)
    assert all(item["workspace_slug"].startswith("github-") for item in why_cases)
    assert all(item["question"].strip() for item in why_cases)
    assert all(item["expected_status"] for item in why_cases)
    assert all(item["expected_terms"] for item in why_cases)
    assert all(item["min_citations"] >= 1 for item in why_cases)

    benchmark = _load_benchmark_module()
    assert benchmark.validate_why_cases(why_cases, repositories) == 0
    malformed_case = dict(why_cases[0])
    malformed_case["repo_id"] = "missing-repo"
    assert benchmark.validate_why_cases([malformed_case], repositories) == 1


def test_live_benchmark_drift_cases_have_repeatable_expectations() -> None:
    root = Path(__file__).resolve().parents[4]
    repositories = json.loads((root / "examples" / "live-benchmarks" / "repositories.json").read_text(encoding="utf-8"))
    drift_cases = json.loads((root / "examples" / "live-benchmarks" / "drift-cases.json").read_text(encoding="utf-8"))

    assert any(item["repo_id"] == "browser-use" for item in drift_cases)
    assert all(item["workspace_slug"].startswith("github-") for item in drift_cases)
    assert all(item["artifact_title_pattern"].strip() for item in drift_cases)
    assert all(item["accepted_decision_title"].strip() for item in drift_cases)
    assert all("possible_supersession" in item["forbidden_alert_types"] for item in drift_cases)
    assert all(item["allowed_outcomes"] for item in drift_cases)

    benchmark = _load_benchmark_module()
    assert benchmark.validate_drift_cases(drift_cases, repositories) == 0
    malformed_case = dict(drift_cases[0])
    malformed_case["forbidden_alert_types"] = []
    assert benchmark.validate_drift_cases([malformed_case], repositories) == 1
