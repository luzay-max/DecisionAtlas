from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
STATUS_PASS = "pass"
STATUS_BLOCKING = "blocking"
STATUS_NON_BLOCKING = "non_blocking"
STATUS_KNOWN_LIMITATION = "known_limitation"
STATUS_OPERATOR_GUIDED = "operator_guided"
STATUS_NOT_PROVIDED = "not_provided"
STATUS_WARNING = "warning"
STATUS_UNKNOWN = "unknown"

PASS_STATUSES = {"pass", "passed", "ok", "success", "succeeded", "ready", "continue", "true"}
BLOCKING_STATUSES = {"block", "blocked", "blocking", "fail", "failed", "failure", "error", "false"}
NON_BLOCKING_STATUSES = {"non_blocking", "non-blocking", "nonblocking", "caution", "warn", "warning"}
KNOWN_LIMITATION_STATUSES = {"known_limitation", "known-limitation", "limitation", "unavailable"}
OPERATOR_GUIDED_STATUSES = {"operator_guided", "operator-guided", "manual", "operator"}
NOT_PROVIDED_STATUSES = {"", "none", "not_provided", "not-provided", "not provided", "missing"}


@dataclass(frozen=True)
class LaneInput:
    id: str
    label: str
    group: str
    required_for_public_walkthrough: bool
    status: str | None = None
    path: Path | None = None
    command: str | None = None
    default_when_missing: str = STATUS_NOT_PROVIDED
    recommended_next_action: str | None = None


def normalize_status(value: Any) -> str:
    if isinstance(value, bool):
        return STATUS_PASS if value else STATUS_BLOCKING
    if value is None:
        return STATUS_NOT_PROVIDED
    normalized = str(value).strip().lower().replace(" ", "_")
    if normalized in PASS_STATUSES:
        return STATUS_PASS
    if normalized in BLOCKING_STATUSES:
        return STATUS_BLOCKING
    if normalized in NON_BLOCKING_STATUSES:
        return STATUS_NON_BLOCKING if normalized != "warning" else STATUS_WARNING
    if normalized in KNOWN_LIMITATION_STATUSES:
        return STATUS_KNOWN_LIMITATION
    if normalized in OPERATOR_GUIDED_STATUSES:
        return STATUS_OPERATOR_GUIDED
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


def _status_from_report(data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if "ready" in data:
        return normalize_status(data.get("ready")), {"reason": f"ready={data.get('ready')}", "summary": data.get("summary")}
    for key in ("status", "overall_status", "public_walkthrough_status", "result", "outcome"):
        if key in data:
            return normalize_status(data.get(key)), {"reason": f"{key}={data.get(key)}"}
    if "passed" in data:
        return normalize_status(data.get("passed")), {"reason": f"passed={data.get('passed')}"}

    summary = data.get("summary")
    if isinstance(summary, dict):
        if isinstance(summary.get("failed"), int):
            failed = int(summary.get("failed") or 0)
            return (STATUS_BLOCKING if failed else STATUS_PASS), {"reason": f"summary.failed={failed}"}
        if "status" in summary:
            return normalize_status(summary.get("status")), {"reason": f"summary.status={summary.get('status')}"}

    return STATUS_UNKNOWN, {"reason": "no_supported_status_field"}


def _status_from_guardrail(data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    agent_status = str(data.get("agent_status") or "").lower()
    if agent_status == "pause":
        status = STATUS_BLOCKING
    elif agent_status == "caution":
        status = STATUS_NON_BLOCKING
    elif agent_status == "continue":
        status = STATUS_PASS
    else:
        status = normalize_status(agent_status)
    return status, {
        "agent_status": data.get("agent_status"),
        "summary": data.get("summary"),
        "handoff_summary": data.get("handoff_summary"),
    }


def _status_from_release_evidence(data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    overall = str(data.get("overall_status") or "").lower()
    if overall == "failed":
        status = STATUS_BLOCKING
    elif overall in {"warning", "incomplete"}:
        status = STATUS_NON_BLOCKING
    else:
        status = normalize_status(overall)
    return status, {
        "overall_status": data.get("overall_status"),
        "missing_inputs": data.get("missing_inputs"),
        "warnings": data.get("warnings"),
    }


def _status_from_real_repo_evidence(data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    failed = int(summary.get("failed") or 0)
    regressed = int(summary.get("regressed") or 0)
    operationally_blocked = int(summary.get("operationally_blocked") or 0)
    status = STATUS_NON_BLOCKING if failed or regressed or operationally_blocked else STATUS_PASS
    return status, {
        "comparison_type": data.get("comparison_type"),
        "repositories": summary.get("repositories"),
        "failed": failed,
        "regressed": regressed,
        "operationally_blocked": operationally_blocked,
    }


def build_lane(lane_input: LaneInput, root: Path) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    lane: dict[str, Any] = {
        "id": lane_input.id,
        "label": lane_input.label,
        "group": lane_input.group,
        "required_for_public_walkthrough": lane_input.required_for_public_walkthrough,
        "status": lane_input.default_when_missing,
        "source_path": None,
        "command": lane_input.command,
        "details": {"reason": "no_status_or_source_path_provided"},
        "recommended_next_action": lane_input.recommended_next_action,
    }

    if lane_input.path is not None:
        path = lane_input.path if lane_input.path.is_absolute() else root / lane_input.path
        lane["source_path"] = str(path)
        if not path.exists():
            lane["status"] = STATUS_BLOCKING if lane_input.required_for_public_walkthrough else STATUS_NON_BLOCKING
            lane["details"] = {"reason": "provided_source_path_missing"}
            warnings.append(f"{lane_input.label} source path does not exist: {path}")
            return lane, warnings
        data, error = _read_json(path)
        if error is not None:
            lane["status"] = STATUS_BLOCKING if lane_input.required_for_public_walkthrough else STATUS_NON_BLOCKING
            lane["details"] = {"reason": "provided_source_path_unreadable", "error": error}
            warnings.append(error)
            return lane, warnings
        if lane_input.id == "governance_guardrail":
            lane["status"], lane["details"] = _status_from_guardrail(data or {})
        elif lane_input.id == "release_evidence":
            lane["status"], lane["details"] = _status_from_release_evidence(data or {})
        elif lane_input.id == "real_repo_evidence":
            lane["status"], lane["details"] = _status_from_real_repo_evidence(data or {})
        else:
            lane["status"], lane["details"] = _status_from_report(data or {})
        return lane, warnings

    if lane_input.status is not None:
        lane["status"] = normalize_status(lane_input.status)
        lane["details"] = {"reason": "explicit_status"}
    return lane, warnings


def calculate_public_walkthrough_status(lanes: list[dict[str, Any]]) -> str:
    required = [lane for lane in lanes if lane.get("required_for_public_walkthrough")]
    statuses = {str(lane.get("status")) for lane in required}
    if STATUS_BLOCKING in statuses:
        return STATUS_BLOCKING
    if statuses & {STATUS_OPERATOR_GUIDED, STATUS_KNOWN_LIMITATION, STATUS_NOT_PROVIDED, STATUS_UNKNOWN}:
        return STATUS_OPERATOR_GUIDED
    if statuses & {STATUS_NON_BLOCKING, STATUS_WARNING}:
        return STATUS_WARNING
    return STATUS_PASS


def build_bundle(
    lane_inputs: list[LaneInput],
    *,
    root: Path,
    generated_at: str | None = None,
    hosted_urls: dict[str, str | None] | None = None,
) -> dict[str, Any]:
    lanes: list[dict[str, Any]] = []
    warnings: list[str] = []
    source_paths: dict[str, str] = {}
    missing_inputs: list[dict[str, Any]] = []
    recommended_next_actions: list[str] = []

    for lane_input in lane_inputs:
        lane, lane_warnings = build_lane(lane_input, root)
        lanes.append(lane)
        warnings.extend(lane_warnings)
        if lane.get("source_path"):
            source_paths[str(lane["id"])] = str(lane["source_path"])
        if lane["status"] in {STATUS_NOT_PROVIDED, STATUS_OPERATOR_GUIDED, STATUS_KNOWN_LIMITATION}:
            missing_inputs.append(
                {
                    "id": lane["id"],
                    "label": lane["label"],
                    "status": lane["status"],
                    "required_for_public_walkthrough": lane["required_for_public_walkthrough"],
                }
            )
        if lane.get("recommended_next_action"):
            recommended_next_actions.append(str(lane["recommended_next_action"]))

    public_status = calculate_public_walkthrough_status(lanes)
    blockers = [
        lane
        for lane in lanes
        if lane.get("required_for_public_walkthrough") and lane.get("status") == STATUS_BLOCKING
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "hosted_urls": hosted_urls or {},
        "overall_status": STATUS_BLOCKING if blockers else public_status,
        "public_walkthrough_status": public_status,
        "public_walkthrough_decision": _public_decision(public_status),
        "lanes": lanes,
        "blockers": blockers,
        "missing_inputs": missing_inputs,
        "warnings": warnings,
        "recommended_next_actions": sorted(set(recommended_next_actions)),
        "source_paths": source_paths,
        "recovery_scope": "Default reset/reseed recovery is scoped to demo-workspace and does not implicitly delete imported workspaces or governance history.",
        "release_gate_note": "Hosted readiness is operator-guided evidence for a running environment and does not replace scripts/ci/pre-release.ps1.",
    }


def _public_decision(public_status: str) -> str:
    if public_status == STATUS_BLOCKING:
        return "do_not_proceed"
    if public_status == STATUS_PASS:
        return "proceed"
    return "operator_review_required"


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, list):
        return "<br>".join(_markdown_cell(item) for item in value) or "-"
    if isinstance(value, dict):
        text = json.dumps(value, sort_keys=True)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>") or "-"


def render_markdown(bundle: dict[str, Any]) -> str:
    lines = [
        "# Hosted Operator Readiness",
        "",
        f"- Generated at: `{bundle.get('generated_at')}`",
        f"- Schema version: `{bundle.get('schema_version')}`",
        f"- Overall status: `{bundle.get('overall_status')}`",
        f"- Public walkthrough status: `{bundle.get('public_walkthrough_status')}`",
        f"- Public walkthrough decision: `{bundle.get('public_walkthrough_decision')}`",
        "",
        "## Lane Status",
        "",
        "| Lane | Group | Required public walkthrough | Status | Source | Details |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for lane in bundle.get("lanes", []):
        lines.append(
            "| "
            + " | ".join(
                _markdown_cell(value)
                for value in (
                    lane.get("label"),
                    lane.get("group"),
                    lane.get("required_for_public_walkthrough"),
                    lane.get("status"),
                    lane.get("source_path") or lane.get("command"),
                    lane.get("details"),
                )
            )
            + " |"
        )

    lines.extend(["", "## Blockers", ""])
    blockers = bundle.get("blockers") or []
    if blockers:
        for blocker in blockers:
            lines.append(f"- `{blocker.get('id')}`: {blocker.get('label')}")
    else:
        lines.append("- None")

    lines.extend(["", "## Missing Or Operator-Guided Inputs", ""])
    missing = bundle.get("missing_inputs") or []
    if missing:
        for item in missing:
            lines.append(f"- `{item.get('id')}`: {item.get('status')} (required_public={item.get('required_for_public_walkthrough')})")
    else:
        lines.append("- None")

    lines.extend(["", "## Recommended Next Actions", ""])
    actions = bundle.get("recommended_next_actions") or []
    if actions:
        for action in actions:
            lines.append(f"- {action}")
    else:
        lines.append("- None")

    lines.extend(["", "## Warnings", ""])
    warnings = bundle.get("warnings") or []
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- None")

    lines.extend(["", "## Rerun Commands", ""])
    lines.extend(
        [
            "- Health: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/health-check.ps1 -WebBaseUrl <web> -ApiBaseUrl <api> -EngineBaseUrl <engine>`",
            "- Smoke: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/smoke-check.ps1 -WebBaseUrl <web> -ApiBaseUrl <api> -EngineBaseUrl <engine>`",
            "- Seeded readiness: `python scripts/demo/check_seeded_demo.py --json`",
            "- Reset: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/reset-demo.ps1`",
            "- Reseed: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/reseed-demo.ps1`",
            "- Guardrail: `python scripts/governance/agent_guardrail.py --summary`",
        ]
    )

    lines.extend(["", "## Scope Notes", ""])
    lines.append(f"- {bundle.get('recovery_scope')}")
    lines.append(f"- {bundle.get('release_gate_note')}")
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: Path, markdown: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _url_lane(
    *,
    lane_id: str,
    label: str,
    url: str | None,
    status: str | None,
    command: str,
    next_action: str,
) -> LaneInput:
    if status is not None:
        default = STATUS_NOT_PROVIDED
    elif url:
        default = STATUS_OPERATOR_GUIDED
    else:
        default = STATUS_OPERATOR_GUIDED
    return LaneInput(
        id=lane_id,
        label=label,
        group="core_hosted_services",
        required_for_public_walkthrough=True,
        status=status,
        command=command,
        default_when_missing=default,
        recommended_next_action=next_action,
    )


def _build_lanes(args: argparse.Namespace) -> list[LaneInput]:
    return [
        _url_lane(
            lane_id="web_hosted_url",
            label="Hosted web URL",
            url=args.web_base_url,
            status=args.web_status,
            command="scripts/demo/health-check.ps1 -WebBaseUrl <web>",
            next_action="Run hosted health check against the web URL before external preview.",
        ),
        _url_lane(
            lane_id="api_hosted_url",
            label="Hosted API URL",
            url=args.api_base_url,
            status=args.api_status,
            command="scripts/demo/health-check.ps1 -ApiBaseUrl <api>",
            next_action="Run hosted health check against the API URL before external preview.",
        ),
        _url_lane(
            lane_id="engine_hosted_url",
            label="Hosted engine URL",
            url=args.engine_base_url,
            status=args.engine_status,
            command="scripts/demo/health-check.ps1 -EngineBaseUrl <engine>",
            next_action="Run hosted health check against the engine URL before external preview.",
        ),
        LaneInput(
            id="hosted_health_check",
            label="Hosted health check",
            group="core_hosted_services",
            required_for_public_walkthrough=True,
            status=args.health_status,
            path=Path(args.health_report) if args.health_report else None,
            command="powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/health-check.ps1",
            default_when_missing=STATUS_OPERATOR_GUIDED,
            recommended_next_action="Run scripts/demo/health-check.ps1 with hosted URLs.",
        ),
        LaneInput(
            id="hosted_smoke_check",
            label="Hosted guided-demo smoke check",
            group="public_walkthrough",
            required_for_public_walkthrough=True,
            status=args.smoke_status,
            path=Path(args.smoke_report) if args.smoke_report else None,
            command="powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/smoke-check.ps1",
            default_when_missing=STATUS_OPERATOR_GUIDED,
            recommended_next_action="Run scripts/demo/smoke-check.ps1 with hosted URLs.",
        ),
        LaneInput(
            id="seeded_demo_readiness",
            label="Seeded demo readiness",
            group="public_walkthrough",
            required_for_public_walkthrough=True,
            status=args.seeded_readiness_status,
            path=Path(args.seeded_readiness_report) if args.seeded_readiness_report else None,
            command="python scripts/demo/check_seeded_demo.py --json",
            default_when_missing=STATUS_OPERATOR_GUIDED,
            recommended_next_action="Run python scripts/demo/check_seeded_demo.py --json before external preview.",
        ),
        LaneInput(
            id="recovery_drill",
            label="Reset/reseed recovery drill",
            group="recovery",
            required_for_public_walkthrough=False,
            status=args.recovery_status,
            path=Path(args.recovery_report) if args.recovery_report else None,
            command="scripts/demo/reset-demo.ps1 or scripts/demo/reseed-demo.ps1",
            default_when_missing=STATUS_OPERATOR_GUIDED,
            recommended_next_action="Record whether reset/reseed recovery was rehearsed or intentionally deferred.",
        ),
        LaneInput(
            id="governance_guardrail",
            label="Governance guardrail",
            group="governance",
            required_for_public_walkthrough=False,
            status=args.guardrail_status,
            path=Path(args.guardrail_report) if args.guardrail_report else None,
            command="python scripts/governance/agent_guardrail.py --summary",
            default_when_missing=STATUS_NOT_PROVIDED,
            recommended_next_action="Run and disclose guardrail caution or pause evidence if showing the governance lane.",
        ),
        LaneInput(
            id="release_evidence",
            label="Release evidence bundle",
            group="release_evidence",
            required_for_public_walkthrough=False,
            path=Path(args.release_evidence_report) if args.release_evidence_report else None,
            command="python scripts/ci/collect_release_evidence.py",
            default_when_missing=STATUS_NOT_PROVIDED,
            recommended_next_action="Attach release evidence when using hosted readiness for release or preview handoff.",
        ),
        LaneInput(
            id="real_repo_evidence",
            label="Real-repo benchmark evidence",
            group="optional_credibility",
            required_for_public_walkthrough=False,
            path=Path(args.real_repo_evidence_report) if args.real_repo_evidence_report else None,
            command="python scripts/ci/run_benchmark.py --live-real-repos or --benchmark-compare-*",
            default_when_missing=STATUS_NOT_PROVIDED,
            recommended_next_action="Attach dated real-repo benchmark evidence only when the optional credibility lane is shown.",
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect hosted/operator delivery readiness evidence into JSON and Markdown.")
    parser.add_argument("--output", default=".tmp/hosted-operator-readiness.json", help="Output path for readiness JSON.")
    parser.add_argument("--markdown-output", default=".tmp/hosted-operator-readiness.md", help="Output path for readiness Markdown.")
    parser.add_argument("--generated-at", help="Override generated_at timestamp for deterministic tests.")
    parser.add_argument("--web-base-url", help="Externally reachable hosted web URL.")
    parser.add_argument("--api-base-url", help="Externally reachable hosted API URL.")
    parser.add_argument("--engine-base-url", help="Externally reachable hosted engine URL.")
    parser.add_argument("--web-status", help="Explicit hosted web URL status.")
    parser.add_argument("--api-status", help="Explicit hosted API URL status.")
    parser.add_argument("--engine-status", help="Explicit hosted engine URL status.")
    parser.add_argument("--health-status", help="Explicit hosted health check status.")
    parser.add_argument("--health-report", help="Explicit JSON hosted health check report.")
    parser.add_argument("--smoke-status", help="Explicit hosted smoke check status.")
    parser.add_argument("--smoke-report", help="Explicit JSON hosted smoke check report.")
    parser.add_argument("--seeded-readiness-status", help="Explicit seeded demo readiness status.")
    parser.add_argument("--seeded-readiness-report", help="Explicit JSON from scripts/demo/check_seeded_demo.py --json.")
    parser.add_argument("--recovery-status", help="Explicit reset/reseed recovery drill status.")
    parser.add_argument("--recovery-report", help="Explicit JSON recovery drill report.")
    parser.add_argument("--guardrail-status", help="Explicit governance guardrail status.")
    parser.add_argument("--guardrail-report", help="Explicit JSON guardrail report.")
    parser.add_argument("--release-evidence-report", help="Explicit JSON release evidence bundle.")
    parser.add_argument("--real-repo-evidence-report", help="Explicit JSON live report, snapshot, or benchmark comparison.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    bundle = build_bundle(
        _build_lanes(args),
        root=root,
        generated_at=args.generated_at,
        hosted_urls={
            "web": args.web_base_url,
            "api": args.api_base_url,
            "engine": args.engine_base_url,
        },
    )
    output_path = Path(args.output)
    markdown_path = Path(args.markdown_output)
    if not output_path.is_absolute():
        output_path = root / output_path
    if not markdown_path.is_absolute():
        markdown_path = root / markdown_path

    _write_json(output_path, bundle)
    _write_markdown(markdown_path, render_markdown(bundle))
    print(f"Hosted readiness JSON written to {output_path}")
    print(f"Hosted readiness Markdown written to {markdown_path}")
    print(f"Public walkthrough status: {bundle['public_walkthrough_status']}")
    return 1 if bundle["public_walkthrough_status"] == STATUS_BLOCKING else 0


if __name__ == "__main__":
    sys.exit(main())
