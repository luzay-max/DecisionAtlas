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
    assert all(item["expectations"].get("minimum_accepted_decisions", 0) >= 0 for item in repositories)
    assert all(item["expectations"].get("minimum_screened_in_artifacts", 0) >= 0 for item in repositories)
    assert all(item["expectations"]["expected_outcomes"] for item in repositories)
    assert all(item["expectations"]["expected_readiness_states"] for item in repositories)
    assert all(item["expectations"]["expected_why_states"] for item in repositories)
    assert all(item["expectations"]["expected_drift_states"] for item in repositories)
    assert next(item for item in repositories if item["id"] == "n8n")["expectations"]["minimum_reviewable_candidates"] == 1
    assert next(item for item in repositories if item["id"] == "browser-use")["expectations"]["minimum_accepted_decisions"] == 1
    assert next(item for item in repositories if item["id"] == "rich")["expectations"][
        "expected_why_states_after_first_acceptance"
    ] == ["ready", "evidence_limited"]

    benchmark = _load_benchmark_module()
    assert benchmark.validate_live_repo_set(repositories) == 0
    malformed_repository = dict(repositories[0])
    malformed_repository["repo"] = "invalid"
    assert benchmark.validate_live_repo_set([malformed_repository]) == 1
    malformed_repository = dict(repositories[-1])
    malformed_repository["expectations"] = dict(repositories[-1]["expectations"])
    malformed_repository["expectations"]["minimum_accepted_decisions"] = 1
    malformed_repository["expectations"]["expected_why_states_after_first_acceptance"] = []
    assert benchmark.validate_live_repo_set([malformed_repository]) == 1


def test_live_benchmark_why_cases_have_repeatable_expectations() -> None:
    root = Path(__file__).resolve().parents[4]
    repositories = json.loads((root / "examples" / "live-benchmarks" / "repositories.json").read_text(encoding="utf-8"))
    why_cases = json.loads((root / "examples" / "live-benchmarks" / "why-cases.json").read_text(encoding="utf-8"))

    assert len(why_cases) >= 3
    assert any(item["repo_id"] == "browser-use" for item in why_cases)
    assert any(item["id"] == "browser-use-http-download-status-equivalent-phrasing" for item in why_cases)
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


def test_live_dashboard_payload_evaluates_broad_readiness_expectations() -> None:
    benchmark = _load_benchmark_module()
    repository = {
        "id": "repo",
        "repo": "org/repo",
        "workspace_slug": "github-org-repo",
        "expectations": {
            "minimum_candidate_decisions": 2,
            "minimum_reviewable_candidates": 1,
            "minimum_accepted_decisions": 1,
            "minimum_screened_in_artifacts": 3,
            "expected_readiness_states": ["why_ready"],
            "expected_why_states": ["ready", "evidence_limited"],
            "expected_drift_states": ["unevaluated", "clean"],
        },
    }
    payload = {
        "workspace_mode": "imported",
        "import_status": "succeeded",
        "decision_counts": {"candidate": 1, "accepted": 1, "rejected": 0, "superseded": 0},
        "workspace_readiness": {
            "state": "why_ready",
            "review_state": "review_complete",
            "why_state": "ready",
            "next_action": "ask_why",
            "recommended_actions": ["ask_why", "evaluate_drift"],
        },
        "drift_status": {"state": "unevaluated"},
        "latest_import": {
            "summary": {
                "extraction_summary": {
                    "screened_in_artifacts": 3,
                    "created_candidates": 1,
                }
            }
        },
    }

    passed, row = benchmark._evaluate_dashboard_payload(repository, payload)

    assert passed is True
    assert row["bounded_outcome"] == "why_ready"
    assert row["candidate_decision_count"] == 1
    assert row["accepted_decision_count"] == 1
    assert row["screened_in_artifact_count"] == 3


def test_live_real_repo_validation_writes_missing_workspace_report(tmp_path, monkeypatch) -> None:
    benchmark = _load_benchmark_module()
    repository = {
        "id": "repo",
        "repo": "org/repo",
        "workspace_slug": "github-org-repo",
        "expectations": {
            "expected_readiness_states": ["review_ready"],
            "expected_why_states": ["review_required"],
            "expected_drift_states": ["review_required"],
        },
    }

    def fake_request(**kwargs):
        return None, {"type": "http_error", "status": 404, "detail": "not found"}

    monkeypatch.setattr(benchmark, "_json_request", fake_request)
    report_path = tmp_path / "report.json"

    status = benchmark.run_live_real_repo_validation(
        base_url="http://127.0.0.1:3001",
        repositories=[repository],
        why_cases=[],
        drift_cases=[],
        report_path=report_path,
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert status == 1
    assert report["repositories"][0]["bounded_outcome"] == "missing_workspace"
    assert report["summary"] == {"repositories": 1, "passed": 0, "failed": 1}


def test_live_real_repo_validation_reports_dashboard_why_and_drift(tmp_path, monkeypatch) -> None:
    benchmark = _load_benchmark_module()
    repository = {
        "id": "repo",
        "repo": "org/repo",
        "workspace_slug": "github-org-repo",
        "expectations": {
            "minimum_candidate_decisions": 1,
            "minimum_reviewable_candidates": 1,
            "expected_readiness_states": ["review_ready"],
            "expected_why_states": ["review_required"],
            "expected_drift_states": ["review_required"],
        },
    }
    why_case = {
        "id": "why-case",
        "repo_id": "repo",
        "repo": "org/repo",
        "workspace_slug": "github-org-repo",
        "question": "why use queue",
        "expected_status": "review_required",
        "expected_terms": ["review"],
        "min_citations": 1,
    }
    drift_case = {
        "id": "drift-case",
        "repo_id": "repo",
        "repo": "org/repo",
        "workspace_slug": "github-org-repo",
        "artifact_title_pattern": "dangerous replacement",
        "accepted_decision_title": "Use queue",
        "forbidden_alert_types": ["possible_supersession"],
        "allowed_outcomes": ["none"],
    }

    def fake_request(**kwargs):
        path = kwargs["path"]
        if path.startswith("/dashboard/summary"):
            return {
                "workspace_mode": "imported",
                "import_status": "succeeded",
                "decision_counts": {"candidate": 1, "accepted": 0, "rejected": 0, "superseded": 0},
                "workspace_readiness": {
                    "state": "review_ready",
                    "review_state": "review_ready",
                    "why_state": "review_required",
                    "next_action": "review_candidates",
                    "recommended_actions": ["review_candidates"],
                },
                "drift_status": {"state": "review_required"},
                "latest_import": {"summary": {"extraction_summary": {"screened_in_artifacts": 1}}},
            }, None
        if path == "/query/why":
            return {
                "status": "review_required",
                "answer": "Review one candidate before using why-search.",
                "citations": [{"id": 1}],
                "answer_context": {"workspace_readiness": {"state": "review_ready"}},
            }, None
        if path.startswith("/drift"):
            return {"evaluation": {"state": "review_required"}, "alerts": []}, None
        raise AssertionError(path)

    monkeypatch.setattr(benchmark, "_json_request", fake_request)
    report_path = tmp_path / "report.json"

    status = benchmark.run_live_real_repo_validation(
        base_url="http://127.0.0.1:3001",
        repositories=[repository],
        why_cases=[why_case],
        drift_cases=[drift_case],
        report_path=report_path,
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert status == 0
    assert report["repositories"][0]["passed"] is True
    assert report["repositories"][0]["why_cases"][0]["passed"] is True
    assert report["repositories"][0]["drift"]["cases"][0]["passed"] is True
