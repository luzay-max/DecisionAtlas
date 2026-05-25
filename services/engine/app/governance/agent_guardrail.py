from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Iterable

from app.governance.diff_checker import run_governance_check
from app.governance.drift_detector import run_governance_drift_detection


AGENT_STATUSES = {"continue", "caution", "pause"}
PAUSE_DIFF_FINDINGS = {"missing-openspec-context", "missing-validation-evidence"}
PAUSE_DRIFT_SIGNALS = {"unsynced_decision"}
ENFORCEMENT_PREVIEW_MODES = {"local-strict", "pr-annotation", "release-checklist"}


@dataclass(frozen=True)
class AgentGuardrailResult:
    agent_status: str
    summary: str
    workflow_protocol: dict[str, Any] = field(default_factory=dict)
    agent_instruction: str = ""
    allowed_next_actions: list[str] = field(default_factory=list)
    disallowed_next_actions: list[str] = field(default_factory=list)
    human_questions: list[dict[str, Any]] = field(default_factory=list)
    handoff_summary: dict[str, Any] = field(default_factory=dict)
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


@dataclass(frozen=True)
class GovernanceEnforcementPreview:
    mode: str
    would_block: bool
    severity: str
    advisory_default: bool
    block_reasons: list[str] = field(default_factory=list)
    warning_reasons: list[str] = field(default_factory=list)
    override_required: bool = False
    override_prompt: str = ""
    source_evidence: dict[str, Any] = field(default_factory=dict)
    report_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DevelopmentProtocolStatus:
    protocol_name: str
    version: str
    advisory_only: bool
    openspec_context: dict[str, Any]
    guardrail: dict[str, Any]
    checkpoints: dict[str, Any]
    handoff_guidance: dict[str, Any]

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


def build_enforcement_preview(result: AgentGuardrailResult, *, mode: str) -> GovernanceEnforcementPreview:
    if mode not in ENFORCEMENT_PREVIEW_MODES:
        allowed = ", ".join(sorted(ENFORCEMENT_PREVIEW_MODES))
        raise ValueError(f"Unsupported enforcement preview mode '{mode}'. Expected one of: {allowed}")

    diff_status = result.context.get("diff_status")
    drift_status = result.context.get("drift_status")
    block_reasons: list[str] = []
    warning_reasons: list[str] = []

    if result.agent_status == "pause":
        block_reasons.append("Agent status is pause and requires human review.")
    if diff_status == "blocked":
        block_reasons.append("Governance diff check is blocked.")
    if drift_status == "review_required":
        block_reasons.append("Governance drift report requires review.")

    would_block = bool(block_reasons)
    if not would_block and result.agent_status == "caution":
        warning_reasons.extend(_preview_warning_reasons(result))

    severity = "blocker" if would_block else "warning" if warning_reasons else "pass"
    override_prompt = ""
    if would_block:
        override_prompt = (
            "If this is a false positive, record a human-authored override in the handoff "
            "that cites the source evidence and states why the agent may continue."
        )

    preview = GovernanceEnforcementPreview(
        mode=mode,
        would_block=would_block,
        severity=severity,
        advisory_default=True,
        block_reasons=_dedupe_strings(block_reasons),
        warning_reasons=_dedupe_strings(warning_reasons),
        override_required=would_block,
        override_prompt=override_prompt,
        source_evidence=_preview_source_evidence(result),
    )
    return GovernanceEnforcementPreview(
        **{
            **preview.to_dict(),
            "report_text": _enforcement_preview_report(preview),
        }
    )


def build_development_protocol_status(
    result: AgentGuardrailResult,
    *,
    root: Path | str,
) -> DevelopmentProtocolStatus:
    repo_root = Path(root).resolve()
    openspec_context = _openspec_context(repo_root)
    return DevelopmentProtocolStatus(
        protocol_name="decisionatlas-default-governance-development-protocol",
        version="1",
        advisory_only=True,
        openspec_context=openspec_context,
        guardrail={
            "agent_status": result.agent_status,
            "summary": result.summary,
            "diff_status": result.context.get("diff_status"),
            "drift_status": result.context.get("drift_status"),
            "required_tests": result.required_tests,
            "recommended_next_actions": result.recommended_next_actions,
            "human_questions": result.human_questions,
            "allowed_next_actions": result.allowed_next_actions,
            "disallowed_next_actions": result.disallowed_next_actions,
            "handoff_summary": result.handoff_summary,
        },
        checkpoints={
            "preflight": {
                "when": "Before non-trivial implementation that may affect behavior, specs, roadmap, governance documents, validation expectations, or project direction.",
                "command": "python scripts/governance/agent_guardrail.py --protocol-status",
            },
            "postflight": {
                "when": "After implementation and targeted validation, before claiming completion.",
                "command": "python scripts/governance/agent_guardrail.py --protocol-status",
            },
            "before_archive": {
                "when": "Before archiving an OpenSpec change.",
                "command": "python scripts/governance/agent_guardrail.py --protocol-status",
            },
            "before_commit": {
                "when": "Before committing completed work.",
                "command": "python scripts/governance/agent_guardrail.py --protocol-status",
            },
        },
        handoff_guidance=_protocol_handoff_guidance(result=result, openspec_context=openspec_context),
    )
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
    protocol = _workflow_protocol(
        agent_status=agent_status,
        check=check,
        drift=drift,
        findings=findings,
        signals=signals,
        required_tests=required_tests,
        human_decisions=human_decisions,
        recommended_actions=recommended_actions,
    )
    return AgentGuardrailResult(
        agent_status=agent_status,
        summary=_summary_for_status(agent_status, check=check, drift=drift),
        workflow_protocol={
            "name": "decisionatlas-agent-governance-workflow",
            "version": "1",
            "advisory_only": True,
        },
        agent_instruction=protocol["agent_instruction"],
        allowed_next_actions=protocol["allowed_next_actions"],
        disallowed_next_actions=protocol["disallowed_next_actions"],
        human_questions=protocol["human_questions"],
        handoff_summary=protocol["handoff_summary"],
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
    parser.add_argument(
        "--protocol-status",
        action="store_true",
        help="Print default local governance development protocol status.",
    )
    parser.add_argument(
        "--agent",
        action="store_true",
        help="Outputs structured JSON and status-specific exit codes (0: continue, 5: caution, 10: pause) for AI agent integration.",
    )
    parser.add_argument(
        "--enforcement-preview",
        choices=sorted(ENFORCEMENT_PREVIEW_MODES),
        help="Opt-in governance enforcement preview mode. Default guardrail behavior remains advisory.",
    )
    parser.add_argument(
        "--strict-exit",
        action="store_true",
        help="With --enforcement-preview, return non-zero only when preview would_block is true.",
    )
    args = parser.parse_args(argv)
    if args.strict_exit and not args.enforcement_preview:
        parser.error("--strict-exit requires --enforcement-preview")

    rules = _rules_from_json_file(Path(args.rules_json)) if args.rules_json else None
    result = run_agent_governance_guardrail(
        root=Path(args.root),
        owner_scope=args.owner_scope,
        database_url=args.database_url,
        governance_rules=rules,
        archived_change_limit=args.archived_change_limit,
    )
    preview = (
        build_enforcement_preview(result, mode=args.enforcement_preview)
        if args.enforcement_preview
        else None
    )
    protocol_status = (
        build_development_protocol_status(result, root=Path(args.root))
        if args.protocol_status
        else None
    )
    
    if args.agent:
        body = {
            "agent_status": result.agent_status,
            "summary": result.summary,
            "required_tests": result.required_tests,
            "human_decisions_needed": result.human_decisions_needed,
            "recommended_next_actions": result.recommended_next_actions,
            "human_questions": result.human_questions,
            "allowed_next_actions": result.allowed_next_actions,
            "disallowed_next_actions": result.disallowed_next_actions,
            "findings": [
                {
                    "id": f.get("id"),
                    "severity": f.get("severity"),
                    "title": f.get("title"),
                    "detail": f.get("detail"),
                    "source": {
                        "kind": f.get("source", {}).get("kind") if f.get("source") else None,
                        "title": f.get("source", {}).get("title") if f.get("source") else None,
                        "excerpt": f.get("source", {}).get("excerpt") if f.get("source") else None,
                    } if f.get("source") else None
                } for f in result.findings
            ],
            "signals": [
                {
                    "id": s.get("id"),
                    "type": s.get("type"),
                    "title": s.get("title"),
                    "recommended_next_action": s.get("recommended_next_action"),
                } for s in result.signals
            ],
        }
        print(json.dumps(body, ensure_ascii=False, indent=2 if args.pretty else None))
        if result.agent_status == "pause":
            return 10
        elif result.agent_status == "caution":
            return 5
        return 0

    if args.summary and protocol_status:
        print(_protocol_human_summary(protocol_status))
    elif args.summary:
        print(_human_summary(result, enforcement_preview=preview))
    else:
        body = protocol_status.to_dict() if protocol_status else result.to_dict()
        if preview:
            body["enforcement_preview"] = preview.to_dict()
        print(json.dumps(body, ensure_ascii=False, indent=2 if args.pretty else None))
    return 1 if args.strict_exit and preview and preview.would_block else 0


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


def _human_summary(
    result: AgentGuardrailResult,
    *,
    enforcement_preview: GovernanceEnforcementPreview | None = None,
) -> str:
    lines = [
        f"Agent status: {result.agent_status}",
        result.summary,
        f"Diff check: {result.context.get('diff_status')}",
        f"Drift report: {result.context.get('drift_status')}",
    ]
    if result.recommended_next_actions:
        lines.append("Recommended next actions:")
        lines.extend(f"- {action}" for action in result.recommended_next_actions)
    if result.human_questions:
        lines.append("Human questions:")
        lines.extend(f"- {question['question']}" for question in result.human_questions if question.get("question"))
    if enforcement_preview:
        lines.append("")
        lines.append(enforcement_preview.report_text)
    return "\n".join(lines)


def _protocol_human_summary(status: DevelopmentProtocolStatus) -> str:
    data = status.to_dict()
    guardrail = data["guardrail"]
    openspec_context = data["openspec_context"]
    lines = [
        f"Protocol: {data['protocol_name']} v{data['version']}",
        "Advisory only: true",
        f"OpenSpec: {openspec_context['state']}",
        f"Active changes: {', '.join(openspec_context['active_changes']) if openspec_context['active_changes'] else 'none'}",
        f"Agent status: {guardrail['agent_status']}",
        f"Diff check: {guardrail['diff_status']}",
        f"Drift report: {guardrail['drift_status']}",
    ]
    if guardrail["required_tests"]:
        lines.append("Required tests:")
        lines.extend(f"- {test}" for test in guardrail["required_tests"])
    if guardrail["recommended_next_actions"]:
        lines.append("Recommended next actions:")
        lines.extend(f"- {action}" for action in guardrail["recommended_next_actions"])
    if guardrail["human_questions"]:
        lines.append("Human questions:")
        lines.extend(f"- {question['question']}" for question in guardrail["human_questions"] if question.get("question"))
    lines.append(f"Handoff: {data['handoff_guidance']['completion_claim']}")
    return "\n".join(lines)


def _protocol_handoff_guidance(
    *,
    result: AgentGuardrailResult,
    openspec_context: dict[str, Any],
) -> dict[str, Any]:
    if result.agent_status == "pause":
        completion_claim = "Do not claim completion. Ask for human review and include the pause evidence."
    elif result.agent_status == "caution":
        completion_claim = "Claim completion only after addressing or explicitly disclosing caution evidence."
    else:
        completion_claim = "May continue normal work, but targeted validation and review are still required."
    return {
        "completion_claim": completion_claim,
        "include_in_handoff": [
            "agent_status",
            "diff_status",
            "drift_status",
            "active_openspec_changes",
            "required_tests",
            "recommended_next_actions",
            "human_questions",
            "advisory_only",
        ],
        "active_openspec_changes": openspec_context.get("active_changes", []),
        "advisory_only": True,
    }


def _openspec_context(root: Path) -> dict[str, Any]:
    command = ["openspec", "list", "--json"]
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return _filesystem_openspec_context(root, command=" ".join(command), error=str(exc))
    if completed.returncode != 0:
        return _filesystem_openspec_context(
            root,
            command=" ".join(command),
            error=completed.stderr.strip() or completed.stdout.strip(),
        )
    try:
        payload = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError as exc:
        return {
            "state": "unavailable",
            "active_changes": [],
            "command": " ".join(command),
            "error": f"Invalid openspec JSON: {exc}",
        }
    changes = payload.get("changes", [])
    active_changes = _active_change_names(changes)
    return {
        "state": "active" if active_changes else "none",
        "active_changes": active_changes,
        "command": " ".join(command),
        "source": "openspec-cli",
    }


def _filesystem_openspec_context(root: Path, *, command: str, error: str) -> dict[str, Any]:
    changes_root = root / "openspec" / "changes"
    if not changes_root.exists():
        return {
            "state": "unavailable",
            "active_changes": [],
            "command": command,
            "source": "filesystem-fallback",
            "error": error,
        }
    active_changes = [
        item.name
        for item in sorted(changes_root.iterdir(), key=lambda path: path.name)
        if item.is_dir() and item.name != "archive" and (item / ".openspec.yaml").exists()
    ]
    return {
        "state": "active" if active_changes else "none",
        "active_changes": active_changes,
        "command": command,
        "source": "filesystem-fallback",
        "fallback_reason": error,
    }


def _active_change_names(changes: Any) -> list[str]:
    if not isinstance(changes, list):
        return []
    names: list[str] = []
    for change in changes:
        if isinstance(change, str):
            names.append(change)
        elif isinstance(change, dict):
            name = change.get("name") or change.get("changeName") or change.get("id")
            if name and not change.get("archived", False):
                names.append(str(name))
    return _dedupe_strings(names)


def _preview_warning_reasons(result: AgentGuardrailResult) -> list[str]:
    reasons: list[str] = []
    reasons.extend(result.recommended_next_actions)
    reasons.extend(str(finding.get("detail")) for finding in result.findings if finding.get("detail"))
    reasons.extend(
        str(signal.get("recommended_next_action"))
        for signal in result.signals
        if signal.get("recommended_next_action")
    )
    if not reasons:
        reasons.append("Guardrail returned caution; disclose or address the advisory evidence before claiming completion.")
    return _dedupe_strings(reasons)


def _preview_source_evidence(result: AgentGuardrailResult) -> dict[str, Any]:
    return {
        "agent_status": result.agent_status,
        "diff_status": result.context.get("diff_status"),
        "drift_status": result.context.get("drift_status"),
        "findings": result.findings,
        "signals": result.signals,
        "human_questions": result.human_questions,
        "recommended_next_actions": result.recommended_next_actions,
        "matched_rules": result.matched_rules,
        "source_results": result.source_results,
        "advisory_default": True,
    }


def _enforcement_preview_report(preview: GovernanceEnforcementPreview) -> str:
    lines = [
        "Governance enforcement preview:",
        f"- Mode: {preview.mode}",
        "- Default advisory: true",
        f"- Would block: {str(preview.would_block).lower()}",
        f"- Severity: {preview.severity}",
    ]
    if preview.block_reasons:
        lines.append("- Block reasons:")
        lines.extend(f"  - {reason}" for reason in preview.block_reasons)
    if preview.warning_reasons:
        lines.append("- Warning evidence:")
        lines.extend(f"  - {reason}" for reason in preview.warning_reasons)
    if preview.override_required:
        lines.append(f"- Override handoff: {preview.override_prompt}")
    if preview.mode == "pr-annotation":
        lines.append("- PR annotation: local report text only; no GitHub API call was made.")
    if preview.mode == "release-checklist":
        lines.append("- Release checklist: record this as optional readiness evidence, not as a default release gate.")
    return "\n".join(lines)


def _workflow_protocol(
    *,
    agent_status: str,
    check: dict[str, Any],
    drift: dict[str, Any],
    findings: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    required_tests: list[str],
    human_decisions: list[str],
    recommended_actions: list[str],
) -> dict[str, Any]:
    human_questions = _human_questions(
        agent_status=agent_status,
        findings=findings,
        signals=signals,
        human_decisions=human_decisions,
    )
    if agent_status == "pause":
        instruction = "Stop implementation and ask for human review before continuing."
        allowed = [
            "summarize_guardrail_evidence",
            "ask_human_for_decision",
            "record_governance_handoff",
        ]
        disallowed = [
            "continue_implementation_without_human_review",
            "commit_without_human_review",
            "silently_rewrite_code_to_clear_guardrail",
            "silently_rewrite_openspec_to_clear_guardrail",
            "silently_rewrite_roadmap_or_governance_rules_to_clear_guardrail",
        ]
    elif agent_status == "caution":
        instruction = "Proceed only after addressing or explicitly reporting recommended governance actions."
        allowed = [
            "address_recommended_next_actions",
            "run_required_tests",
            "continue_with_explicit_caution_handoff",
        ]
        disallowed = [
            "claim_completion_without_disclosing_caution",
            "skip_required_tests",
        ]
    else:
        instruction = "Continue normal work while still running targeted validation and reporting guardrail status."
        allowed = [
            "continue_implementation",
            "run_required_tests",
            "record_governance_handoff",
        ]
        disallowed = [
            "skip_targeted_validation",
            "claim_guardrail_as_correctness_proof",
        ]

    return {
        "agent_instruction": instruction,
        "allowed_next_actions": allowed,
        "disallowed_next_actions": disallowed,
        "human_questions": human_questions,
        "handoff_summary": {
            "agent_status": agent_status,
            "diff_status": check.get("status"),
            "drift_status": drift.get("status"),
            "required_tests": required_tests,
            "human_questions": human_questions,
            "recommended_next_actions": recommended_actions,
            "advisory_only": True,
        },
    }


def _human_questions(
    *,
    agent_status: str,
    findings: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    human_decisions: list[str],
) -> list[dict[str, Any]]:
    if agent_status != "pause":
        return []

    questions: list[dict[str, Any]] = []
    for index, decision in enumerate(human_decisions, start=1):
        questions.append(
            {
                "id": f"human-decision-{index}",
                "question": str(decision),
                "evidence_type": "human_decision",
                "evidence_id": f"human_decisions_needed[{index - 1}]",
            }
        )

    for finding in findings:
        question = _question_from_finding(finding)
        if question:
            questions.append(question)

    for signal in signals:
        question = _question_from_signal(signal)
        if question:
            questions.append(question)

    if not questions:
        questions.append(
            {
                "id": "human-review-required",
                "question": "Review the guardrail pause evidence and decide whether the agent may continue.",
                "evidence_type": "source_results",
                "evidence_id": "source_results",
            }
        )
    return _dedupe_dicts(questions)


def _question_from_finding(finding: dict[str, Any]) -> dict[str, Any] | None:
    finding_id = str(finding.get("id") or "finding")
    title = str(finding.get("title") or finding_id)
    detail = str(finding.get("detail") or title)
    if finding_id == "missing-openspec-context":
        question = "Should this behavior change get OpenSpec context before implementation continues?"
    elif finding_id == "missing-validation-evidence":
        question = "What validation evidence is required before the agent may continue or claim completion?"
    elif finding.get("severity") == "blocker":
        question = f"How should the blocker be resolved before the agent continues: {title}?"
    else:
        return None
    return {
        "id": f"finding-{finding_id}",
        "question": question,
        "evidence_type": "finding",
        "evidence_id": finding_id,
        "evidence_summary": detail,
    }


def _question_from_signal(signal: dict[str, Any]) -> dict[str, Any] | None:
    signal_type = str(signal.get("type") or "")
    signal_id = str(signal.get("id") or signal_type or "signal")
    title = str(signal.get("title") or signal_id)
    if signal_type == "unsynced_decision":
        question = "Should the unsynced human decision update OpenSpec specs, accepted governance rules, or remain documented only?"
    elif signal_type == "stale_rule":
        question = "Should this inactive governance rule remain stale or superseded, use the recorded replacement, or become a new accepted current rule?"
    elif signal.get("severity") in {"blocker", "warning"} and signal.get("recommended_next_action"):
        question = f"What decision is needed for this governance drift signal: {title}?"
    else:
        return None
    return {
        "id": f"signal-{signal_id}",
        "question": question,
        "evidence_type": "signal",
        "evidence_id": signal_id,
        "evidence_summary": str(signal.get("recommended_next_action") or title),
    }


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
