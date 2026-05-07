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
    assert all(item["role"].strip() for item in repositories)
    assert all(item["benchmark_purpose"].strip() for item in repositories)
    assert all(item["expectations"]["expected_value_outcomes"] for item in repositories)
    assert all(item["expectations"]["minimum_candidate_decisions"] >= 0 for item in repositories)
    assert all(item["expectations"].get("minimum_reviewable_candidates", 0) >= 0 for item in repositories)
    assert all(item["expectations"].get("minimum_accepted_decisions", 0) >= 0 for item in repositories)
    assert all(item["expectations"].get("minimum_screened_in_artifacts", 0) >= 0 for item in repositories)
    assert all(isinstance(item["expectations"].get("candidate_quality"), dict) for item in repositories)
    assert all(
        item["expectations"]["candidate_quality"].get("minimum_strong_candidates", 0) >= 0 for item in repositories
    )
    assert all(
        0 <= item["expectations"]["candidate_quality"].get("maximum_thin_candidate_ratio", 1) <= 1
        for item in repositories
    )
    assert all(item["expectations"]["expected_outcomes"] for item in repositories)
    assert all(item["expectations"]["expected_readiness_states"] for item in repositories)
    assert all(item["expectations"]["expected_why_states"] for item in repositories)
    assert all(item["expectations"]["expected_drift_states"] for item in repositories)
    assert next(item for item in repositories if item["id"] == "n8n")["expectations"]["minimum_reviewable_candidates"] == 1
    assert next(item for item in repositories if item["id"] == "n8n")["role"] == "large_typescript_stress_repo"
    assert next(item for item in repositories if item["id"] == "browser-use")["expectations"]["minimum_accepted_decisions"] == 1
    assert next(item for item in repositories if item["id"] == "browser-use")["role"] == "decision_rich_regression_repo"
    assert next(item for item in repositories if item["id"] == "rich")["expectations"][
        "expected_why_states_after_first_acceptance"
    ] == ["ready", "evidence_limited"]

    benchmark = _load_benchmark_module()
    assert benchmark.validate_live_repo_set(repositories) == 0
    malformed_repository = dict(repositories[0])
    malformed_repository["repo"] = "invalid"
    assert benchmark.validate_live_repo_set([malformed_repository]) == 1
    malformed_repository = dict(repositories[0])
    malformed_repository["role"] = ""
    assert benchmark.validate_live_repo_set([malformed_repository]) == 1
    malformed_repository = dict(repositories[0])
    malformed_repository["expectations"] = dict(repositories[0]["expectations"])
    malformed_repository["expectations"]["expected_value_outcomes"] = ["not_a_value_outcome"]
    assert benchmark.validate_live_repo_set([malformed_repository]) == 1
    malformed_repository = dict(repositories[-1])
    malformed_repository["expectations"] = dict(repositories[-1]["expectations"])
    malformed_repository["expectations"]["minimum_accepted_decisions"] = 1
    malformed_repository["expectations"]["expected_why_states_after_first_acceptance"] = []
    assert benchmark.validate_live_repo_set([malformed_repository]) == 1
    malformed_repository = dict(repositories[0])
    malformed_repository["expectations"] = dict(repositories[0]["expectations"])
    malformed_repository["expectations"]["candidate_quality"] = {"maximum_thin_candidate_ratio": 2}
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
    assert all(item.get("expected_primary_title", "").strip() for item in why_cases)

    benchmark = _load_benchmark_module()
    assert benchmark.validate_why_cases(why_cases, repositories) == 0
    malformed_case = dict(why_cases[0])
    malformed_case["repo_id"] = "missing-repo"
    assert benchmark.validate_why_cases([malformed_case], repositories) == 1
    malformed_case = dict(why_cases[0])
    malformed_case["expected_primary_title"] = "   "
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
            "candidate_quality": {
                "minimum_strong_candidates": 1,
                "maximum_thin_candidate_ratio": 0.5,
                "require_provenance": True,
            },
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


def test_candidate_quality_payload_evaluates_report_observations() -> None:
    benchmark = _load_benchmark_module()
    repository = {
        "id": "repo",
        "repo": "org/repo",
        "workspace_slug": "github-org-repo",
        "expectations": {
            "candidate_quality": {
                "minimum_strong_candidates": 1,
                "maximum_thin_candidate_ratio": 0.5,
                "require_provenance": True,
            }
        },
    }
    candidates = [
        {
            "candidate_quality": {
                "label": "strong",
                "source_ref_count": 2,
                "previewable_source_ref_count": 2,
                "has_primary_artifact": True,
                "has_source_url": True,
                "confidence_bucket": "high",
                "reasons": [
                    "multiple_source_refs",
                    "previewable_quote",
                    "artifact_provenance",
                    "source_url_available",
                    "high_confidence",
                ],
            }
        },
        {
            "candidate_quality": {
                "label": "partial",
                "source_ref_count": 1,
                "previewable_source_ref_count": 1,
                "has_primary_artifact": True,
                "has_source_url": False,
                "confidence_bucket": "medium",
                "reasons": [
                    "single_source_ref",
                    "previewable_quote",
                    "artifact_provenance",
                    "missing_source_url",
                    "medium_confidence",
                ],
            }
        },
    ]

    passed, row = benchmark._evaluate_candidate_quality(repository, candidates, None)

    assert passed is True
    assert row["observations"]["strong_candidate_count"] == 1
    assert row["observations"]["thin_candidate_ratio"] == 0
    assert row["observations"]["source_url_gap_count"] == 1
    assert row["observations"]["reason_counts"]["missing_source_url"] == 1
    assert row["observations"]["reason_counts"]["source_url_available"] == 1
    assert row["checks"]["reason_payload_available"] is True


def test_live_real_repo_validation_writes_missing_workspace_report(tmp_path, monkeypatch) -> None:
    benchmark = _load_benchmark_module()
    repository = {
        "id": "repo",
        "repo": "org/repo",
        "workspace_slug": "github-org-repo",
        "role": "small_python_library",
        "benchmark_purpose": "Missing workspace classification test.",
        "expectations": {
            "expected_value_outcomes": ["missing_workspace"],
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
    assert report["repositories"][0]["role"] == "small_python_library"
    assert report["repositories"][0]["benchmark_purpose"] == "Missing workspace classification test."
    assert report["repositories"][0]["value_outcome"] == "missing_workspace"
    assert report["repositories"][0]["limitation_categories"] == ["missing_workspace"]
    assert report["repositories"][0]["follow_up_categories"] == ["operator_setup"]
    assert report["summary"] == {"repositories": 1, "passed": 0, "failed": 1}


def test_live_real_repo_validation_reports_dashboard_why_and_drift(tmp_path, monkeypatch) -> None:
    benchmark = _load_benchmark_module()
    repository = {
        "id": "repo",
        "repo": "org/repo",
        "workspace_slug": "github-org-repo",
        "role": "decision_rich_regression_repo",
        "benchmark_purpose": "Useful value classification test.",
        "expectations": {
            "expected_value_outcomes": ["useful_now"],
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
        "expected_primary_title": "Use queue",
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
        if path.startswith("/decisions"):
            return [
                {
                    "candidate_quality": {
                        "label": "strong",
                        "source_ref_count": 2,
                        "previewable_source_ref_count": 1,
                        "has_primary_artifact": True,
                        "has_source_url": True,
                        "confidence_bucket": "high",
                        "reasons": [
                            "multiple_source_refs",
                            "previewable_quote",
                            "artifact_provenance",
                            "source_url_available",
                            "high_confidence",
                        ],
                    }
                }
            ], None
        if path == "/query/why":
            return {
                "status": "review_required",
                "answer": "Review one candidate before using why-search.",
                "citations": [{"id": 1}],
                "primary_decision": {"title": "Use queue"},
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
    assert report["repositories"][0]["role"] == "decision_rich_regression_repo"
    assert report["repositories"][0]["benchmark_purpose"] == "Useful value classification test."
    assert report["repositories"][0]["value_outcome"] == "useful_now"
    assert report["repositories"][0]["value_outcome_allowed"] is True
    assert report["repositories"][0]["limitation_categories"] == []
    assert report["repositories"][0]["follow_up_categories"] == []
    assert report["repositories"][0]["key_metrics"]["why_case_passed_count"] == 1
    assert report["repositories"][0]["key_metrics"]["drift_case_passed_count"] == 1
    assert report["repositories"][0]["candidate_quality"]["passed"] is True
    assert report["repositories"][0]["candidate_quality"]["observations"]["strong_candidate_count"] == 1
    assert report["repositories"][0]["why_cases"][0]["expected_terms"] == ["review"]
    assert report["repositories"][0]["why_cases"][0]["matched_terms"] == ["review"]
    assert report["repositories"][0]["why_cases"][0]["primary_thread_match"] is True
    assert report["repositories"][0]["why_cases"][0]["passed"] is True
    assert report["repositories"][0]["drift"]["cases"][0]["passed"] is True


def test_value_classification_covers_bounded_outcome_families() -> None:
    benchmark = _load_benchmark_module()

    useful = benchmark._attach_value_summary(
        {
            "dashboard": {
                "bounded_outcome": "why_ready",
                "candidate_decision_count": 1,
                "accepted_decision_count": 1,
                "total_decision_count": 2,
                "checks": {"readiness_allowed": True},
            },
            "candidate_quality": {"passed": True, "observations": {"strong_candidate_count": 1, "thin_candidate_ratio": 0}},
            "why_cases": [{"passed": True}],
            "drift": {"passed": True, "cases": [{"passed": True}]},
            "expectations": {"expected_value_outcomes": ["useful_now"]},
        }
    )
    reviewable_limited = benchmark._attach_value_summary(
        {
            "dashboard": {
                "bounded_outcome": "review_ready",
                "candidate_decision_count": 1,
                "accepted_decision_count": 0,
                "total_decision_count": 1,
                "checks": {"readiness_allowed": True},
            },
            "candidate_quality": {
                "passed": False,
                "observations": {"strong_candidate_count": 0, "thin_candidate_ratio": 1, "provenance_gap_count": 1},
                "checks": {"minimum_strong_candidates": False},
            },
            "why_cases": [],
            "drift": {"passed": True, "cases": []},
            "expectations": {"expected_value_outcomes": ["reviewable_limited"]},
        }
    )
    conversion_limited = benchmark._attach_value_summary(
        {"dashboard": {"bounded_outcome": "conversion_limited"}, "candidate_quality": {}, "why_cases": [], "drift": {}}
    )
    evidence_limited = benchmark._attach_value_summary(
        {
            "dashboard": {"bounded_outcome": "evidence_limited", "total_decision_count": 0},
            "candidate_quality": {},
            "why_cases": [],
            "drift": {},
        }
    )
    missing_workspace = benchmark._attach_value_summary({"bounded_outcome": "missing_workspace", "operational_error": {}})
    operational_blocked = benchmark._attach_value_summary({"bounded_outcome": "unknown", "operational_error": {"type": "url_error"}})

    assert useful["value_outcome"] == "useful_now"
    assert reviewable_limited["value_outcome"] == "reviewable_limited"
    assert "candidate_quality" in reviewable_limited["follow_up_categories"]
    assert conversion_limited["value_outcome"] == "conversion_limited"
    assert evidence_limited["value_outcome"] == "evidence_limited"
    assert missing_workspace["value_outcome"] == "missing_workspace"
    assert operational_blocked["value_outcome"] == "operational_blocked"


def test_live_real_repo_validation_writes_markdown_report_from_json_rows(tmp_path, monkeypatch) -> None:
    benchmark = _load_benchmark_module()
    repository = {
        "id": "repo",
        "repo": "org/repo",
        "workspace_slug": "github-org-repo",
        "role": "small_python_library",
        "benchmark_purpose": "Markdown mirror test.",
        "expectations": {
            "expected_value_outcomes": ["missing_workspace"],
            "expected_readiness_states": ["review_ready"],
            "expected_why_states": ["review_required"],
            "expected_drift_states": ["review_required"],
        },
    }

    def fake_request(**kwargs):
        return None, {"type": "http_error", "status": 404, "detail": "not found"}

    monkeypatch.setattr(benchmark, "_json_request", fake_request)
    report_path = tmp_path / "report.json"
    markdown_report_path = tmp_path / "report.md"

    status = benchmark.run_live_real_repo_validation(
        base_url="http://127.0.0.1:3001",
        repositories=[repository],
        why_cases=[],
        drift_cases=[],
        report_path=report_path,
        markdown_report_path=markdown_report_path,
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    markdown = markdown_report_path.read_text(encoding="utf-8")
    assert status == 1
    assert report["repositories"][0]["value_outcome"] == "missing_workspace"
    assert "| org/repo | small_python_library | Markdown mirror test." in markdown
    assert "missing_workspace" in markdown
    assert "operator_setup" in markdown


def test_live_repo_filtering_keeps_offline_fixture_validation_independent() -> None:
    benchmark = _load_benchmark_module()
    root = Path(__file__).resolve().parents[4]
    repositories = json.loads((root / "examples" / "live-benchmarks" / "repositories.json").read_text(encoding="utf-8"))
    why_cases = json.loads((root / "examples" / "live-benchmarks" / "why-cases.json").read_text(encoding="utf-8"))
    drift_cases = json.loads((root / "examples" / "live-benchmarks" / "drift-cases.json").read_text(encoding="utf-8"))

    filtered_repositories, filtered_why_cases, filtered_drift_cases = benchmark._filter_live_repo_inputs(
        repositories=repositories,
        why_cases=why_cases,
        drift_cases=drift_cases,
        repo_ids=["browser-use"],
    )

    assert benchmark.validate_live_repo_set(repositories) == 0
    assert [repository["id"] for repository in filtered_repositories] == ["browser-use"]
    assert {case["repo_id"] for case in filtered_why_cases} == {"browser-use"}
    assert {case["repo_id"] for case in filtered_drift_cases} == {"browser-use"}

    try:
        benchmark._filter_live_repo_inputs(
            repositories=repositories,
            why_cases=why_cases,
            drift_cases=drift_cases,
            repo_ids=["missing-repo"],
        )
    except ValueError as exc:
        assert "missing-repo" in str(exc)
    else:
        raise AssertionError("Expected missing repository filter to fail.")
