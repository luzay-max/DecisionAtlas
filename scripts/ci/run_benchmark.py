from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import sys
from typing import Any
from urllib import error, request
from urllib.parse import urlencode, urlsplit, urlunsplit


VALUE_OUTCOMES = {
    "useful_now",
    "reviewable_limited",
    "conversion_limited",
    "evidence_limited",
    "missing_workspace",
    "operational_blocked",
}
BENCHMARK_HISTORY_SCHEMA_VERSION = 2
SUPPORTED_BENCHMARK_HISTORY_SCHEMA_VERSIONS = {1, BENCHMARK_HISTORY_SCHEMA_VERSION}
OPERATIONAL_VALUE_OUTCOMES = {"missing_workspace", "operational_blocked"}
PRODUCT_LIMITED_VALUE_OUTCOMES = {"conversion_limited", "evidence_limited"}
VALUE_OUTCOME_RANK = {
    "useful_now": 5,
    "reviewable_limited": 4,
    "evidence_limited": 2,
    "conversion_limited": 1,
}
VALUE_OUTCOME_ASSESSMENTS = {
    "exact",
    "exceeds_floor",
    "below_floor",
    "operational",
    "not_constrained",
}
BENCHMARK_MOVEMENTS = {
    "improved",
    "unchanged",
    "regressed",
    "product-limited",
    "operationally-blocked",
    "newly-evaluated",
    "missing-from-current",
    "needs-review",
}


def _safe_base_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme and parsed.hostname:
        netloc = parsed.hostname
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"
        return urlunsplit((parsed.scheme, netloc, "", "", ""))
    return "<redacted>"


def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_request(
    *,
    base_url: str,
    path: str,
    method: str = "GET",
    body: dict | None = None,
    timeout: int = 30,
) -> tuple[dict | None, dict | None]:
    encoded_body = json.dumps(body).encode("utf-8") if body is not None else None
    http_request = request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=encoded_body,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with request.urlopen(http_request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8")), None
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return None, {"type": "http_error", "status": exc.code, "detail": detail}
    except error.URLError as exc:
        return None, {"type": "url_error", "detail": str(exc)}


def _operational_outcome(error_payload: dict | None, *, missing_workspace_on_404: bool = False) -> str:
    if missing_workspace_on_404 and error_payload and error_payload.get("status") == 404:
        return "missing_workspace"
    return "operational_failure"


def _nested_int(payload: dict | None, *keys: str) -> int:
    current: object = payload or {}
    for key in keys:
        if not isinstance(current, dict):
            return 0
        current = current.get(key)
    try:
        return int(current or 0)
    except (TypeError, ValueError):
        return 0


def _optional_nonnegative_int(payload: dict, key: str) -> int | None:
    if key not in payload or payload.get(key) is None:
        return None
    try:
        return max(0, int(payload.get(key)))
    except (TypeError, ValueError):
        return None


def _ratio(numerator: int | None, denominator: int | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return round(numerator / denominator, 4)


def _bounded_counter_map(value: object) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    counters: dict[str, int] = {}
    for key, raw_count in value.items():
        label = str(key).strip()[:80]
        if not label:
            continue
        try:
            counters[label] = max(0, int(raw_count))
        except (TypeError, ValueError):
            continue
    return dict(sorted(counters.items()))


def _provider_metadata(base_url: str) -> dict[str, Any]:
    payload, error_payload = _json_request(base_url=base_url, path="/runtime/provider-mode")
    if not isinstance(payload, dict):
        return {
            "status": "not_provided",
            "mode": "unknown",
            "is_live": None,
            "llm_provider_mode": "unknown",
            "embedding_provider_mode": "unknown",
            "model_label": os.getenv("LLM_MODEL") or "not_provided",
            "error_type": (error_payload or {}).get("type") if isinstance(error_payload, dict) else None,
        }
    return {
        "status": "provided",
        "mode": payload.get("mode") or "unknown",
        "is_live": payload.get("is_live"),
        "llm_provider_mode": payload.get("llm_provider_mode") or "unknown",
        "embedding_provider_mode": payload.get("embedding_provider_mode") or "unknown",
        "model_label": os.getenv("LLM_MODEL") or "not_provided",
    }


def _sparse_conversion_from_payload(
    dashboard_payload: dict,
    provider_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    extraction = _latest_import_summary(dashboard_payload).get("extraction_summary")
    provider = provider_metadata or {
        "status": "not_provided",
        "mode": "unknown",
        "is_live": None,
        "llm_provider_mode": "unknown",
        "embedding_provider_mode": "unknown",
        "model_label": "not_provided",
    }
    base = {
        "status": "not_provided",
        "skip_reason": None,
        "normal_attempts": None,
        "normal_candidates": None,
        "sparse_eligible_artifacts": None,
        "sparse_attempted_artifacts": None,
        "sparse_model_attempts": None,
        "sparse_recovered_candidates": None,
        "recovery_candidates": None,
        "candidate_yield": None,
        "normal_candidate_yield": None,
        "sparse_recovered_yield": None,
        "rejection_reasons": {},
        "conversion_loss_reasons": {},
        "elapsed_seconds": None,
        "provider_mode": provider.get("mode") or "unknown",
        "provider_is_live": provider.get("is_live"),
        "llm_provider_mode": provider.get("llm_provider_mode") or "unknown",
        "embedding_provider_mode": provider.get("embedding_provider_mode") or "unknown",
        "model_label": provider.get("model_label") or "not_provided",
    }
    if not isinstance(extraction, dict):
        return base

    normal_attempts = _optional_nonnegative_int(extraction, "full_extraction_requests")
    created_candidates = _optional_nonnegative_int(extraction, "created_candidates")
    recovery_candidates = _optional_nonnegative_int(extraction, "recovered_candidates")
    sparse_eligible = _optional_nonnegative_int(extraction, "sparse_recovery_eligible_artifacts")
    sparse_attempted = _optional_nonnegative_int(extraction, "sparse_recovery_attempted_artifacts")
    sparse_attempts = _optional_nonnegative_int(extraction, "sparse_recovery_model_attempts")
    sparse_recovered = _optional_nonnegative_int(extraction, "sparse_recovery_recovered_candidates")
    normal_candidates = (
        max(created_candidates - recovery_candidates, 0)
        if created_candidates is not None and recovery_candidates is not None
        else None
    )
    total_attempts = (
        normal_attempts + sparse_attempts
        if normal_attempts is not None and sparse_attempts is not None
        else None
    )
    return {
        **base,
        "status": str(extraction.get("sparse_recovery_status") or "not_provided"),
        "skip_reason": extraction.get("sparse_recovery_skip_reason"),
        "normal_attempts": normal_attempts,
        "normal_candidates": normal_candidates,
        "sparse_eligible_artifacts": sparse_eligible,
        "sparse_attempted_artifacts": sparse_attempted,
        "sparse_model_attempts": sparse_attempts,
        "sparse_recovered_candidates": sparse_recovered,
        "recovery_candidates": recovery_candidates,
        "candidate_yield": _ratio(created_candidates, total_attempts),
        "normal_candidate_yield": _ratio(normal_candidates, normal_attempts),
        "sparse_recovered_yield": _ratio(sparse_recovered, sparse_attempts),
        "rejection_reasons": _bounded_counter_map(extraction.get("sparse_recovery_rejection_reasons")),
        "conversion_loss_reasons": _bounded_counter_map(extraction.get("conversion_loss_reasons")),
        "elapsed_seconds": _optional_nonnegative_int(extraction, "elapsed_seconds"),
    }


def _latest_import_summary(dashboard_payload: dict) -> dict:
    latest_import = dashboard_payload.get("latest_import") or {}
    summary = latest_import.get("summary")
    return summary if isinstance(summary, dict) else {}


def _decision_total(decision_counts: dict) -> int:
    return sum(int(decision_counts.get(state, 0) or 0) for state in ("candidate", "accepted", "rejected", "superseded"))


def _write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_json_object(path: Path) -> dict:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return loaded


def validate_live_repo_set(repositories: list[dict]) -> int:
    if not repositories:
        print("Live benchmark repository set is empty.", file=sys.stderr)
        return 1

    print(f"Loaded {len(repositories)} live benchmark repositories.")
    for repository in repositories:
        expectations = repository.get("expectations", {})
        if not repository.get("repo") or "/" not in repository["repo"]:
            print(f"Invalid repository entry: {repository}", file=sys.stderr)
            return 1
        if not str(repository.get("role", "")).strip():
            print(f"Missing repository role for {repository['repo']}.", file=sys.stderr)
            return 1
        if not str(repository.get("benchmark_purpose", "")).strip():
            print(f"Missing benchmark purpose for {repository['repo']}.", file=sys.stderr)
            return 1
        expected_value_outcomes = expectations.get("expected_value_outcomes")
        if not isinstance(expected_value_outcomes, list) or not expected_value_outcomes:
            print(f"Missing expected value outcomes for {repository['repo']}.", file=sys.stderr)
            return 1
        if any(outcome not in VALUE_OUTCOMES for outcome in expected_value_outcomes):
            print(f"Invalid expected value outcome for {repository['repo']}.", file=sys.stderr)
            return 1
        if expectations.get("minimum_candidate_decisions", 0) < 0:
            print(f"Invalid minimum candidate count for {repository['repo']}.", file=sys.stderr)
            return 1
        if expectations.get("minimum_reviewable_candidates", 0) < 0:
            print(f"Invalid minimum reviewable candidate count for {repository['repo']}.", file=sys.stderr)
            return 1
        if expectations.get("minimum_accepted_decisions", 0) < 0:
            print(f"Invalid minimum accepted decision count for {repository['repo']}.", file=sys.stderr)
            return 1
        if expectations.get("minimum_screened_in_artifacts", 0) < 0:
            print(f"Invalid minimum screened-in count for {repository['repo']}.", file=sys.stderr)
            return 1
        candidate_quality = expectations.get("candidate_quality")
        if not isinstance(candidate_quality, dict):
            print(f"Missing candidate_quality expectations for {repository['repo']}.", file=sys.stderr)
            return 1
        if candidate_quality.get("minimum_strong_candidates", 0) < 0:
            print(f"Invalid minimum strong candidate count for {repository['repo']}.", file=sys.stderr)
            return 1
        max_thin_ratio = candidate_quality.get("maximum_thin_candidate_ratio", 1)
        if not isinstance(max_thin_ratio, int | float) or max_thin_ratio < 0 or max_thin_ratio > 1:
            print(f"Invalid maximum thin candidate ratio for {repository['repo']}.", file=sys.stderr)
            return 1
        if not expectations.get("expected_readiness_states"):
            print(f"Missing readiness expectations for {repository['repo']}.", file=sys.stderr)
            return 1
        if not expectations.get("expected_why_states"):
            print(f"Missing why expectations for {repository['repo']}.", file=sys.stderr)
            return 1
        if not expectations.get("expected_drift_states"):
            print(f"Missing drift expectations for {repository['repo']}.", file=sys.stderr)
            return 1
        if expectations.get("minimum_accepted_decisions", 0) > 0 and not expectations.get(
            "expected_why_states_after_first_acceptance"
        ):
            print(
                f"Missing first-acceptance why expectations for {repository['repo']}.",
                file=sys.stderr,
            )
            return 1
        print(
            f"{repository['id']}: repo={repository['repo']} "
            f"role={repository['role']} "
            f"min_candidates={expectations.get('minimum_candidate_decisions', 0)} "
            f"min_reviewable={expectations.get('minimum_reviewable_candidates', 0)} "
            f"min_accepted={expectations.get('minimum_accepted_decisions', 0)} "
            f"min_screened_in={expectations.get('minimum_screened_in_artifacts', 0)} "
            f"min_strong={candidate_quality.get('minimum_strong_candidates', 0)} "
            f"max_thin_ratio={max_thin_ratio}"
        )
    return 0


def _repo_ids(repositories: list[dict]) -> set[str]:
    return {repository["id"] for repository in repositories if repository.get("id")}


def validate_why_cases(why_cases: list[dict], repositories: list[dict]) -> int:
    if not why_cases:
        print("Live benchmark why-case set is empty.", file=sys.stderr)
        return 1

    repo_ids = _repo_ids(repositories)
    seen_ids: set[str] = set()
    print(f"Loaded {len(why_cases)} real-repo why benchmark cases.")
    for case in why_cases:
        case_id = case.get("id")
        if not case_id or case_id in seen_ids:
            print(f"Invalid or duplicate why case id: {case}", file=sys.stderr)
            return 1
        seen_ids.add(case_id)
        if case.get("repo_id") not in repo_ids:
            print(f"Why case {case_id} references unknown repo_id: {case.get('repo_id')}", file=sys.stderr)
            return 1
        if not case.get("repo") or "/" not in case["repo"]:
            print(f"Invalid repo for why case {case_id}: {case.get('repo')}", file=sys.stderr)
            return 1
        if not case.get("workspace_slug", "").startswith("github-"):
            print(f"Invalid workspace_slug for why case {case_id}: {case.get('workspace_slug')}", file=sys.stderr)
            return 1
        if not case.get("question", "").strip():
            print(f"Missing question for why case {case_id}.", file=sys.stderr)
            return 1
        if not case.get("expected_status"):
            print(f"Missing expected_status for why case {case_id}.", file=sys.stderr)
            return 1
        if case.get("min_citations", 0) < 1:
            print(f"Invalid min_citations for why case {case_id}.", file=sys.stderr)
            return 1
        if not case.get("expected_terms"):
            print(f"Missing expected_terms for why case {case_id}.", file=sys.stderr)
            return 1
        if case.get("repo_id") == "browser-use" and case.get("expected_primary_title") is None:
            print(f"Browser-use regression why case {case_id} must name an expected primary title.", file=sys.stderr)
            return 1
        expected_primary_title = case.get("expected_primary_title")
        if expected_primary_title is not None and not str(expected_primary_title).strip():
            print(f"Invalid expected_primary_title for why case {case_id}.", file=sys.stderr)
            return 1
        print(
            f"{case_id}: workspace={case['workspace_slug']} "
            f"status={case['expected_status']} min_citations={case['min_citations']}"
        )
    return 0


def validate_drift_cases(drift_cases: list[dict], repositories: list[dict]) -> int:
    if not drift_cases:
        print("Live benchmark drift-case set is empty.", file=sys.stderr)
        return 1

    repo_ids = _repo_ids(repositories)
    seen_ids: set[str] = set()
    print(f"Loaded {len(drift_cases)} real-repo drift benchmark cases.")
    for case in drift_cases:
        case_id = case.get("id")
        if not case_id or case_id in seen_ids:
            print(f"Invalid or duplicate drift case id: {case}", file=sys.stderr)
            return 1
        seen_ids.add(case_id)
        if case.get("repo_id") not in repo_ids:
            print(f"Drift case {case_id} references unknown repo_id: {case.get('repo_id')}", file=sys.stderr)
            return 1
        if not case.get("workspace_slug", "").startswith("github-"):
            print(f"Invalid workspace_slug for drift case {case_id}: {case.get('workspace_slug')}", file=sys.stderr)
            return 1
        if not case.get("artifact_title_pattern", "").strip():
            print(f"Missing artifact_title_pattern for drift case {case_id}.", file=sys.stderr)
            return 1
        if not case.get("accepted_decision_title", "").strip():
            print(f"Missing accepted_decision_title for drift case {case_id}.", file=sys.stderr)
            return 1
        if not case.get("forbidden_alert_types"):
            print(f"Missing forbidden_alert_types for drift case {case_id}.", file=sys.stderr)
            return 1
        if not case.get("allowed_outcomes"):
            print(f"Missing allowed_outcomes for drift case {case_id}.", file=sys.stderr)
            return 1
        if case.get("repo_id") == "browser-use" and "possible_supersession" not in case.get("forbidden_alert_types", []):
            print(f"Browser-use drift case {case_id} must forbid possible_supersession.", file=sys.stderr)
            return 1
        print(
            f"{case_id}: workspace={case['workspace_slug']} "
            f"forbidden={','.join(case['forbidden_alert_types'])}"
        )
    return 0


def validate_fixtures(queries: list[dict], expected_answers: list[dict]) -> int:
    root = Path(__file__).resolve().parents[2]
    query_ids = [item["id"] for item in queries]
    expected_ids = [item["id"] for item in expected_answers]

    if query_ids != expected_ids:
        print("Benchmark fixture mismatch between queries and expected answers.", file=sys.stderr)
        return 1

    print(f"Loaded {len(queries)} benchmark queries.")
    for query, expected in zip(queries, expected_answers):
        print(
            f"{query['id']}: {query['question']} -> topic={expected['expected_topic']} "
            f"min_citations={expected['min_citations']}"
        )
    return 0


def _why_payload_observations(payload: dict, expected: dict) -> dict:
    answer = (payload.get("answer") or "").lower()
    expected_terms = [term.lower() for term in expected.get("expected_terms", [])]
    observed_status = payload.get("status")
    citations = payload.get("citations", [])
    primary_decision = payload.get("primary_decision") if isinstance(payload.get("primary_decision"), dict) else {}
    observed_primary_title = primary_decision.get("title")
    expected_primary_title = expected.get("expected_primary_title")
    primary_title_match = (
        str(expected_primary_title).lower() in str(observed_primary_title).lower()
        if expected_primary_title
        else True
    )
    matched_terms = [term for term in expected_terms if term in answer]
    return {
        "expected_status": expected.get("expected_status", "ok"),
        "observed_status": observed_status,
        "expected_min_citations": expected["min_citations"],
        "observed_citations": len(citations),
        "expected_terms": expected_terms,
        "matched_terms": matched_terms,
        "term_matches": len(matched_terms) == len(expected_terms),
        "expected_primary_title": expected_primary_title,
        "observed_primary_title": observed_primary_title,
        "primary_thread_match": primary_title_match,
    }


def _evaluate_why_payload(payload: dict, expected: dict) -> tuple[bool, str]:
    observations = _why_payload_observations(payload, expected)
    status_matches = observations["observed_status"] == observations["expected_status"]
    citations_match = observations["observed_citations"] >= observations["expected_min_citations"]
    term_matches = observations["term_matches"]
    primary_thread_match = observations["primary_thread_match"]
    passed = status_matches and citations_match and term_matches and primary_thread_match
    if passed:
        return True, "passed"
    return (
        False,
        "expected "
        f"status={observations['expected_status']} min_citations={observations['expected_min_citations']} "
        f"terms={observations['expected_terms']} primary={observations['expected_primary_title']}; "
        f"observed status={observations['observed_status']} citations={observations['observed_citations']} "
        f"primary={observations['observed_primary_title']}",
    )


def run_live_benchmark(*, base_url: str, workspace_slug: str, queries: list[dict], expected_answers: list[dict]) -> int:
    failures = 0
    for query, expected in zip(queries, expected_answers):
        body = json.dumps(
            {
                "workspace_slug": workspace_slug,
                "question": query["question"],
            }
        ).encode("utf-8")
        http_request = request.Request(
            f"{base_url.rstrip('/')}/query/why",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except error.URLError as exc:
            print(f"Live benchmark request failed for {query['id']}: {exc}", file=sys.stderr)
            return 1

        passed, reason = _evaluate_why_payload(payload, expected)
        print(
            f"{query['id']}: status={payload.get('status')} citations={len(payload.get('citations', []))} "
            f"passed={passed}"
        )
        if not passed:
            print(f"Demo benchmark failed for {query['id']}: {reason}", file=sys.stderr)
            failures += 1
    if failures:
        print(f"Live benchmark failed for {failures} queries.", file=sys.stderr)
        return 1
    return 0


def run_live_real_repo_why_cases(*, base_url: str, why_cases: list[dict]) -> int:
    failures = 0
    for case in why_cases:
        body = json.dumps(
            {
                "workspace_slug": case["workspace_slug"],
                "question": case["question"],
            }
        ).encode("utf-8")
        http_request = request.Request(
            f"{base_url.rstrip('/')}/query/why",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except error.URLError as exc:
            print(
                f"Live real-repo why case failed for {case['id']} "
                f"workspace={case['workspace_slug']}: {exc}",
                file=sys.stderr,
            )
            return 1

        passed, reason = _evaluate_why_payload(payload, case)
        print(
            f"{case['id']}: workspace={case['workspace_slug']} "
            f"status={payload.get('status')} citations={len(payload.get('citations', []))} passed={passed}"
        )
        if not passed:
            print(
                f"Live real-repo why case failed for {case['id']} "
                f"workspace={case['workspace_slug']}: {reason}",
                file=sys.stderr,
            )
            failures += 1
    if failures:
        print(f"Live real-repo why benchmark failed for {failures} cases.", file=sys.stderr)
        return 1
    return 0


def _evaluate_dashboard_payload(
    repository: dict,
    payload: dict,
    provider_metadata: dict[str, Any] | None = None,
) -> tuple[bool, dict]:
    expectations = repository.get("expectations", {})
    readiness = payload.get("workspace_readiness") or {}
    drift_status = payload.get("drift_status") or {}
    decision_counts = payload.get("decision_counts") or {}
    import_summary = _latest_import_summary(payload)
    extraction_summary = import_summary.get("extraction_summary") if isinstance(import_summary, dict) else {}
    extraction_summary = extraction_summary if isinstance(extraction_summary, dict) else {}

    readiness_state = readiness.get("state")
    why_state = readiness.get("why_state")
    drift_state = drift_status.get("state") or readiness.get("drift_state")
    candidate_count = int(decision_counts.get("candidate", 0) or 0)
    accepted_count = int(decision_counts.get("accepted", 0) or 0)
    total_decisions = _decision_total(decision_counts)
    screened_in_count = _nested_int({"extraction_summary": extraction_summary}, "extraction_summary", "screened_in_artifacts")

    checks = {
        "readiness_allowed": readiness_state in expectations.get("expected_readiness_states", []),
        "why_allowed": why_state in expectations.get("expected_why_states", []) if why_state else True,
        "drift_allowed": drift_state in expectations.get("expected_drift_states", []) if drift_state else True,
        "minimum_candidate_decisions": total_decisions >= int(expectations.get("minimum_candidate_decisions", 0) or 0),
        "minimum_reviewable_candidates": candidate_count >= int(expectations.get("minimum_reviewable_candidates", 0) or 0),
        "minimum_accepted_decisions": accepted_count >= int(expectations.get("minimum_accepted_decisions", 0) or 0),
        "minimum_screened_in_artifacts": screened_in_count >= int(expectations.get("minimum_screened_in_artifacts", 0) or 0),
    }
    row = {
        "workspace_slug": repository["workspace_slug"],
        "workspace_mode": payload.get("workspace_mode"),
        "bounded_outcome": readiness_state or "unknown",
        "readiness_state": readiness_state,
        "review_state": readiness.get("review_state"),
        "why_state": why_state,
        "drift_state": drift_state,
        "next_action": readiness.get("next_action"),
        "recommended_actions": readiness.get("recommended_actions") or [],
        "candidate_decision_count": candidate_count,
        "accepted_decision_count": accepted_count,
        "total_decision_count": total_decisions,
        "screened_in_artifact_count": screened_in_count,
        "latest_import_status": payload.get("import_status"),
        "sparse_conversion": _sparse_conversion_from_payload(payload, provider_metadata),
        "checks": checks,
    }
    return all(checks.values()), row


def _summarize_candidate_quality(candidates: list[dict]) -> dict:
    label_counts: dict[str, int] = {}
    provenance_gaps = 0
    source_url_gaps = 0
    previewable_refs = 0
    source_refs = 0
    confidence_buckets: dict[str, int] = {}
    reason_counts: dict[str, int] = {}
    for candidate in candidates:
        quality = candidate.get("candidate_quality") or {}
        label = str(quality.get("label") or "unknown")
        label_counts[label] = label_counts.get(label, 0) + 1
        if quality.get("has_primary_artifact") is False:
            provenance_gaps += 1
        if quality.get("has_source_url") is False:
            source_url_gaps += 1
        source_refs += int(quality.get("source_ref_count") or 0)
        previewable_refs += int(quality.get("previewable_source_ref_count") or 0)
        confidence_bucket = str(quality.get("confidence_bucket") or "unknown")
        confidence_buckets[confidence_bucket] = confidence_buckets.get(confidence_bucket, 0) + 1
        for reason in quality.get("reasons") or []:
            reason = str(reason)
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
    total = len(candidates)
    thin = label_counts.get("thin", 0)
    return {
        "candidate_count": total,
        "label_counts": label_counts,
        "strong_candidate_count": label_counts.get("strong", 0),
        "thin_candidate_count": thin,
        "thin_candidate_ratio": round(thin / total, 4) if total else 0,
        "source_ref_count": source_refs,
        "previewable_source_ref_count": previewable_refs,
        "provenance_gap_count": provenance_gaps,
        "source_url_gap_count": source_url_gaps,
        "confidence_buckets": confidence_buckets,
        "reason_counts": reason_counts,
    }


def _evaluate_candidate_quality(repository: dict, candidates: list[dict] | None, error_payload: dict | None) -> tuple[bool, dict]:
    expectations = (repository.get("expectations") or {}).get("candidate_quality") or {}
    if error_payload is not None or candidates is None:
        return False, {
            "passed": False,
            "operational_error": error_payload,
            "observations": _summarize_candidate_quality([]),
            "checks": {
                "quality_payload_available": False,
                "reason_payload_available": False,
                "minimum_strong_candidates": False,
                "maximum_thin_candidate_ratio": False,
                "provenance_available": False,
            },
        }

    observations = _summarize_candidate_quality(candidates)
    total = observations["candidate_count"]
    checks = {
        "quality_payload_available": all("candidate_quality" in candidate for candidate in candidates),
        "reason_payload_available": all(
            isinstance((candidate.get("candidate_quality") or {}).get("reasons"), list) for candidate in candidates
        ),
        "minimum_strong_candidates": observations["strong_candidate_count"]
        >= int(expectations.get("minimum_strong_candidates", 0) or 0),
        "maximum_thin_candidate_ratio": observations["thin_candidate_ratio"]
        <= float(expectations.get("maximum_thin_candidate_ratio", 1) or 1),
        "provenance_available": (
            observations["provenance_gap_count"] == 0 if expectations.get("require_provenance") and total else True
        ),
    }
    return all(checks.values()), {
        "passed": all(checks.values()),
        "operational_error": None,
        "observations": observations,
        "checks": checks,
    }


def _evaluate_drift_cases_for_workspace(*, payload: dict, cases: list[dict]) -> tuple[bool, list[dict], str | None]:
    evaluation = payload.get("evaluation") or {}
    observed_state = evaluation.get("state")
    alerts = payload.get("alerts") or []
    case_results: list[dict] = []
    failures = 0
    for case in cases:
        title_pattern = case["artifact_title_pattern"].lower()
        forbidden_types = set(case.get("forbidden_alert_types", []))
        matching_forbidden_alerts = []
        for alert in alerts:
            artifact = alert.get("artifact") or {}
            artifact_title = str(artifact.get("title") or "").lower()
            if title_pattern in artifact_title and alert.get("alert_type") in forbidden_types:
                matching_forbidden_alerts.append(
                    {
                        "alert_type": alert.get("alert_type"),
                        "artifact_title": artifact.get("title"),
                        "decision_title": (alert.get("decision") or {}).get("title"),
                    }
                )
        passed = not matching_forbidden_alerts
        failures += 0 if passed else 1
        case_results.append(
            {
                "id": case["id"],
                "passed": passed,
                "forbidden_alert_types": case.get("forbidden_alert_types", []),
                "matching_forbidden_alerts": matching_forbidden_alerts,
            }
        )
    return failures == 0, case_results, observed_state


def _failed_check_names(section: dict | None) -> list[str]:
    checks = (section or {}).get("checks") or {}
    return [name for name, passed in checks.items() if passed is False]


def _follow_up_categories(row: dict) -> list[str]:
    categories: list[str] = []
    dashboard = row.get("dashboard") or {}
    quality = row.get("candidate_quality") or {}
    quality_observations = quality.get("observations") or {}

    if row.get("operational_error"):
        categories.append("operator_setup")
    if dashboard.get("bounded_outcome") == "conversion_limited":
        categories.append("extraction_conversion")
    if dashboard.get("bounded_outcome") == "evidence_limited":
        categories.append("source_evidence")
    if quality_observations.get("thin_candidate_ratio", 0) > 0:
        categories.append("candidate_quality")
    if quality_observations.get("provenance_gap_count", 0) > 0:
        categories.append("provenance")
    if quality_observations.get("source_url_gap_count", 0) > 0:
        categories.append("source_url_coverage")
    if any(not case.get("passed") for case in row.get("why_cases", [])):
        categories.append("why_retrieval")
    drift = row.get("drift") or {}
    if drift and not drift.get("passed", True):
        categories.append("drift_precision")
    for check_name in _failed_check_names(dashboard):
        categories.append(f"dashboard:{check_name}")
    for check_name in _failed_check_names(quality):
        categories.append(f"candidate_quality:{check_name}")
    return sorted(set(categories))


def _limitation_categories(row: dict) -> list[str]:
    categories: list[str] = []
    dashboard = row.get("dashboard") or {}
    quality = row.get("candidate_quality") or {}
    quality_observations = quality.get("observations") or {}

    if row.get("bounded_outcome") == "missing_workspace":
        categories.append("missing_workspace")
    elif row.get("operational_error"):
        categories.append("operational_blocker")
    if dashboard.get("bounded_outcome") == "conversion_limited":
        categories.append("candidate_conversion")
    if dashboard.get("bounded_outcome") == "evidence_limited":
        categories.append("source_evidence")
    if quality_observations.get("thin_candidate_ratio", 0) > 0:
        categories.append("thin_candidates")
    if quality_observations.get("provenance_gap_count", 0) > 0:
        categories.append("missing_provenance")
    if quality_observations.get("source_url_gap_count", 0) > 0:
        categories.append("missing_source_url")
    if any(not case.get("passed") for case in row.get("why_cases", [])):
        categories.append("why_support")
    drift = row.get("drift") or {}
    if drift and not drift.get("passed", True):
        categories.append("drift_precision")
    if row.get("value_outcome_allowed") is False:
        categories.append("unexpected_value_outcome")
    return sorted(set(categories))


def _value_outcome(row: dict) -> str:
    if row.get("bounded_outcome") == "missing_workspace":
        return "missing_workspace"
    if row.get("operational_error"):
        return "operational_blocked"

    dashboard = row.get("dashboard") or {}
    quality = row.get("candidate_quality") or {}
    drift = row.get("drift") or {}
    bounded_outcome = dashboard.get("bounded_outcome") or row.get("bounded_outcome")
    why_cases = row.get("why_cases") or []
    why_passed = all(case.get("passed") for case in why_cases)
    drift_passed = bool(drift.get("passed", True))
    dashboard_passed = all((dashboard.get("checks") or {}).values()) if dashboard.get("checks") else bool(dashboard)
    quality_passed = bool(quality.get("passed", True))
    accepted_count = int(dashboard.get("accepted_decision_count") or 0)
    candidate_count = int(dashboard.get("candidate_decision_count") or 0)
    total_decisions = int(dashboard.get("total_decision_count") or 0)

    if bounded_outcome == "conversion_limited":
        return "conversion_limited"
    if bounded_outcome == "evidence_limited" and total_decisions == 0:
        return "evidence_limited"
    if dashboard_passed and quality_passed and why_passed and drift_passed and (accepted_count > 0 or candidate_count > 0):
        return "useful_now"
    if candidate_count > 0 or total_decisions > 0:
        return "reviewable_limited"
    return "evidence_limited"


def _assess_value_outcome(outcome: str, expected_outcomes: list[str]) -> dict[str, Any]:
    """Assess a value outcome against a profile's minimum product-value floor."""
    expected = [str(value) for value in expected_outcomes if str(value) in VALUE_OUTCOMES]
    if outcome in OPERATIONAL_VALUE_OUTCOMES:
        return {
            "allowed": outcome in expected,
            "assessment": "operational",
            "minimum_product_value_floor": None,
            "minimum_product_value_rank": None,
        }

    expected_product = [value for value in expected if value in VALUE_OUTCOME_RANK]
    if not expected_product:
        return {
            "allowed": True,
            "assessment": "not_constrained",
            "minimum_product_value_floor": None,
            "minimum_product_value_rank": None,
        }

    floor = min(expected_product, key=lambda value: VALUE_OUTCOME_RANK[value])
    outcome_rank = VALUE_OUTCOME_RANK.get(outcome)
    floor_rank = VALUE_OUTCOME_RANK[floor]
    if outcome in expected:
        assessment = "exact"
    elif outcome_rank is not None and outcome_rank > floor_rank:
        assessment = "exceeds_floor"
    else:
        assessment = "below_floor"
    return {
        "allowed": outcome_rank is not None and outcome_rank >= floor_rank,
        "assessment": assessment,
        "minimum_product_value_floor": floor,
        "minimum_product_value_rank": floor_rank,
    }


def _attach_value_summary(row: dict) -> dict:
    outcome = _value_outcome(row)
    follow_ups = _follow_up_categories(row)
    expectations = ((row.get("expectations") or {}).get("expected_value_outcomes")) or []
    assessment = _assess_value_outcome(outcome, expectations)
    row["value_outcome"] = outcome
    row["value_outcome_allowed"] = assessment["allowed"]
    row["value_outcome_assessment"] = assessment["assessment"]
    row["minimum_product_value_floor"] = assessment["minimum_product_value_floor"]
    row["minimum_product_value_rank"] = assessment["minimum_product_value_rank"]
    row["limitation_categories"] = _limitation_categories(row)
    row["follow_up_categories"] = follow_ups
    row["key_metrics"] = {
        "candidate_decision_count": ((row.get("dashboard") or {}).get("candidate_decision_count")),
        "accepted_decision_count": ((row.get("dashboard") or {}).get("accepted_decision_count")),
        "total_decision_count": ((row.get("dashboard") or {}).get("total_decision_count")),
        "screened_in_artifact_count": ((row.get("dashboard") or {}).get("screened_in_artifact_count")),
        "strong_candidate_count": (((row.get("candidate_quality") or {}).get("observations") or {}).get("strong_candidate_count")),
        "thin_candidate_ratio": (((row.get("candidate_quality") or {}).get("observations") or {}).get("thin_candidate_ratio")),
        "why_case_count": len(row.get("why_cases") or []),
        "why_case_passed_count": sum(1 for case in row.get("why_cases") or [] if case.get("passed")),
        "drift_case_count": len(((row.get("drift") or {}).get("cases")) or []),
        "drift_case_passed_count": sum(1 for case in ((row.get("drift") or {}).get("cases")) or [] if case.get("passed")),
    }
    row["sparse_conversion"] = dict(
        row.get("sparse_conversion")
        or ((row.get("dashboard") or {}).get("sparse_conversion"))
        or {}
    )
    return row


def _markdown_cell(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        text = ", ".join(str(item) for item in value) if value else "-"
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def _write_markdown_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Live Real-Repository Value Benchmark",
        "",
        f"- Generated at: `{report.get('generated_at', '-')}`",
        f"- Base URL: `{report.get('base_url', '-')}`",
        f"- Repositories: `{(report.get('summary') or {}).get('repositories', 0)}`",
        f"- Passed: `{(report.get('summary') or {}).get('passed', 0)}`",
        f"- Failed: `{(report.get('summary') or {}).get('failed', 0)}`",
        "",
        "| Repository | Role | Purpose | Workspace | Value outcome | Bounded outcome | Passed | Key metrics | Limitations | Follow-up |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.get("repositories", []):
        metrics = row.get("key_metrics") or {}
        key_metrics = [
            f"candidates={metrics.get('candidate_decision_count')}",
            f"accepted={metrics.get('accepted_decision_count')}",
            f"strong={metrics.get('strong_candidate_count')}",
            f"thin_ratio={metrics.get('thin_candidate_ratio')}",
            f"why={metrics.get('why_case_passed_count')}/{metrics.get('why_case_count')}",
            f"drift={metrics.get('drift_case_passed_count')}/{metrics.get('drift_case_count')}",
        ]
        lines.append(
            "| "
            + " | ".join(
                _markdown_cell(value)
                for value in (
                    row.get("repo") or row.get("id"),
                    row.get("role"),
                    row.get("benchmark_purpose"),
                    row.get("workspace_slug"),
                    row.get("value_outcome"),
                    row.get("bounded_outcome"),
                    row.get("passed"),
                    key_metrics,
                    row.get("limitation_categories") or [],
                    row.get("follow_up_categories") or [],
                )
            )
            + " |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _operational_error_type(row: dict | None) -> str | None:
    error_payload = (row or {}).get("operational_error")
    if not isinstance(error_payload, dict):
        return None
    status = error_payload.get("status")
    error_type = error_payload.get("type")
    if status:
        return f"{error_type or 'http_error'}:{status}"
    return str(error_type) if error_type else "operational_error"


def _why_case_summary(row: dict) -> dict:
    cases = row.get("why_cases") or []
    return {
        "case_count": len(cases),
        "passed_count": sum(1 for case in cases if case.get("passed")),
        "failed_ids": [str(case.get("id")) for case in cases if case.get("passed") is False and case.get("id")],
        "statuses": sorted({str(case.get("status")) for case in cases if case.get("status")}),
        "primary_thread_match_count": sum(1 for case in cases if case.get("primary_thread_match") is True),
    }


def _drift_case_summary(row: dict) -> dict:
    drift = row.get("drift") or {}
    cases = drift.get("cases") or []
    return {
        "state": drift.get("state"),
        "case_count": len(cases),
        "passed_count": sum(1 for case in cases if case.get("passed")),
        "failed_ids": [str(case.get("id")) for case in cases if case.get("passed") is False and case.get("id")],
        "forbidden_failure_count": sum(
            len(case.get("matching_forbidden_alerts") or []) for case in cases if isinstance(case, dict)
        ),
    }


def _snapshot_row_from_report_row(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "repo": row.get("repo"),
        "workspace_slug": row.get("workspace_slug"),
        "role": row.get("role"),
        "benchmark_purpose": row.get("benchmark_purpose"),
        "passed": bool(row.get("passed")),
        "value_outcome": row.get("value_outcome"),
        "bounded_outcome": row.get("bounded_outcome"),
        "value_outcome_allowed": row.get("value_outcome_allowed"),
        "key_metrics": dict(row.get("key_metrics") or {}),
        "limitation_categories": list(row.get("limitation_categories") or []),
        "follow_up_categories": list(row.get("follow_up_categories") or []),
        "why_summary": _why_case_summary(row),
        "drift_summary": _drift_case_summary(row),
        "operational_error_type": _operational_error_type(row),
        "sparse_conversion": dict(row.get("sparse_conversion") or {}),
    }


def build_benchmark_history_snapshot(report: dict, *, generated_at: str | None = None) -> dict:
    rows = [_snapshot_row_from_report_row(row) for row in report.get("repositories") or []]
    return {
        "schema_version": BENCHMARK_HISTORY_SCHEMA_VERSION,
        "generated_at": generated_at or report.get("generated_at") or datetime.now(UTC).isoformat(),
        "source": "live-real-repo-validation-report",
        "provider": dict(report.get("provider") or {"status": "not_provided"}),
        "summary": {
            "repositories": len(rows),
            "passed": sum(1 for row in rows if row.get("passed")),
            "failed": sum(1 for row in rows if not row.get("passed")),
        },
        "repositories": rows,
    }


def validate_benchmark_history_snapshot(snapshot: dict) -> int:
    if snapshot.get("schema_version") not in SUPPORTED_BENCHMARK_HISTORY_SCHEMA_VERSIONS:
        print("Invalid benchmark history schema_version.", file=sys.stderr)
        return 1
    if not str(snapshot.get("generated_at", "")).strip():
        print("Benchmark history snapshot is missing generated_at.", file=sys.stderr)
        return 1
    rows = snapshot.get("repositories")
    if not isinstance(rows, list):
        print("Benchmark history snapshot repositories must be a list.", file=sys.stderr)
        return 1
    seen_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            print("Benchmark history row must be an object.", file=sys.stderr)
            return 1
        repo_id = str(row.get("id") or "")
        if not repo_id or repo_id in seen_ids:
            print(f"Invalid or duplicate benchmark history repo id: {repo_id}", file=sys.stderr)
            return 1
        seen_ids.add(repo_id)
        if row.get("value_outcome") not in VALUE_OUTCOMES:
            print(f"Invalid value_outcome for benchmark history row {repo_id}.", file=sys.stderr)
            return 1
        if not isinstance(row.get("key_metrics"), dict):
            print(f"Missing key_metrics for benchmark history row {repo_id}.", file=sys.stderr)
            return 1
        if not isinstance(row.get("limitation_categories"), list):
            print(f"Missing limitation_categories for benchmark history row {repo_id}.", file=sys.stderr)
            return 1
        if not isinstance(row.get("follow_up_categories"), list):
            print(f"Missing follow_up_categories for benchmark history row {repo_id}.", file=sys.stderr)
            return 1
        if not isinstance(row.get("why_summary"), dict):
            print(f"Missing why_summary for benchmark history row {repo_id}.", file=sys.stderr)
            return 1
        if not isinstance(row.get("drift_summary"), dict):
            print(f"Missing drift_summary for benchmark history row {repo_id}.", file=sys.stderr)
            return 1
        if "sparse_conversion" in row and not isinstance(row.get("sparse_conversion"), dict):
            print(f"Invalid sparse_conversion for benchmark history row {repo_id}.", file=sys.stderr)
            return 1
    return 0


def _snapshot_from_report_or_snapshot(payload: dict) -> dict:
    if payload.get("schema_version") in SUPPORTED_BENCHMARK_HISTORY_SCHEMA_VERSIONS:
        return payload
    return build_benchmark_history_snapshot(payload)


def _rows_by_id(snapshot: dict) -> dict[str, dict]:
    return {str(row["id"]): row for row in snapshot.get("repositories") or [] if row.get("id")}


def _metric_delta(current: dict, baseline: dict, key: str) -> dict:
    current_metrics = current.get("key_metrics") or {}
    baseline_metrics = baseline.get("key_metrics") or {}
    current_value = current_metrics.get(key)
    baseline_value = baseline_metrics.get(key)
    try:
        delta = None if current_value is None or baseline_value is None else round(float(current_value) - float(baseline_value), 4)
    except (TypeError, ValueError):
        delta = None
    return {"current": current_value, "baseline": baseline_value, "delta": delta}


def _category_delta(current: dict, baseline: dict, key: str) -> dict:
    current_values = set(current.get(key) or [])
    baseline_values = set(baseline.get(key) or [])
    return {
        "current": sorted(current_values),
        "baseline": sorted(baseline_values),
        "added": sorted(current_values - baseline_values),
        "removed": sorted(baseline_values - current_values),
    }


SPARSE_COMPARISON_METRICS = (
    "normal_attempts",
    "normal_candidates",
    "sparse_eligible_artifacts",
    "sparse_attempted_artifacts",
    "sparse_model_attempts",
    "sparse_recovered_candidates",
    "recovery_candidates",
    "candidate_yield",
    "normal_candidate_yield",
    "sparse_recovered_yield",
    "elapsed_seconds",
)


def _sparse_movement(current: dict | None, baseline: dict | None) -> str:
    if current is None:
        return "missing-from-current"
    current_sparse = current.get("sparse_conversion")
    if current.get("operational_error_type") or (
        isinstance(current_sparse, dict) and current_sparse.get("status") == "operationally_blocked"
    ):
        return "operationally-blocked"
    if not isinstance(current_sparse, dict) or current_sparse.get("status") in {None, "not_provided"}:
        return "not_provided"
    if baseline is None or not isinstance(baseline.get("sparse_conversion"), dict):
        return "newly-evaluated"
    baseline_sparse = baseline["sparse_conversion"]
    if baseline_sparse.get("status") in {None, "not_provided"}:
        return "newly-evaluated"
    comparison_key = "sparse_recovered_yield"
    current_value = current_sparse.get(comparison_key)
    baseline_value = baseline_sparse.get(comparison_key)
    if current_value is None or baseline_value is None:
        comparison_key = "candidate_yield"
        current_value = current_sparse.get(comparison_key)
        baseline_value = baseline_sparse.get(comparison_key)
    if current_value is None or baseline_value is None:
        comparison_key = "sparse_recovered_candidates"
        current_value = current_sparse.get(comparison_key)
        baseline_value = baseline_sparse.get(comparison_key)
    try:
        if current_value is None or baseline_value is None:
            return "unchanged" if current_sparse.get("status") == baseline_sparse.get("status") else "needs-review"
        current_number = float(current_value)
        baseline_number = float(baseline_value)
    except (TypeError, ValueError):
        return "needs-review"
    if current_number > baseline_number:
        return "improved"
    if current_number < baseline_number:
        return "regressed"
    return "unchanged"


def _sparse_conversion_comparison(current: dict | None, baseline: dict | None) -> dict[str, Any]:
    current_sparse = (current or {}).get("sparse_conversion")
    baseline_sparse = (baseline or {}).get("sparse_conversion")
    current_sparse = current_sparse if isinstance(current_sparse, dict) else {}
    baseline_sparse = baseline_sparse if isinstance(baseline_sparse, dict) else {}
    metric_deltas: dict[str, dict[str, Any]] = {}
    for key in SPARSE_COMPARISON_METRICS:
        current_value = current_sparse.get(key)
        baseline_value = baseline_sparse.get(key)
        try:
            delta = (
                round(float(current_value) - float(baseline_value), 4)
                if current_value is not None and baseline_value is not None
                else None
            )
        except (TypeError, ValueError):
            delta = None
        metric_deltas[key] = {"current": current_value, "baseline": baseline_value, "delta": delta}
    rejection_delta = {
        "current": sorted((current_sparse.get("rejection_reasons") or {}).keys()),
        "baseline": sorted((baseline_sparse.get("rejection_reasons") or {}).keys()),
    }
    rejection_delta["added"] = sorted(set(rejection_delta["current"]) - set(rejection_delta["baseline"]))
    rejection_delta["removed"] = sorted(set(rejection_delta["baseline"]) - set(rejection_delta["current"]))
    movement = _sparse_movement(current, baseline)
    reasons = []
    if movement == "regressed":
        reasons.append("Sparse conversion yield or recovery count is lower than the baseline.")
    elif movement == "improved":
        reasons.append("Sparse conversion yield or recovery count is higher than the baseline.")
    if rejection_delta["added"]:
        reasons.append("New sparse rejection reasons: " + ", ".join(rejection_delta["added"][:5]))
    return {
        "movement": movement,
        "status": current_sparse.get("status"),
        "baseline_status": baseline_sparse.get("status"),
        "metric_deltas": metric_deltas,
        "rejection_reason_deltas": rejection_delta,
        "reasons": reasons,
    }


def _comparison_metric_deltas(current: dict, baseline: dict) -> dict:
    metric_keys = [
        "candidate_decision_count",
        "accepted_decision_count",
        "strong_candidate_count",
        "thin_candidate_ratio",
        "why_case_passed_count",
        "drift_case_passed_count",
    ]
    deltas = {key: _metric_delta(current, baseline, key) for key in metric_keys}
    deltas["limitation_categories"] = _category_delta(current, baseline, "limitation_categories")
    deltas["follow_up_categories"] = _category_delta(current, baseline, "follow_up_categories")
    return deltas


def _comparison_reasons(current: dict | None, baseline: dict | None, movement: str, metric_deltas: dict | None = None) -> list[str]:
    if current is None:
        return ["Repository existed in the baseline snapshot but is missing from the current comparison input."]
    if baseline is None:
        return ["Repository is present in the current comparison input but not in the baseline snapshot."]
    reasons = [
        f"value_outcome: {baseline.get('value_outcome')} -> {current.get('value_outcome')}",
        f"bounded_outcome: {baseline.get('bounded_outcome')} -> {current.get('bounded_outcome')}",
    ]
    if current.get("operational_error_type"):
        reasons.append(f"operational_error: {current.get('operational_error_type')}")
    if movement == "regressed":
        reasons.append("Current bounded value outcome is weaker than the baseline.")
    elif movement == "improved":
        reasons.append("Current bounded value outcome is stronger than the baseline.")
    elif movement == "product-limited":
        reasons.append("Current row remains product-limited and needs product follow-up, not operator setup.")
    if metric_deltas:
        for key in ("candidate_decision_count", "accepted_decision_count", "strong_candidate_count", "thin_candidate_ratio"):
            delta = (metric_deltas.get(key) or {}).get("delta")
            if delta not in (None, 0):
                reasons.append(f"{key} delta: {delta:+g}")
    return reasons


def _classify_benchmark_movement(current: dict | None, baseline: dict | None) -> str:
    if current is None:
        return "missing-from-current"
    if baseline is None:
        return "newly-evaluated"
    current_outcome = str(current.get("value_outcome") or "")
    baseline_outcome = str(baseline.get("value_outcome") or "")
    if current_outcome in OPERATIONAL_VALUE_OUTCOMES or current.get("operational_error_type"):
        return "operationally-blocked"
    current_rank = VALUE_OUTCOME_RANK.get(current_outcome)
    baseline_rank = VALUE_OUTCOME_RANK.get(baseline_outcome)
    if current_rank is None or baseline_rank is None:
        return "needs-review"
    if current_rank > baseline_rank:
        return "improved"
    if current_rank < baseline_rank:
        return "regressed"
    if current_outcome in PRODUCT_LIMITED_VALUE_OUTCOMES:
        return "product-limited"
    return "unchanged"


def compare_benchmark_snapshots(current_snapshot: dict, baseline_snapshot: dict) -> dict:
    current_rows = _rows_by_id(current_snapshot)
    baseline_rows = _rows_by_id(baseline_snapshot)
    repo_ids = sorted(set(current_rows) | set(baseline_rows))
    rows: list[dict] = []
    summary_counts = {movement: 0 for movement in sorted(BENCHMARK_MOVEMENTS)}
    for repo_id in repo_ids:
        current = current_rows.get(repo_id)
        baseline = baseline_rows.get(repo_id)
        movement = _classify_benchmark_movement(current, baseline)
        summary_counts[movement] += 1
        metric_deltas = _comparison_metric_deltas(current, baseline) if current and baseline else {}
        sparse_comparison = _sparse_conversion_comparison(current, baseline)
        row = {
            "id": repo_id,
            "repo": (current or baseline or {}).get("repo"),
            "workspace_slug": (current or baseline or {}).get("workspace_slug"),
            "movement": movement,
            "current_value_outcome": current.get("value_outcome") if current else None,
            "baseline_value_outcome": baseline.get("value_outcome") if baseline else None,
            "current_bounded_outcome": current.get("bounded_outcome") if current else None,
            "baseline_bounded_outcome": baseline.get("bounded_outcome") if baseline else None,
            "metric_deltas": metric_deltas,
            "sparse_conversion": sparse_comparison,
            "reasons": _comparison_reasons(current, baseline, movement, metric_deltas),
        }
        row["reasons"].extend(sparse_comparison["reasons"])
        rows.append(row)
    return {
        "schema_version": BENCHMARK_HISTORY_SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "comparison_type": "real-repo-benchmark-regression",
        "baseline_generated_at": baseline_snapshot.get("generated_at"),
        "current_generated_at": current_snapshot.get("generated_at"),
        "summary": {
            "repositories": len(rows),
            "movements": summary_counts,
            "regressed": summary_counts.get("regressed", 0),
            "improved": summary_counts.get("improved", 0),
            "operationally_blocked": summary_counts.get("operationally-blocked", 0),
            "sparse_movements": {
                "improved": sum(1 for row in rows if row["sparse_conversion"]["movement"] == "improved"),
                "regressed": sum(1 for row in rows if row["sparse_conversion"]["movement"] == "regressed"),
                "operationally_blocked": sum(
                    1 for row in rows if row["sparse_conversion"]["movement"] == "operationally-blocked"
                ),
                "not_provided": sum(1 for row in rows if row["sparse_conversion"]["movement"] == "not_provided"),
            },
            "release_evidence_ready": True,
        },
        "repositories": rows,
    }


def _write_benchmark_comparison_markdown(path: Path, comparison: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = comparison.get("summary") or {}
    movements = summary.get("movements") or {}
    lines = [
        "# Real-Repository Benchmark Regression Comparison",
        "",
        f"- Generated at: `{comparison.get('generated_at', '-')}`",
        f"- Baseline generated at: `{comparison.get('baseline_generated_at', '-')}`",
        f"- Current generated at: `{comparison.get('current_generated_at', '-')}`",
        f"- Repositories: `{summary.get('repositories', 0)}`",
        f"- Improved: `{summary.get('improved', 0)}`",
        f"- Regressed: `{summary.get('regressed', 0)}`",
        f"- Operationally blocked: `{summary.get('operationally_blocked', 0)}`",
        f"- Sparse movements: `{summary.get('sparse_movements', {})}`",
        "",
        "| Repository | Movement | Sparse movement | Value outcome | Bounded outcome | Metric deltas | Reasons |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in comparison.get("repositories", []):
        metric_deltas = row.get("metric_deltas") or {}
        metrics = []
        for key in ("candidate_decision_count", "accepted_decision_count", "strong_candidate_count", "thin_candidate_ratio"):
            delta = (metric_deltas.get(key) or {}).get("delta")
            if delta not in (None, 0):
                metrics.append(f"{key}={delta:+g}")
        lines.append(
            "| "
            + " | ".join(
                _markdown_cell(value)
                for value in (
                    row.get("repo") or row.get("id"),
                    row.get("movement"),
                    (row.get("sparse_conversion") or {}).get("movement"),
                    f"{row.get('baseline_value_outcome')} -> {row.get('current_value_outcome')}",
                    f"{row.get('baseline_bounded_outcome')} -> {row.get('current_bounded_outcome')}",
                    metrics,
                    row.get("reasons") or [],
                )
            )
            + " |"
        )
    lines.append("")
    lines.append("## Movement Counts")
    lines.append("")
    for movement, count in sorted(movements.items()):
        lines.append(f"- {movement}: {count}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _filter_live_repo_inputs(
    *,
    repositories: list[dict],
    why_cases: list[dict],
    drift_cases: list[dict],
    repo_ids: list[str],
) -> tuple[list[dict], list[dict], list[dict]]:
    if not repo_ids:
        return repositories, why_cases, drift_cases

    requested = set(repo_ids)
    known = _repo_ids(repositories)
    unknown = sorted(requested - known)
    if unknown:
        raise ValueError(f"Unknown live benchmark repo id(s): {', '.join(unknown)}")

    return (
        [repository for repository in repositories if repository.get("id") in requested],
        [case for case in why_cases if case.get("repo_id") in requested],
        [case for case in drift_cases if case.get("repo_id") in requested],
    )


def run_live_real_repo_validation(
    *,
    base_url: str,
    repositories: list[dict],
    why_cases: list[dict],
    drift_cases: list[dict],
    report_path: Path,
    markdown_report_path: Path | None = None,
) -> int:
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "base_url": _safe_base_url(base_url),
        "provider": _provider_metadata(base_url),
        "repositories": [],
        "summary": {"repositories": len(repositories), "passed": 0, "failed": 0},
    }
    failures = 0
    why_cases_by_repo: dict[str, list[dict]] = {}
    drift_cases_by_repo: dict[str, list[dict]] = {}
    for case in why_cases:
        why_cases_by_repo.setdefault(case["repo_id"], []).append(case)
    for case in drift_cases:
        drift_cases_by_repo.setdefault(case["repo_id"], []).append(case)

    for repository in repositories:
        query = urlencode({"workspace_slug": repository["workspace_slug"]})
        dashboard_payload, dashboard_error = _json_request(base_url=base_url, path=f"/dashboard/summary?{query}")
        row = {
            "id": repository["id"],
            "repo": repository["repo"],
            "workspace_slug": repository["workspace_slug"],
            "role": repository.get("role"),
            "benchmark_purpose": repository.get("benchmark_purpose"),
            "expectations": {"expected_value_outcomes": repository.get("expectations", {}).get("expected_value_outcomes", [])},
            "passed": False,
            "bounded_outcome": "unknown",
            "value_outcome": "operational_blocked",
            "value_outcome_allowed": False,
            "limitation_categories": [],
            "follow_up_categories": [],
            "key_metrics": {},
            "operational_error": None,
            "dashboard": None,
            "why_cases": [],
            "drift": None,
        }
        if dashboard_error is not None or dashboard_payload is None:
            row["bounded_outcome"] = _operational_outcome(dashboard_error, missing_workspace_on_404=True)
            row["operational_error"] = dashboard_error
            row = _attach_value_summary(row)
            failures += 1
            report["repositories"].append(row)
            print(f"{repository['id']}: outcome={row['bounded_outcome']} passed=False")
            continue

        dashboard_passed, dashboard_row = _evaluate_dashboard_payload(
            repository,
            dashboard_payload,
            report.get("provider"),
        )
        row["bounded_outcome"] = dashboard_row["bounded_outcome"]
        row["dashboard"] = dashboard_row
        repo_passed = dashboard_passed

        candidate_payload, candidate_error = _json_request(
            base_url=base_url,
            path=f"/decisions?{query}&review_state=candidate",
        )
        candidate_quality_passed, candidate_quality_row = _evaluate_candidate_quality(
            repository,
            candidate_payload if isinstance(candidate_payload, list) else None,
            candidate_error,
        )
        row["candidate_quality"] = candidate_quality_row
        repo_passed = repo_passed and candidate_quality_passed

        for case in why_cases_by_repo.get(repository["id"], []):
            why_payload, why_error = _json_request(
                base_url=base_url,
                path="/query/why",
                method="POST",
                body={"workspace_slug": case["workspace_slug"], "question": case["question"]},
            )
            if why_error is not None or why_payload is None:
                case_result = {
                    "id": case["id"],
                    "passed": False,
                    "status": "operational_failure",
                    "operational_error": why_error,
                }
            else:
                passed, reason = _evaluate_why_payload(why_payload, case)
                observations = _why_payload_observations(why_payload, case)
                case_result = {
                    "id": case["id"],
                    "passed": passed,
                    "status": why_payload.get("status"),
                    "citations": len(why_payload.get("citations", [])),
                    "reason": reason,
                    "expected_status": observations["expected_status"],
                    "expected_min_citations": observations["expected_min_citations"],
                    "expected_terms": observations["expected_terms"],
                    "matched_terms": observations["matched_terms"],
                    "expected_primary_title": observations["expected_primary_title"],
                    "observed_primary_title": observations["observed_primary_title"],
                    "primary_thread_match": observations["primary_thread_match"],
                    "readiness_state": ((why_payload.get("answer_context") or {}).get("workspace_readiness") or {}).get(
                        "state"
                    ),
                }
            row["why_cases"].append(case_result)
            repo_passed = repo_passed and bool(case_result["passed"])

        drift_payload, drift_error = _json_request(base_url=base_url, path=f"/drift?{query}")
        repo_drift_cases = drift_cases_by_repo.get(repository["id"], [])
        if drift_error is not None or drift_payload is None:
            drift_result = {
                "passed": False,
                "state": "operational_failure",
                "operational_error": drift_error,
                "cases": [],
            }
        else:
            drift_passed, case_results, drift_state = _evaluate_drift_cases_for_workspace(
                payload=drift_payload,
                cases=repo_drift_cases,
            )
            drift_allowed = (
                drift_state in repository.get("expectations", {}).get("expected_drift_states", [])
                if drift_state
                else True
            )
            drift_result = {
                "passed": drift_passed and drift_allowed,
                "state": drift_state,
                "state_allowed": drift_allowed,
                "cases": case_results,
            }
        row["drift"] = drift_result
        repo_passed = repo_passed and bool(drift_result["passed"])
        row = _attach_value_summary(row)
        repo_passed = repo_passed and bool(row["value_outcome_allowed"])

        row["passed"] = repo_passed
        failures += 0 if repo_passed else 1
        report["repositories"].append(row)
        print(
            f"{repository['id']}: outcome={row['bounded_outcome']} "
            f"readiness={dashboard_row['readiness_state']} drift={row['drift']['state']} passed={repo_passed}"
        )

    report["summary"]["passed"] = len(repositories) - failures
    report["summary"]["failed"] = failures
    _write_report(report_path, report)
    print(f"Live real-repo validation report written to {report_path}")
    if markdown_report_path is not None:
        _write_markdown_report(markdown_report_path, report)
        print(f"Live real-repo Markdown report written to {markdown_report_path}")
    if failures:
        print(f"Live real-repo validation failed for {failures} repositories.", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Run benchmark against a live API endpoint.")
    parser.add_argument(
        "--live-real-repos",
        action="store_true",
        help="Run real-repo readiness, why, and drift benchmark checks against a live API endpoint and existing imported workspaces.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:3001", help="API base URL for live benchmark mode.")
    parser.add_argument("--workspace-slug", default="demo-workspace", help="Workspace slug for live benchmark mode.")
    parser.add_argument(
        "--live-real-repos-report",
        default=".tmp/live-real-repo-validation-report.json",
        help="Output path for the live real-repo validation report.",
    )
    parser.add_argument(
        "--live-real-repos-markdown-report",
        default=".tmp/live-real-repo-validation-report.md",
        help="Output path for the live real-repo Markdown value report.",
    )
    parser.add_argument(
        "--repo-id",
        action="append",
        default=[],
        help="Run live real-repo validation for one repository id. Repeat to include multiple repositories.",
    )
    parser.add_argument(
        "--benchmark-snapshot-source",
        help="Read a live real-repo validation report and write a compact history snapshot.",
    )
    parser.add_argument(
        "--benchmark-snapshot-output",
        help="Output path for --benchmark-snapshot-source.",
    )
    parser.add_argument(
        "--benchmark-compare-current",
        help="Current live report or compact snapshot to compare.",
    )
    parser.add_argument(
        "--benchmark-compare-baseline",
        help="Baseline compact snapshot or live report to compare against.",
    )
    parser.add_argument(
        "--benchmark-compare-output",
        help="Output path for machine-readable benchmark comparison JSON.",
    )
    parser.add_argument(
        "--benchmark-compare-markdown-output",
        help="Optional output path for operator-readable benchmark comparison Markdown.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    workspace_dir = root / "examples" / "demo-workspace"
    live_repo_dir = root / "examples" / "live-benchmarks"
    queries = load_json(workspace_dir / "queries.json")
    expected_answers = load_json(workspace_dir / "expected-answers.json")
    live_repositories = load_json(live_repo_dir / "repositories.json")
    why_cases = load_json(live_repo_dir / "why-cases.json")
    drift_cases = load_json(live_repo_dir / "drift-cases.json")

    fixture_status = validate_fixtures(queries, expected_answers)
    if fixture_status != 0:
        return fixture_status

    live_repo_status = validate_live_repo_set(live_repositories)
    if live_repo_status != 0:
        return live_repo_status

    why_case_status = validate_why_cases(why_cases, live_repositories)
    if why_case_status != 0:
        return why_case_status

    drift_case_status = validate_drift_cases(drift_cases, live_repositories)
    if drift_case_status != 0:
        return drift_case_status

    if args.benchmark_snapshot_source:
        if not args.benchmark_snapshot_output:
            print("--benchmark-snapshot-output is required with --benchmark-snapshot-source.", file=sys.stderr)
            return 1
        try:
            source_report = _load_json_object((root / args.benchmark_snapshot_source).resolve())
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"Failed to read benchmark snapshot source: {exc}", file=sys.stderr)
            return 1
        snapshot = _snapshot_from_report_or_snapshot(source_report)
        validation_status = validate_benchmark_history_snapshot(snapshot)
        if validation_status != 0:
            return validation_status
        output_path = (root / args.benchmark_snapshot_output).resolve()
        _write_report(output_path, snapshot)
        print(f"Real-repo benchmark history snapshot written to {output_path}")
        return 0

    if args.benchmark_compare_current or args.benchmark_compare_baseline:
        if not args.benchmark_compare_current or not args.benchmark_compare_baseline or not args.benchmark_compare_output:
            print(
                "--benchmark-compare-current, --benchmark-compare-baseline, and --benchmark-compare-output are required together.",
                file=sys.stderr,
            )
            return 1
        try:
            current_payload = _load_json_object((root / args.benchmark_compare_current).resolve())
            baseline_payload = _load_json_object((root / args.benchmark_compare_baseline).resolve())
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"Failed to read benchmark comparison input: {exc}", file=sys.stderr)
            return 1
        current_snapshot = _snapshot_from_report_or_snapshot(current_payload)
        baseline_snapshot = _snapshot_from_report_or_snapshot(baseline_payload)
        if validate_benchmark_history_snapshot(current_snapshot) != 0:
            return 1
        if validate_benchmark_history_snapshot(baseline_snapshot) != 0:
            return 1
        comparison = compare_benchmark_snapshots(current_snapshot=current_snapshot, baseline_snapshot=baseline_snapshot)
        output_path = (root / args.benchmark_compare_output).resolve()
        _write_report(output_path, comparison)
        print(f"Real-repo benchmark comparison written to {output_path}")
        if args.benchmark_compare_markdown_output:
            markdown_path = (root / args.benchmark_compare_markdown_output).resolve()
            _write_benchmark_comparison_markdown(markdown_path, comparison)
            print(f"Real-repo benchmark comparison Markdown written to {markdown_path}")
        return 0

    if args.live_real_repos:
        try:
            filtered_repositories, filtered_why_cases, filtered_drift_cases = _filter_live_repo_inputs(
                repositories=live_repositories,
                why_cases=why_cases,
                drift_cases=drift_cases,
                repo_ids=args.repo_id,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        return run_live_real_repo_validation(
            base_url=args.base_url,
            repositories=filtered_repositories,
            why_cases=filtered_why_cases,
            drift_cases=filtered_drift_cases,
            report_path=(root / args.live_real_repos_report).resolve(),
            markdown_report_path=(root / args.live_real_repos_markdown_report).resolve(),
        )

    if not args.live:
        return 0

    return run_live_benchmark(
        base_url=args.base_url,
        workspace_slug=args.workspace_slug,
        queries=queries,
        expected_answers=expected_answers,
    )


if __name__ == "__main__":
    raise SystemExit(main())
