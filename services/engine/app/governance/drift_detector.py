from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

from app.governance.diff_checker import GitDiffContext, collect_git_diff


REPORT_STATUSES = {"clean", "watch", "drift_detected", "review_required"}
SIGNAL_SEVERITIES = {"note", "warning", "blocker"}
DRIFT_SIGNAL_TYPES = {
    "roadmap_mismatch",
    "spec_gap",
    "stale_rule",
    "repeated_postmortem_issue",
    "unsynced_decision",
}


@dataclass(frozen=True)
class DriftEvidence:
    kind: str
    path: str | None = None
    title: str | None = None
    excerpt: str | None = None
    id: str | int | None = None
    lifecycle_status: str | None = None
    lifecycle_rationale: str | None = None
    superseded_by_rule_id: str | int | None = None


@dataclass(frozen=True)
class GovernanceDriftSignal:
    id: str
    type: str
    severity: str
    title: str
    detail: str
    evidence: list[DriftEvidence] = field(default_factory=list)
    recommended_next_action: str | None = None


@dataclass(frozen=True)
class GovernanceDriftReport:
    status: str
    signals: list[GovernanceDriftSignal] = field(default_factory=list)
    human_decisions_needed: list[str] = field(default_factory=list)
    recommended_next_actions: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DocumentRef:
    kind: str
    path: str
    title: str
    excerpt: str
    text: str

    def evidence(self, *, excerpt: str | None = None) -> DriftEvidence:
        return DriftEvidence(kind=self.kind, path=self.path, title=self.title, excerpt=excerpt or self.excerpt)


@dataclass(frozen=True)
class SpecRef:
    name: str
    path: str
    requirements: list[str]
    text: str

    def evidence(self, *, excerpt: str | None = None) -> DriftEvidence:
        return DriftEvidence(kind="spec", path=self.path, title=self.name, excerpt=excerpt or _bounded_excerpt(self.text))


@dataclass(frozen=True)
class ArchivedChangeRef:
    name: str
    path: str
    text_by_path: dict[str, str]
    capabilities: list[str]
    decision_markers: list[str]

    @property
    def combined_text(self) -> str:
        return "\n".join(self.text_by_path.values())

    def evidence(self, *, excerpt: str | None = None) -> DriftEvidence:
        return DriftEvidence(kind="archived_change", path=self.path, title=self.name, excerpt=excerpt or _bounded_excerpt(self.combined_text))


@dataclass(frozen=True)
class GovernanceDriftContext:
    roadmap_refs: list[DocumentRef]
    spec_refs: list[SpecRef]
    archived_changes: list[ArchivedChangeRef]
    log_refs: list[DocumentRef]
    governance_rules: list[dict[str, Any]]
    accepted_rules: list[dict[str, Any]]
    diff_context: GitDiffContext


def run_governance_drift_detection(
    *,
    root: Path | str,
    owner_scope: str = "local-default",
    governance_rules: list[dict[str, Any]] | None = None,
    diff_text: str | None = None,
    status_text: str | None = None,
    database_url: str | None = None,
    archived_change_limit: int = 12,
) -> GovernanceDriftReport:
    repo_root = Path(root).resolve()
    context = collect_governance_drift_context(
        repo_root,
        owner_scope=owner_scope,
        governance_rules=governance_rules,
        diff_text=diff_text,
        status_text=status_text,
        database_url=database_url,
        archived_change_limit=archived_change_limit,
    )
    signals = _dedupe_signals(
        [
            *_detect_roadmap_mismatch(context),
            *_detect_spec_gaps(context),
            *_detect_stale_rules(context),
            *_detect_repeated_postmortem_issues(context),
            *_detect_unsynced_decisions(context),
        ]
    )
    human_decisions = _human_decisions_needed(signals)
    recommended_actions = _recommended_actions(signals, human_decisions)
    status = _status_from_signals(signals, human_decisions)
    return GovernanceDriftReport(
        status=status,
        signals=signals,
        human_decisions_needed=human_decisions,
        recommended_next_actions=recommended_actions,
        context={
            "roadmap_refs": len(context.roadmap_refs),
            "spec_refs": len(context.spec_refs),
            "archived_changes": len(context.archived_changes),
            "log_refs": len(context.log_refs),
            "governance_rules": len(context.governance_rules),
            "accepted_rule_count": len(context.accepted_rules),
            "diff_paths": context.diff_context.all_paths,
            "advisory_only": True,
        },
    )


def collect_governance_drift_context(
    root: Path,
    *,
    owner_scope: str = "local-default",
    governance_rules: list[dict[str, Any]] | None = None,
    diff_text: str | None = None,
    status_text: str | None = None,
    database_url: str | None = None,
    archived_change_limit: int = 12,
) -> GovernanceDriftContext:
    rules = collect_governance_rules(
        repo_root=root,
        owner_scope=owner_scope,
        governance_rules=governance_rules,
        database_url=database_url,
    )
    return GovernanceDriftContext(
        roadmap_refs=collect_roadmap_refs(root),
        spec_refs=collect_spec_refs(root),
        archived_changes=collect_archived_changes(root, limit=archived_change_limit),
        log_refs=collect_update_log_refs(root),
        governance_rules=rules,
        accepted_rules=[rule for rule in rules if _is_active_accepted_rule(rule)],
        diff_context=collect_git_diff(root, diff_text=diff_text, status_text=status_text),
    )


def collect_roadmap_refs(root: Path) -> list[DocumentRef]:
    plans_root = root / "docs" / "plans"
    if not plans_root.exists():
        return []
    refs: list[DocumentRef] = []
    for path in sorted(plans_root.glob("*.md")):
        text = _read_text(path)
        if not text.strip():
            continue
        lowered = text.lower()
        if any(marker in lowered for marker in ("roadmap", "路线", "阶段", "plan", "治理", "governance")):
            refs.append(_document_ref(root=root, path=path, kind="roadmap"))
    return refs


def collect_spec_refs(root: Path) -> list[SpecRef]:
    specs_root = root / "openspec" / "specs"
    if not specs_root.exists():
        return []
    refs: list[SpecRef] = []
    for path in sorted(specs_root.glob("*/spec.md")):
        text = _read_text(path)
        refs.append(
            SpecRef(
                name=path.parent.name,
                path=str(path.relative_to(root)),
                requirements=_requirement_names(text),
                text=text,
            )
        )
    return refs


def collect_archived_changes(root: Path, *, limit: int = 12) -> list[ArchivedChangeRef]:
    archive_root = root / "openspec" / "changes" / "archive"
    if not archive_root.exists():
        return []
    change_dirs = sorted(
        [path for path in archive_root.iterdir() if path.is_dir()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )[:limit]
    changes: list[ArchivedChangeRef] = []
    for change_dir in change_dirs:
        text_by_path: dict[str, str] = {}
        for relative in ("proposal.md", "design.md", "tasks.md"):
            file_path = change_dir / relative
            if file_path.exists():
                text_by_path[str(file_path.relative_to(root))] = _read_text(file_path)
        specs_dir = change_dir / "specs"
        if specs_dir.exists():
            for spec_file in sorted(specs_dir.rglob("*.md")):
                text_by_path[str(spec_file.relative_to(root))] = _read_text(spec_file)
        combined = "\n".join(text_by_path.values())
        changes.append(
            ArchivedChangeRef(
                name=change_dir.name,
                path=str(change_dir.relative_to(root)),
                text_by_path=text_by_path,
                capabilities=_capabilities_from_proposal(text_by_path.get(str((change_dir / "proposal.md").relative_to(root)), "")),
                decision_markers=_decision_markers_from_text(combined),
            )
        )
    return changes


def collect_update_log_refs(root: Path) -> list[DocumentRef]:
    docs_root = root / "docs" / "project"
    if not docs_root.exists():
        return []
    refs: list[DocumentRef] = []
    for path in sorted(docs_root.glob("*.md")):
        name = path.name.lower()
        text = _read_text(path)
        lowered = text.lower()
        if any(marker in name for marker in ("update-log", "postmortem", "error", "incident")) or any(
            marker in lowered for marker in ("postmortem", "regression", "error", "issue", "失败", "错误", "复盘")
        ):
            refs.append(_document_ref(root=root, path=path, kind="project_log"))
    return refs


def collect_governance_rules(
    *,
    repo_root: Path,
    owner_scope: str,
    governance_rules: list[dict[str, Any]] | None = None,
    database_url: str | None = None,
) -> list[dict[str, Any]]:
    if governance_rules is not None:
        return [_normalize_rule(rule) for rule in governance_rules]

    db_path = _sqlite_path(repo_root=repo_root, database_url=database_url or os.environ.get("DATABASE_URL"))
    if db_path is None or not db_path.exists():
        return []
    query = """
        SELECT
            r.id,
            r.title,
            r.description,
            r.severity,
            r.scope,
            r.source_excerpt,
            r.review_state,
            r.status,
            r.lifecycle_status,
            r.superseded_by_rule_id,
            r.lifecycle_rationale,
            d.title AS source_title,
            d.source_path AS source_path,
            d.status AS document_status,
            d.document_type AS document_type
        FROM governance_rule_drafts r
        JOIN governance_documents d ON d.id = r.document_id
        WHERE r.owner_scope = ?
        ORDER BY r.reviewed_at DESC, r.created_at DESC, r.id DESC
    """
    try:
        with sqlite3.connect(db_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(query, (owner_scope,)).fetchall()
    except sqlite3.Error:
        return []
    return [_normalize_rule(dict(row)) for row in rows]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a local DecisionAtlas governance drift report.")
    parser.add_argument("--root", default=".", help="Repository root to inspect.")
    parser.add_argument("--owner-scope", default=os.environ.get("DECISIONATLAS_OWNER_SCOPE", "local-default"))
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--rules-json", help="Optional JSON file with governance rules for offline checks.")
    parser.add_argument("--archived-change-limit", type=int, default=12)
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args(argv)

    rules = None
    if args.rules_json:
        rules = _rules_from_json_file(Path(args.rules_json))
    report = run_governance_drift_detection(
        root=Path(args.root),
        owner_scope=args.owner_scope,
        governance_rules=rules,
        database_url=args.database_url,
        archived_change_limit=args.archived_change_limit,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


def _detect_roadmap_mismatch(context: GovernanceDriftContext) -> list[GovernanceDriftSignal]:
    if not context.roadmap_refs:
        return []
    recent_tokens = _recent_topic_tokens(context)
    if not recent_tokens:
        return []
    roadmap_tokens = set(_tokens("\n".join(ref.text for ref in context.roadmap_refs)))
    spec_tokens = {token for spec in context.spec_refs for token in _tokens(f"{spec.name} {' '.join(spec.requirements)}")}
    aligned = recent_tokens & (roadmap_tokens | spec_tokens)
    if aligned:
        return []
    evidence = [context.roadmap_refs[0].evidence()]
    if context.archived_changes:
        evidence.append(context.archived_changes[0].evidence())
    if context.diff_context.all_paths:
        evidence.append(DriftEvidence(kind="git_diff", title="current diff paths", excerpt=", ".join(context.diff_context.all_paths[:8])))
    return [
        GovernanceDriftSignal(
            id="roadmap-mismatch-recent-context",
            type="roadmap_mismatch",
            severity="note",
            title="Recent governance history is not obviously aligned with roadmap terms",
            detail="Recent change or diff topics have little overlap with current roadmap and spec terminology. Review whether roadmap direction needs an update.",
            evidence=evidence,
            recommended_next_action="Review the roadmap and recent change context before continuing this direction.",
        )
    ]


def _rules_from_json_file(path: Path) -> list[dict[str, Any]]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(loaded, dict):
        loaded = loaded.get("rules", [])
    if not isinstance(loaded, list):
        raise ValueError("--rules-json must contain a rule list or an object with a rules list")
    return loaded


def _detect_spec_gaps(context: GovernanceDriftContext) -> list[GovernanceDriftSignal]:
    existing_specs = {spec.name for spec in context.spec_refs}
    signals: list[GovernanceDriftSignal] = []
    for change in context.archived_changes:
        missing = [capability for capability in change.capabilities if capability not in existing_specs]
        if not missing:
            continue
        signals.append(
            GovernanceDriftSignal(
                id=f"spec-gap-{change.name}",
                type="spec_gap",
                severity="warning",
                title="Archived change capability is missing from main specs",
                detail=f"Archived change '{change.name}' references capabilities not present in main specs: {', '.join(missing)}.",
                evidence=[change.evidence()],
                recommended_next_action="Sync or create the missing main spec, or document why the archived capability is obsolete.",
            )
        )
    return signals


def _detect_stale_rules(context: GovernanceDriftContext) -> list[GovernanceDriftSignal]:
    recent_text = _recent_text(context).lower()
    if not recent_text.strip():
        return []
    signals: list[GovernanceDriftSignal] = []
    for rule in context.governance_rules:
        if _is_active_accepted_rule(rule):
            continue
        rule_tokens = set(_tokens(f"{rule.get('title', '')} {rule.get('description', '')}"))
        if not rule_tokens or len(rule_tokens & set(_tokens(recent_text))) < 2:
            continue
        source_title = str(rule.get("source_title") or rule.get("title") or "stale governance rule")
        lifecycle_status = str(rule.get("lifecycle_status") or "inactive")
        replacement = rule.get("superseded_by_rule_id")
        replacement_text = f" Replacement rule: #{replacement}." if replacement else ""
        signals.append(
            GovernanceDriftSignal(
                id=f"stale-rule-{rule.get('id') or _slug(source_title)}",
                type="stale_rule",
                severity="warning",
                title="Inactive governance source appears in recent context",
                detail=(
                    f"Rule '{rule.get('title')}' has lifecycle '{lifecycle_status}' and appears related to recent "
                    f"governance context.{replacement_text}"
                ),
                evidence=[
                    DriftEvidence(
                        kind="governance_rule",
                        id=rule.get("id"),
                        title=source_title,
                        excerpt=rule.get("source_excerpt") or rule.get("description"),
                        lifecycle_status=lifecycle_status,
                        lifecycle_rationale=rule.get("lifecycle_rationale"),
                        superseded_by_rule_id=replacement,
                    )
                ],
                recommended_next_action=(
                    "Confirm whether this inactive lifecycle rule should remain inactive, point to the recorded "
                    "replacement, or be replaced by a new accepted current rule."
                ),
            )
        )
    return signals


def _detect_repeated_postmortem_issues(context: GovernanceDriftContext) -> list[GovernanceDriftSignal]:
    recent_text = _current_change_text(context)
    recent_tokens = set(_tokens(recent_text))
    if not recent_tokens:
        return []
    signals: list[GovernanceDriftSignal] = []
    for log_ref in context.log_refs:
        issue_lines = _issue_lines(log_ref.text)
        for line in issue_lines[:6]:
            line_tokens = set(_tokens(line))
            if len(line_tokens & recent_tokens) < 3:
                continue
            signals.append(
                GovernanceDriftSignal(
                    id=f"repeated-postmortem-{_slug(log_ref.path)}-{_slug(line)[:24]}",
                    type="repeated_postmortem_issue",
                    severity="warning",
                    title="Recent context resembles a historical issue",
                    detail="A prior update log or postmortem issue appears similar to recent governance context.",
                    evidence=[
                        log_ref.evidence(excerpt=line),
                        DriftEvidence(kind="recent_context", title="recent governance context", excerpt=_bounded_excerpt(recent_text)),
                    ],
                    recommended_next_action="Review the historical issue before repeating the same implementation pattern.",
                )
            )
            break
    return signals


def _detect_unsynced_decisions(context: GovernanceDriftContext) -> list[GovernanceDriftSignal]:
    spec_text = "\n".join([spec.name, *spec.requirements] for spec in context.spec_refs) if False else "\n".join(
        f"{spec.name} {' '.join(spec.requirements)}" for spec in context.spec_refs
    )
    rule_text = "\n".join(f"{rule.get('title', '')} {rule.get('description', '')}" for rule in context.accepted_rules)
    baseline_tokens = set(_tokens(f"{spec_text}\n{rule_text}"))
    signals: list[GovernanceDriftSignal] = []

    for change in context.archived_changes:
        for marker in change.decision_markers[:3]:
            marker_tokens = set(_tokens(marker))
            if marker_tokens and len(marker_tokens & baseline_tokens) >= 2:
                continue
            signals.append(
                GovernanceDriftSignal(
                    id=f"unsynced-decision-{change.name}-{_slug(marker)[:24]}",
                    type="unsynced_decision",
                    severity="warning",
                    title="Archived human decision may not be synchronized",
                    detail=f"Archived change '{change.name}' contains a decision-like statement that is not clearly reflected in main specs or accepted rules.",
                    evidence=[change.evidence(excerpt=marker)],
                    recommended_next_action="Decide whether this human decision should update a main spec or become an accepted governance rule.",
                )
            )
            break

    for log_ref in context.log_refs:
        for marker in _decision_markers_from_text(log_ref.text)[:2]:
            marker_tokens = set(_tokens(marker))
            if marker_tokens and len(marker_tokens & baseline_tokens) >= 2:
                continue
            signals.append(
                GovernanceDriftSignal(
                    id=f"unsynced-decision-{_slug(log_ref.path)}-{_slug(marker)[:24]}",
                    type="unsynced_decision",
                    severity="warning",
                    title="Logged human decision may not be synchronized",
                    detail="A project log contains a decision-like statement that is not clearly reflected in main specs or accepted rules.",
                    evidence=[log_ref.evidence(excerpt=marker)],
                    recommended_next_action="Review whether the logged decision should be captured in specs or accepted governance rules.",
                )
            )
            break
    return signals


def _status_from_signals(signals: list[GovernanceDriftSignal], human_decisions_needed: list[str]) -> str:
    if human_decisions_needed:
        return "review_required"
    if any(signal.severity == "blocker" for signal in signals):
        return "review_required"
    if any(signal.severity == "warning" for signal in signals):
        return "drift_detected"
    if signals:
        return "watch"
    return "clean"


def _human_decisions_needed(signals: list[GovernanceDriftSignal]) -> list[str]:
    decisions: list[str] = []
    for signal in signals:
        if signal.type == "unsynced_decision":
            decisions.append("Decide whether the detected human decision should update main specs or accepted governance rules.")
        elif signal.type == "stale_rule":
            decisions.append("Decide whether the inactive governance rule should remain inactive, be superseded, or be replaced.")
    return _dedupe_strings(decisions)


def _recommended_actions(signals: list[GovernanceDriftSignal], human_decisions: list[str]) -> list[str]:
    actions = [signal.recommended_next_action for signal in signals if signal.recommended_next_action]
    actions.extend(human_decisions)
    if not actions:
        actions.append("No governance drift signals detected. Continue normal review.")
    return _dedupe_strings(actions)


def _recent_topic_tokens(context: GovernanceDriftContext) -> set[str]:
    text = _recent_text(context)
    tokens = set(_tokens(text))
    for path in context.diff_context.all_paths:
        tokens.update(_tokens(Path(path.replace("\\", "/")).stem.replace("-", " ").replace("_", " ")))
    return {token for token in tokens if len(token) > 3}


def _recent_text(context: GovernanceDriftContext) -> str:
    parts: list[str] = []
    parts.extend(change.combined_text for change in context.archived_changes[:5])
    parts.append(context.diff_context.diff)
    parts.extend(context.diff_context.all_paths)
    return "\n".join(part for part in parts if part)


def _current_change_text(context: GovernanceDriftContext) -> str:
    parts = [context.diff_context.diff, *context.diff_context.all_paths]
    return "\n".join(part for part in parts if part)


def _document_ref(*, root: Path, path: Path, kind: str) -> DocumentRef:
    text = _read_text(path)
    return DocumentRef(
        kind=kind,
        path=str(path.relative_to(root)),
        title=path.name,
        excerpt=_bounded_excerpt(text),
        text=text,
    )


def _capabilities_from_proposal(text: str) -> list[str]:
    capabilities: list[str] = []
    in_capabilities = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("### New Capabilities"):
            in_capabilities = True
            continue
        if in_capabilities and stripped.startswith("### "):
            break
        if not in_capabilities:
            continue
        match = re.search(r"`([a-z0-9][a-z0-9-]+)`", stripped)
        if match:
            capabilities.append(match.group(1))
    return _dedupe_strings(capabilities)


def _decision_markers_from_text(text: str) -> list[str]:
    markers: list[str] = []
    patterns = (
        r"(?im)^\s*(?:[-*]\s*)?(?:decision|decided|we decided)\s*:\s*(.+)$",
        r"(?im)^\s*(?:[-*]\s*)?(?:人工决策|决定|选择)\s*[:：]\s*(.+)$",
    )
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            markers.append(match.group(1).strip())
    return _dedupe_strings(markers)


def _issue_lines(text: str) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip().lstrip("-* ").strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if any(marker in lowered for marker in ("issue", "error", "bug", "regression", "failed", "failure", "错误", "失败", "问题")):
            lines.append(stripped)
    return lines


def _requirement_names(text: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"(?m)^### Requirement:\s*(.+?)\s*$", text)]


def _normalize_rule(rule: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": rule.get("id"),
        "title": str(rule.get("title") or "Untitled governance rule"),
        "description": str(rule.get("description") or ""),
        "severity": str(rule.get("severity") or "warning").lower(),
        "scope": str(rule.get("scope") or "all").lower(),
        "source_title": rule.get("source_title"),
        "source_path": rule.get("source_path"),
        "source_excerpt": rule.get("source_excerpt"),
        "review_state": str(rule.get("review_state") or "accepted").lower(),
        "status": str(rule.get("status") or "active").lower(),
        "lifecycle_status": str(rule.get("lifecycle_status") or "current").lower(),
        "superseded_by_rule_id": rule.get("superseded_by_rule_id"),
        "lifecycle_rationale": rule.get("lifecycle_rationale"),
        "document_status": str(rule.get("document_status") or "active").lower(),
        "document_type": str(rule.get("document_type") or "").lower(),
    }


def _is_active_accepted_rule(rule: dict[str, Any]) -> bool:
    return (
        str(rule.get("review_state") or "").lower() == "accepted"
        and str(rule.get("status") or "").lower() == "active"
        and str(rule.get("lifecycle_status") or "current").lower() == "current"
        and str(rule.get("document_status") or "active").lower() == "active"
    )


def _sqlite_path(*, repo_root: Path, database_url: str | None) -> Path | None:
    if database_url and database_url.startswith("sqlite:///"):
        path_value = database_url.removeprefix("sqlite:///")
        path = Path(path_value)
        return path if path.is_absolute() else repo_root / path
    candidates = [
        repo_root / "services" / "engine" / "decisionatlas.db",
        repo_root / "decisionatlas.db",
    ]
    return next((candidate for candidate in candidates if candidate.exists()), None)


def _tokens(text: str) -> list[str]:
    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "that",
        "this",
        "shall",
        "must",
        "should",
        "decision",
        "governance",
        "change",
        "changes",
        "rule",
        "rules",
        "docs",
        "project",
        "script",
        "scripts",
        "service",
        "services",
        "engine",
        "test",
        "tests",
        "report",
        "local",
        "current",
    }
    return [token for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_]{2,}", text.lower()) if token not in stop_words]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _bounded_excerpt(text: str, limit: int = 1200) -> str:
    return re.sub(r"\s+", " ", text).strip()[:limit]


def _dedupe_strings(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _dedupe_signals(signals: Iterable[GovernanceDriftSignal]) -> list[GovernanceDriftSignal]:
    seen: set[str] = set()
    result: list[GovernanceDriftSignal] = []
    for signal in signals:
        if signal.id in seen:
            continue
        seen.add(signal.id)
        result.append(signal)
    return result


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


if __name__ == "__main__":
    raise SystemExit(main())
