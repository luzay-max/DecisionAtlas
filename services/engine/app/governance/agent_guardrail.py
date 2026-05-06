from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Iterable

from app.governance.diff_checker import run_governance_check
from app.governance.drift_detector import run_governance_drift_detection


AGENT_STATUSES = {"continue", "caution", "pause"}
PAUSE_DIFF_FINDINGS = {"missing-openspec-context", "missing-validation-evidence"}
PAUSE_DRIFT_SIGNALS = {"unsynced_decision"}


@dataclass(frozen=True)
class AgentGuardrailResult:
    agent_status: str
    summary: str
    findings: list[dict[str, Any]] = field(default_factory=list)
    signals: list[dict[str, Any]] = field(default_factory=list)
    matched_rules: list[dict[str, Any]] = field(default_factory=list)
    required_tests: list[str] = field(default_factory=list)
    human_decisions_needed: list[str] = field(default_factory=list)
    recommended_next_actions: list[str] = field(default_factory=list)
    source_results: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_agent_governance_guardrail(
    *,
    root: Path | str,
    owner_scope: str = "local-default",
    database_url: str | None = None,
    governance_rules: list[dict[str, Any]] | None = None,
    archived_change_limit: int = 12,
) -> AgentGuardrailResult:
    repo_root = Path(root).resolve()
    check_result = run_governance_check(
        root=repo_root,
        owner_scope=owner_scope,
        database_url=database_url,
        accepted_rules=governance_rules,
    )
    drift_report = run_governance_drift_detection(
        root=repo_root,
        owner_scope=owner_scope,
        database_url=database_url,
        governance_rules=governance_rules,
        archived_change_limit=archived_change_limit,
    )
    return aggregate_governance_guardrail(diff_check=check_result, drift_report=drift_report)


def aggregate_governance_guardrail(*, diff_check: Any, drift_report: Any) -> AgentGuardrailResult:
    check = _to_plain_dict(diff_check)
    drift = _to_plain_dict(drift_report)
    findings = _list_of_dicts(check.get("findings"))
    signals = _list_of_dicts(drift.get("signals"))
    matched_rules = _list_of_dicts(check.get("matched_rules"))
    required_tests = _dedupe_strings(check.get("required_tests") or [])
    human_decisions = _dedupe_strings(drift.get("human_decisions_needed") or [])
    recommended_actions = _dedupe_strings(
        [
            check.get("recommended_next_action"),
            *(drift.get("recommended_next_actions") or []),
            *_actions_from_findings(findings),
            *_actions_from_signals(signals),
            *human_decisions,
        ]
    )
    agent_status = _agent_status(
        check=check,
        drift=drift,
        findings=findings,
        signals=signals,
        human_decisions=human_decisions,
    )
    return AgentGuardrailResult(
        agent_status=agent_status,
        summary=_summary_for_status(agent_status, check=check, drift=drift),
        findings=_dedupe_dicts(findings),
        signals=_dedupe_dicts(signals),
        matched_rules=_dedupe_dicts(matched_rules),
        required_tests=required_tests,
        human_decisions_needed=human_decisions,
        recommended_next_actions=recommended_actions,
        source_results={
            "diff_check": check,
            "drift_report": drift,
        },
        context={
            "diff_status": check.get("status"),
            "drift_status": drift.get("status"),
            "advisory_only": True,
        },
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run an AI-agent governance guardrail summary.")
    parser.add_argument("--root", default=".", help="Repository root to inspect.")
    parser.add_argument("--owner-scope", default=os.environ.get("DECISIONATLAS_OWNER_SCOPE", "local-default"))
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--rules-json", help="Optional JSON file with governance rules for offline checks.")
    parser.add_argument("--archived-change-limit", type=int, default=12)
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--summary", action="store_true", help="Print a concise human-readable summary.")
    args = parser.parse_args(argv)

    rules = _rules_from_json_file(Path(args.rules_json)) if args.rules_json else None
    result = run_agent_governance_guardrail(
        root=Path(args.root),
        owner_scope=args.owner_scope,
        database_url=args.database_url,
        governance_rules=rules,
        archived_change_limit=args.archived_change_limit,
    )
    if args.summary:
        print(_human_summary(result))
    else:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


def _agent_status(
    *,
    check: dict[str, Any],
    drift: dict[str, Any],
    findings: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    human_decisions: list[str],
) -> str:
    if check.get("status") == "blocked" or drift.get("status") == "review_required":
        return "pause"
    if check.get("conflicts"):
        return "pause"
    if human_decisions:
        return "pause"
    if any(finding.get("id") in PAUSE_DIFF_FINDINGS for finding in findings):
        return "pause"
    if any(signal.get("type") in PAUSE_DRIFT_SIGNALS for signal in signals):
        return "pause"
    if check.get("status") == "warning" or drift.get("status") in {"watch", "drift_detected"}:
        return "caution"
    return "continue"


def _summary_for_status(agent_status: str, *, check: dict[str, Any], drift: dict[str, Any]) -> str:
    if agent_status == "pause":
        return "Governance guardrail requires human review before the agent continues."
    if agent_status == "caution":
        return "Governance guardrail found advisory concerns; the agent may continue only after addressing recommended actions."
    return "Governance guardrail found no blocking or caution-level governance concerns."


def _human_summary(result: AgentGuardrailResult) -> str:
    lines = [
        f"Agent status: {result.agent_status}",
        result.summary,
        f"Diff check: {result.context.get('diff_status')}",
        f"Drift report: {result.context.get('drift_status')}",
    ]
    if result.recommended_next_actions:
        lines.append("Recommended next actions:")
        lines.extend(f"- {action}" for action in result.recommended_next_actions)
    return "\n".join(lines)


def _to_plain_dict(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    elif is_dataclass(value):
        value = asdict(value)
    if isinstance(value, dict):
        return value
    raise TypeError(f"Unsupported governance source result: {type(value).__name__}")


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in (_to_plain_dict(item) if not isinstance(item, dict) else item for item in value) if isinstance(item, dict)]


def _actions_from_findings(findings: Iterable[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for finding in findings:
        detail = finding.get("detail")
        if finding.get("severity") in {"warning", "blocker"} and detail:
            actions.append(str(detail))
    return actions


def _actions_from_signals(signals: Iterable[dict[str, Any]]) -> list[str]:
    return [str(signal["recommended_next_action"]) for signal in signals if signal.get("recommended_next_action")]


def _dedupe_strings(values: Iterable[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value is None:
            continue
        normalized = str(value).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _dedupe_dicts(values: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for value in values:
        key = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def _rules_from_json_file(path: Path) -> list[dict[str, Any]]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(loaded, dict):
        loaded = loaded.get("rules", [])
    if not isinstance(loaded, list):
        raise ValueError("--rules-json must contain a rule list or an object with a rules list")
    return loaded


if __name__ == "__main__":
    raise SystemExit(main())
