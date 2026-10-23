"""Run offline rule regression; exit 1 for expectation failures, 2 for bad input."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "engine"))
from app.extractor.evidence import evaluate_evidence

DEFAULT_FIXTURES = ROOT / "services/engine/tests/fixtures/decision_evidence/cases.json"
AUDIT = ROOT / "docs/validation/2026-10-21-pallets-click-eight-candidate-independent-audit.json"


def historical_candidates() -> list[dict]:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    return [{
        "id": f"click-{row['id']}", "title": row["title"],
        **audit["candidate_fields_shared"], "provider_kind": "fake",
        "historical_ai_classification": row["classification"],
        "citations": [{"url": row["verified_at_fixed_sha_url"],
                       "revision": audit["github_source_sha"],
                       "kind": "pull_request" if row["id"] == 6 else "document",
                       **({"merged": False} if row["id"] == 6 else {})}],
    } for row in audit["evaluations"]]


def build_report(fixture: dict) -> dict:
    if not isinstance(fixture, dict):
        raise ValueError("fixture must be an object")
    cases = fixture.get("cases")
    if fixture.get("schema_version") != 1 or not isinstance(cases, list) or not cases:
        raise ValueError("expected schema_version=1 and nonempty cases")
    results = []
    identifiers = set()
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("candidate"), dict):
            raise ValueError("each case requires a candidate object")
        candidate = case["candidate"]
        identifier = candidate.get("id")
        if not isinstance(identifier, str) or not identifier or identifier in identifiers:
            raise ValueError("candidate IDs must be unique nonempty strings")
        identifiers.add(identifier)
        if candidate.get("provider_kind") not in {"synthetic", "fake", "live"}:
            raise ValueError("candidate provider_kind is required")
        expected = case.get("expected")
        if not isinstance(expected, dict) or expected.get("diagnostic_status") not in {"fail", "review_required"}:
            raise ValueError("each case requires a diagnostic expectation")
        reasons = expected.get("reasons")
        if not isinstance(reasons, list) or not reasons or any(not isinstance(r, str) for r in reasons):
            raise ValueError("each case requires expected reason codes")
        result = evaluate_evidence(candidate)
        actual_reasons = {check["reason"] for check in result["checks"]}
        result["regression_status"] = "pass" if result["diagnostic_status"] == expected["diagnostic_status"] and set(reasons) <= actual_reasons else "fail"
        result["expected"] = expected
        results.append(result)
    observations = []
    for candidate in historical_candidates():
        result = evaluate_evidence(candidate)
        result["historical_ai_classification"] = candidate["historical_ai_classification"]
        observations.append(result)
    return {
        "schema_version": 1,
        "scope": "offline_supplied_snapshots_only",
        "regression": {"total": len(results), **dict(Counter(r["regression_status"] for r in results))},
        "provider_counts": dict(Counter(r["provider_kind"] for r in results + observations)),
        "human_review": "not_run", "model_accuracy": "not_evaluated",
        "historical_source": str(AUDIT.relative_to(ROOT)).replace("\\", "/"),
        "historical_observation_count": len(observations),
        "results": results, "historical_observations": observations,
    }


def markdown(report: dict) -> str:
    lines = ["# Offline decision evidence regression", "",
             "Rule regression only. Human review: **not_run**. Model accuracy: **not_evaluated**.",
             "Historical AI classifications are observations, not human gold labels.", "",
             f"Regression counts: `{json.dumps(report['regression'], sort_keys=True)}`",
             f"Provider counts: `{json.dumps(report['provider_counts'], sort_keys=True)}`", "",
             "| Candidate | Diagnostic | Regression | Reasons |",
             "| --- | --- | --- | --- |"]
    def escape(value: object) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")
    for row in report["results"] + report["historical_observations"]:
        reasons = sorted({c["reason"] for c in row["checks"] if c["status"] != "pass"})
        cells = [row["id"], row["diagnostic_status"], row.get("regression_status", "not_evaluated"), ", ".join(reasons)]
        lines.append("| " + " | ".join(map(escape, cells)) + " |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/offline-evidence")
    args = parser.parse_args()
    try:
        report = build_report(json.loads(args.fixtures.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Invalid evidence fixture: {exc}", file=sys.stderr)
        return 2
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (args.output / "report.md").write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report["regression"], sort_keys=True))
    return 1 if report["regression"].get("fail", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
