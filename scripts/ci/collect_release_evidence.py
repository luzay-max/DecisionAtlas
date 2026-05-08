from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
STATUS_PASSED = "passed"
STATUS_FAILED = "failed"
STATUS_WARNING = "warning"
STATUS_CAUTION = "caution"
STATUS_MISSING = "missing"
STATUS_NOT_PROVIDED = "not_provided"
STATUS_UNKNOWN = "unknown"

PASS_STATUSES = {"pass", "passed", "success", "succeeded", "ok", "clean", "continue", "true"}
FAIL_STATUSES = {"fail", "failed", "failure", "error", "blocked", "false"}
WARNING_STATUSES = {"warn", "warning", "warnings", "caution", "pause", "needs_review", "needs-review"}
MISSING_STATUSES = {"missing", "not_found", "not-found"}
NOT_PROVIDED_STATUSES = {"", "none", "not_provided", "not-provided", "not provided"}
ADVISORY_NON_CLEAN = {STATUS_FAILED, STATUS_WARNING, STATUS_CAUTION, "pause", STATUS_MISSING, STATUS_NOT_PROVIDED, STATUS_UNKNOWN}


@dataclass(frozen=True)
class SourceInput:
    id: str
    label: str
    category: str
    required: bool
    status: str | None = None
    path: Path | None = None
    command: str | None = None


def normalize_status(value: Any) -> str:
    if isinstance(value, bool):
        return STATUS_PASSED if value else STATUS_FAILED
    if value is None:
        return STATUS_NOT_PROVIDED
    normalized = str(value).strip().lower().replace(" ", "_")
    if normalized in PASS_STATUSES:
        return STATUS_PASSED
    if normalized in FAIL_STATUSES:
        return STATUS_FAILED
    if normalized == STATUS_CAUTION:
        return STATUS_CAUTION
    if normalized in WARNING_STATUSES:
        return STATUS_WARNING if normalized != "pause" else "pause"
    if normalized in MISSING_STATUSES:
        return STATUS_MISSING
    if normalized in NOT_PROVIDED_STATUSES:
        return STATUS_NOT_PROVIDED
    return normalized or STATUS_UNKNOWN


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, f"Failed to read {path}: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"Failed to parse JSON from {path}: {exc}"
    if not isinstance(data, dict):
        return None, f"Expected JSON object in {path}."
    return data, None


def _status_from_generic_report(data: dict[str, Any]) -> tuple[str, str]:
    for key in ("status", "overall_status", "outcome", "result"):
        if key in data:
            return normalize_status(data.get(key)), f"{key}={data.get(key)}"
    if "passed" in data:
        return normalize_status(data.get("passed")), f"passed={data.get('passed')}"
    if "success" in data:
        return normalize_status(data.get("success")), f"success={data.get('success')}"

    summary = data.get("summary")
    if isinstance(summary, dict):
        failed = summary.get("failed")
        if isinstance(failed, int):
            return (STATUS_FAILED if failed > 0 else STATUS_PASSED), f"summary.failed={failed}"
        if "status" in summary:
            return normalize_status(summary.get("status")), f"summary.status={summary.get('status')}"

    return STATUS_UNKNOWN, "No supported status field found."


def _status_from_guardrail(data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    agent_status = normalize_status(data.get("agent_status"))
    context = data.get("context") if isinstance(data.get("context"), dict) else {}
    handoff = data.get("handoff_summary") if isinstance(data.get("handoff_summary"), dict) else {}
    details = {
        "agent_status": data.get("agent_status"),
        "diff_status": context.get("diff_status") or handoff.get("diff_status"),
        "drift_status": context.get("drift_status") or handoff.get("drift_status"),
        "advisory_only": context.get("advisory_only") if "advisory_only" in context else handoff.get("advisory_only"),
        "summary": data.get("summary"),
    }
    return agent_status, details


def _status_from_benchmark_comparison(data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    regressed = int(summary.get("regressed") or 0)
    operationally_blocked = int(summary.get("operationally_blocked") or 0)
    status = STATUS_WARNING if regressed or operationally_blocked else STATUS_PASSED
    details = {
        "comparison_type": data.get("comparison_type"),
        "repositories": summary.get("repositories"),
        "regressed": regressed,
        "operationally_blocked": operationally_blocked,
        "improved": summary.get("improved"),
        "release_evidence_ready": summary.get("release_evidence_ready"),
    }
    return status, details


def build_evidence_item(source: SourceInput, root: Path) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    item: dict[str, Any] = {
        "id": source.id,
        "label": source.label,
        "category": source.category,
        "required": source.required,
        "status": STATUS_NOT_PROVIDED,
        "source_path": None,
        "command": source.command,
        "details": {},
    }

    if source.path is not None:
        path = source.path if source.path.is_absolute() else root / source.path
        item["source_path"] = str(path)
        if not path.exists():
            status = STATUS_MISSING if source.required else STATUS_WARNING
            item["status"] = status
            item["details"] = {"reason": "provided_source_path_missing"}
            warnings.append(f"{source.label} source path does not exist: {path}")
            return item, warnings

        data, error = _read_json(path)
        if error is not None:
            status = STATUS_FAILED if source.required else STATUS_WARNING
            item["status"] = status
            item["details"] = {"reason": "provided_source_path_unreadable", "error": error}
            warnings.append(error)
            return item, warnings

        if source.id == "governance_guardrail":
            item["status"], item["details"] = _status_from_guardrail(data or {})
            return item, warnings
        if source.id == "real_repo_benchmark_comparison":
            item["status"], item["details"] = _status_from_benchmark_comparison(data or {})
            return item, warnings

        status, reason = _status_from_generic_report(data or {})
        item["status"] = status
        item["details"] = {"reason": reason}
        return item, warnings

    if source.status is not None:
        item["status"] = normalize_status(source.status)
        item["details"] = {"reason": "explicit_status"}
        return item, warnings

    item["status"] = STATUS_MISSING if source.required else STATUS_NOT_PROVIDED
    item["details"] = {"reason": "no_status_or_source_path_provided"}
    return item, warnings


def calculate_overall_status(required_gates: list[dict[str, Any]], advisory_signals: list[dict[str, Any]]) -> str:
    required_statuses = {item["status"] for item in required_gates}
    advisory_statuses = {item["status"] for item in advisory_signals}
    if required_statuses & {STATUS_FAILED, STATUS_WARNING, STATUS_CAUTION, "pause", STATUS_UNKNOWN}:
        return STATUS_FAILED
    if required_statuses & {STATUS_MISSING, STATUS_NOT_PROVIDED}:
        return "incomplete"
    if advisory_statuses & ADVISORY_NON_CLEAN:
        return STATUS_WARNING
    return STATUS_PASSED


def build_bundle(sources: list[SourceInput], *, root: Path, generated_at: str | None = None) -> dict[str, Any]:
    required_gates: list[dict[str, Any]] = []
    advisory_signals: list[dict[str, Any]] = []
    warnings: list[str] = []
    source_paths: dict[str, str] = {}
    missing_inputs: list[dict[str, Any]] = []

    for source in sources:
        item, item_warnings = build_evidence_item(source, root)
        warnings.extend(item_warnings)
        if item.get("source_path"):
            source_paths[item["id"]] = item["source_path"]
        if item["status"] in {STATUS_MISSING, STATUS_NOT_PROVIDED}:
            missing_inputs.append(
                {
                    "id": item["id"],
                    "label": item["label"],
                    "required": item["required"],
                    "status": item["status"],
                }
            )
        if item["required"]:
            required_gates.append(item)
        else:
            advisory_signals.append(item)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "overall_status": calculate_overall_status(required_gates, advisory_signals),
        "required_gates": required_gates,
        "advisory_signals": advisory_signals,
        "evidence_items": required_gates + advisory_signals,
        "missing_inputs": missing_inputs,
        "warnings": warnings,
        "source_paths": source_paths,
    }


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, list):
        return "<br>".join(_markdown_cell(item) for item in value) or "-"
    if isinstance(value, dict):
        text = json.dumps(value, sort_keys=True)
    else:
        text = str(value)
    text = text.replace("|", "\\|").replace("\n", "<br>")
    return text or "-"


def render_markdown(bundle: dict[str, Any]) -> str:
    lines = [
        "# Release Evidence",
        "",
        f"- Generated at: `{bundle.get('generated_at')}`",
        f"- Schema version: `{bundle.get('schema_version')}`",
        f"- Overall status: `{bundle.get('overall_status')}`",
        "",
        "## Required Gates",
        "",
        "| Gate | Status | Source | Details |",
        "| --- | --- | --- | --- |",
    ]
    for item in bundle.get("required_gates", []):
        lines.append(
            "| "
            + " | ".join(
                _markdown_cell(value)
                for value in (
                    item.get("label"),
                    item.get("status"),
                    item.get("source_path") or item.get("command"),
                    item.get("details"),
                )
            )
            + " |"
        )

    lines.extend(["", "## Advisory Signals", "", "| Signal | Status | Source | Details |", "| --- | --- | --- | --- |"])
    for item in bundle.get("advisory_signals", []):
        lines.append(
            "| "
            + " | ".join(
                _markdown_cell(value)
                for value in (
                    item.get("label"),
                    item.get("status"),
                    item.get("source_path") or item.get("command"),
                    item.get("details"),
                )
            )
            + " |"
        )

    lines.extend(["", "## Missing Inputs", ""])
    missing = bundle.get("missing_inputs") or []
    if missing:
        for item in missing:
            lines.append(f"- `{item.get('id')}`: {item.get('status')} (required={item.get('required')})")
    else:
        lines.append("- None")

    lines.extend(["", "## Warnings", ""])
    warnings = bundle.get("warnings") or []
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- None")

    lines.extend(["", "## Source Paths", ""])
    source_paths = bundle.get("source_paths") or {}
    if source_paths:
        for key, value in sorted(source_paths.items()):
            lines.append(f"- `{key}`: `{value}`")
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: Path, markdown: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _build_sources(args: argparse.Namespace) -> list[SourceInput]:
    return [
        SourceInput(
            id="canonical_pre_release",
            label="Canonical pre-release baseline",
            category="required_gate",
            required=True,
            status=args.pre_release_status,
            path=Path(args.pre_release_source) if args.pre_release_source else None,
            command="powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ci/pre-release.ps1",
        ),
        SourceInput(
            id="openspec_strict_validation",
            label="OpenSpec strict validation",
            category="required_gate",
            required=True,
            status=args.openspec_status,
            path=Path(args.openspec_source) if args.openspec_source else None,
            command="openspec validate --all --strict",
        ),
        SourceInput(
            id="offline_benchmark_validation",
            label="Offline benchmark fixture validation",
            category="required_gate",
            required=True,
            status=args.offline_benchmark_status,
            path=Path(args.offline_benchmark_source) if args.offline_benchmark_source else None,
            command="python scripts/ci/run_benchmark.py",
        ),
        SourceInput(
            id="governance_guardrail",
            label="Governance guardrail",
            category="advisory_signal",
            required=False,
            status=args.guardrail_status,
            path=Path(args.guardrail_report) if args.guardrail_report else None,
            command="python scripts/governance/agent_guardrail.py",
        ),
        SourceInput(
            id="targeted_tests",
            label="Targeted test summary",
            category="advisory_signal",
            required=False,
            status=args.targeted_tests_status,
            path=Path(args.targeted_tests_report) if args.targeted_tests_report else None,
        ),
        SourceInput(
            id="real_repo_benchmark_comparison",
            label="Real-repo benchmark comparison",
            category="advisory_signal",
            required=False,
            path=Path(args.benchmark_comparison_report) if args.benchmark_comparison_report else None,
            command=(
                "python scripts/ci/run_benchmark.py --benchmark-compare-current <current> "
                "--benchmark-compare-baseline <baseline> --benchmark-compare-output <output>"
            ),
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect local DecisionAtlas release evidence into JSON and Markdown.")
    parser.add_argument("--output", default=".tmp/release-evidence.json", help="Output path for machine-readable evidence JSON.")
    parser.add_argument("--markdown-output", default=".tmp/release-evidence.md", help="Output path for operator-readable Markdown.")
    parser.add_argument("--generated-at", help="Override generated_at timestamp for deterministic tests.")
    parser.add_argument("--pre-release-status", help="Explicit canonical pre-release status.")
    parser.add_argument("--pre-release-source", help="Explicit JSON source for canonical pre-release evidence.")
    parser.add_argument("--openspec-status", help="Explicit OpenSpec strict validation status.")
    parser.add_argument("--openspec-source", help="Explicit JSON source for OpenSpec validation evidence.")
    parser.add_argument("--offline-benchmark-status", help="Explicit offline benchmark fixture validation status.")
    parser.add_argument("--offline-benchmark-source", help="Explicit JSON source for offline benchmark fixture validation.")
    parser.add_argument("--guardrail-status", help="Explicit governance guardrail status when no JSON report is supplied.")
    parser.add_argument("--guardrail-report", help="Explicit JSON report from scripts/governance/agent_guardrail.py.")
    parser.add_argument("--targeted-tests-status", help="Explicit targeted test status when no JSON report is supplied.")
    parser.add_argument("--targeted-tests-report", help="Explicit JSON report for targeted tests.")
    parser.add_argument("--benchmark-comparison-report", help="Explicit JSON real-repo benchmark comparison report.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    bundle = build_bundle(_build_sources(args), root=root, generated_at=args.generated_at)
    output_path = Path(args.output)
    markdown_path = Path(args.markdown_output)
    if not output_path.is_absolute():
        output_path = root / output_path
    if not markdown_path.is_absolute():
        markdown_path = root / markdown_path

    _write_json(output_path, bundle)
    _write_markdown(markdown_path, render_markdown(bundle))
    print(f"Release evidence JSON written to {output_path}")
    print(f"Release evidence Markdown written to {markdown_path}")
    print(f"Overall status: {bundle['overall_status']}")
    return 1 if bundle["overall_status"] == STATUS_FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
