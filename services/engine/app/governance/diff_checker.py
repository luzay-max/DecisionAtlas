from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


CHECK_STATUSES = {"pass", "warning", "blocked"}
FINDING_SEVERITIES = {"note", "warning", "blocker"}
CODE_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".sql",
}
TEST_MARKERS = ("test", "tests", "spec", "fixtures")


@dataclass(frozen=True)
class SourceReference:
    kind: str
    path: str | None = None
    title: str | None = None
    excerpt: str | None = None
    id: str | int | None = None


@dataclass(frozen=True)
class GovernanceFinding:
    id: str
    severity: str
    title: str
    detail: str
    source: SourceReference | None = None


@dataclass(frozen=True)
class MatchedRule:
    id: str | int | None
    title: str
    severity: str
    scope: str
    source_title: str | None = None
    source_excerpt: str | None = None


@dataclass(frozen=True)
class GovernanceCheckResult:
    status: str
    findings: list[GovernanceFinding] = field(default_factory=list)
    matched_rules: list[MatchedRule] = field(default_factory=list)
    conflicts: list[GovernanceFinding] = field(default_factory=list)
    required_tests: list[str] = field(default_factory=list)
    recommended_next_action: str = "No action required."
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GitDiffContext:
    diff: str
    paths: list[str]
    untracked_paths: list[str]

    @property
    def all_paths(self) -> list[str]:
        return [*self.paths, *self.untracked_paths]

    @property
    def has_code_changes(self) -> bool:
        return any(_is_code_path(path) for path in self.all_paths)

    @property
    def has_test_changes(self) -> bool:
        return any(_is_test_path(path) for path in self.all_paths)


@dataclass(frozen=True)
class OpenSpecContext:
    active_changes: list[str]
    text_by_path: dict[str, str]
    validation_tasks: list[str]


@dataclass(frozen=True)
class ProjectContext:
    roadmap_refs: list[SourceReference]
    spec_refs: list[SourceReference]


def run_governance_check(
    *,
    root: Path | str,
    owner_scope: str = "local-default",
    diff_text: str | None = None,
    status_text: str | None = None,
    accepted_rules: list[dict[str, Any]] | None = None,
    database_url: str | None = None,
) -> GovernanceCheckResult:
    repo_root = Path(root).resolve()
    diff_context = collect_git_diff(repo_root, diff_text=diff_text, status_text=status_text)
    openspec_context = collect_openspec_context(repo_root)
    project_context = collect_project_context(repo_root)
    rules = collect_accepted_governance_rules(
        repo_root=repo_root,
        owner_scope=owner_scope,
        accepted_rules=accepted_rules,
        database_url=database_url,
    )
    findings: list[GovernanceFinding] = []
    matched_rules: list[MatchedRule] = []
    conflicts: list[GovernanceFinding] = []
    required_tests: list[str] = []

    findings.extend(_evaluate_missing_openspec(diff_context, openspec_context))

    rule_findings, rule_matches = _evaluate_accepted_rules(diff_context, rules)
    findings.extend(rule_findings)
    matched_rules.extend(rule_matches)
    conflicts.extend(finding for finding in rule_findings if finding.severity == "blocker")

    validation_findings, validation_requirements = _evaluate_validation_expectations(
        diff_context=diff_context,
        openspec_context=openspec_context,
        rules=rules,
    )
    findings.extend(validation_findings)
    required_tests.extend(validation_requirements)

    findings.extend(_evaluate_roadmap_alignment(diff_context, openspec_context, project_context))
    findings = _dedupe_findings(findings)
    required_tests = _dedupe_strings(required_tests)
    status = _status_from_findings(findings)
    return GovernanceCheckResult(
        status=status,
        findings=findings,
        matched_rules=_dedupe_matched_rules(matched_rules),
        conflicts=conflicts,
        required_tests=required_tests,
        recommended_next_action=_recommended_next_action(status, findings, required_tests),
        context={
            "diff_paths": diff_context.all_paths,
            "active_openspec_changes": openspec_context.active_changes,
            "roadmap_refs": len(project_context.roadmap_refs),
            "spec_refs": len(project_context.spec_refs),
            "accepted_rule_count": len(rules),
            "advisory_only": True,
        },
    )


def collect_git_diff(root: Path, *, diff_text: str | None = None, status_text: str | None = None) -> GitDiffContext:
    diff = diff_text if diff_text is not None else _workspace_diff(root)
    status = status_text if status_text is not None else _git(root, "status", "--short")
    paths = _paths_from_diff(diff)
    untracked = _untracked_paths_from_status(status)
    return GitDiffContext(diff=diff, paths=paths, untracked_paths=untracked)


def collect_openspec_context(root: Path) -> OpenSpecContext:
    changes_dir = root / "openspec" / "changes"
    active_changes: list[str] = []
    text_by_path: dict[str, str] = {}
    validation_tasks: list[str] = []
    if not changes_dir.exists():
        return OpenSpecContext(active_changes=[], text_by_path={}, validation_tasks=[])

    for change_dir in sorted(path for path in changes_dir.iterdir() if path.is_dir() and path.name != "archive"):
        if not (change_dir / ".openspec.yaml").exists():
            continue
        active_changes.append(change_dir.name)
        for relative_name in ("proposal.md", "design.md", "tasks.md"):
            file_path = change_dir / relative_name
            if file_path.exists():
                text = _read_text(file_path)
                text_by_path[str(file_path.relative_to(root))] = text
                if relative_name == "tasks.md":
                    validation_tasks.extend(_validation_tasks_from_text(text))
        specs_dir = change_dir / "specs"
        if specs_dir.exists():
            for spec_file in sorted(specs_dir.rglob("*.md")):
                text_by_path[str(spec_file.relative_to(root))] = _read_text(spec_file)
    return OpenSpecContext(active_changes=active_changes, text_by_path=text_by_path, validation_tasks=validation_tasks)


def collect_project_context(root: Path) -> ProjectContext:
    roadmap_refs: list[SourceReference] = []
    for plan_path in sorted((root / "docs" / "plans").glob("*.md")) if (root / "docs" / "plans").exists() else []:
        text = _read_text(plan_path)
        if any(marker in text.lower() for marker in ("roadmap", "路线", "阶段", "governance diff checker")):
            roadmap_refs.append(
                SourceReference(
                    kind="roadmap",
                    path=str(plan_path.relative_to(root)),
                    title=plan_path.name,
                    excerpt=_bounded_excerpt(text),
                )
            )

    spec_refs: list[SourceReference] = []
    specs_root = root / "openspec" / "specs"
    if specs_root.exists():
        for spec_path in sorted(specs_root.glob("*/spec.md")):
            text = _read_text(spec_path)
            spec_refs.append(
                SourceReference(
                    kind="spec",
                    path=str(spec_path.relative_to(root)),
                    title=spec_path.parent.name,
                    excerpt=_bounded_excerpt(text),
                )
            )
    return ProjectContext(roadmap_refs=roadmap_refs[:5], spec_refs=spec_refs[:30])


def collect_accepted_governance_rules(
    *,
    repo_root: Path,
    owner_scope: str,
    accepted_rules: list[dict[str, Any]] | None = None,
    database_url: str | None = None,
) -> list[dict[str, Any]]:
    if accepted_rules is not None:
        return [_normalize_rule(rule) for rule in accepted_rules if _is_accepted_rule(rule)]

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
            d.title AS source_title,
            d.source_path AS source_path
        FROM governance_rule_drafts r
        JOIN governance_documents d ON d.id = r.document_id
        WHERE r.owner_scope = ?
          AND r.review_state = 'accepted'
          AND r.status = 'active'
        ORDER BY r.reviewed_at DESC, r.id DESC
    """
    try:
        with sqlite3.connect(db_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(query, (owner_scope,)).fetchall()
    except sqlite3.Error:
        return []
    return [_normalize_rule(dict(row)) for row in rows]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a local DecisionAtlas governance diff check.")
    parser.add_argument("--root", default=".", help="Repository root to inspect.")
    parser.add_argument("--owner-scope", default=os.environ.get("DECISIONATLAS_OWNER_SCOPE", "local-default"))
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args(argv)

    result = run_governance_check(root=Path(args.root), owner_scope=args.owner_scope, database_url=args.database_url)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


def _workspace_diff(root: Path) -> str:
    parts = [_git(root, "diff", "--cached"), _git(root, "diff")]
    return "\n".join(part for part in parts if part.strip())


def _git(root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return ""
    return completed.stdout if completed.returncode == 0 else ""


def _paths_from_diff(diff: str) -> list[str]:
    paths: list[str] = []
    for line in diff.splitlines():
        if not line.startswith("diff --git "):
            continue
        match = re.match(r"diff --git a/(.+?) b/(.+)$", line)
        if match:
            paths.append(match.group(2))
    return _dedupe_strings(paths)


def _untracked_paths_from_status(status: str) -> list[str]:
    paths: list[str] = []
    for line in status.splitlines():
        if line.startswith("?? "):
            paths.append(line[3:].strip().rstrip("/"))
    return _dedupe_strings(paths)


def _evaluate_missing_openspec(diff_context: GitDiffContext, openspec_context: OpenSpecContext) -> list[GovernanceFinding]:
    if not diff_context.has_code_changes or openspec_context.active_changes:
        return []
    code_paths = ", ".join(path for path in diff_context.all_paths if _is_code_path(path))[:500]
    return [
        GovernanceFinding(
            id="missing-openspec-context",
            severity="blocker",
            title="Code changes need OpenSpec context",
            detail=f"Current code changes have no active OpenSpec change. Affected paths: {code_paths}",
            source=SourceReference(kind="openspec", title="active changes", excerpt="No active OpenSpec change detected."),
        )
    ]


def _evaluate_accepted_rules(diff_context: GitDiffContext, rules: list[dict[str, Any]]) -> tuple[list[GovernanceFinding], list[MatchedRule]]:
    findings: list[GovernanceFinding] = []
    matched: list[MatchedRule] = []
    for rule in rules:
        if not _rule_scope_matches_diff(rule, diff_context):
            continue
        if _rule_requires_tests(rule) and diff_context.has_code_changes and not diff_context.has_test_changes:
            matched_rule = _matched_rule(rule)
            matched.append(matched_rule)
            severity = _normalize_finding_severity(rule.get("severity", "warning"))
            findings.append(
                GovernanceFinding(
                    id=f"accepted-rule-{matched_rule.id or matched_rule.title}-missing-tests",
                    severity=severity,
                    title="Accepted governance rule expects validation",
                    detail=f"Rule '{matched_rule.title}' applies to the current code change, but no test or validation file changes were detected.",
                    source=SourceReference(
                        kind="governance_rule",
                        id=matched_rule.id,
                        title=matched_rule.source_title or matched_rule.title,
                        excerpt=matched_rule.source_excerpt,
                    ),
                )
            )
        elif _rule_text_overlaps_diff(rule, diff_context):
            matched_rule = _matched_rule(rule)
            matched.append(matched_rule)
            findings.append(
                GovernanceFinding(
                    id=f"accepted-rule-{matched_rule.id or matched_rule.title}-review",
                    severity=_normalize_finding_severity(rule.get("severity", "warning")),
                    title="Accepted governance rule may apply",
                    detail=f"Rule '{matched_rule.title}' appears related to the current change. Review the source-linked rule before merge.",
                    source=SourceReference(
                        kind="governance_rule",
                        id=matched_rule.id,
                        title=matched_rule.source_title or matched_rule.title,
                        excerpt=matched_rule.source_excerpt,
                    ),
                )
            )
    return findings, matched


def _evaluate_validation_expectations(
    *,
    diff_context: GitDiffContext,
    openspec_context: OpenSpecContext,
    rules: list[dict[str, Any]],
) -> tuple[list[GovernanceFinding], list[str]]:
    required_tests = list(openspec_context.validation_tasks)
    if diff_context.has_code_changes:
        required_tests.append("Run or add targeted tests for changed behavior.")
    if any(_rule_requires_tests(rule) for rule in rules):
        required_tests.append("Satisfy accepted governance rules that require validation evidence.")

    findings: list[GovernanceFinding] = []
    if diff_context.has_code_changes and not diff_context.has_test_changes:
        findings.append(
            GovernanceFinding(
                id="missing-validation-evidence",
                severity="warning",
                title="Validation evidence is missing",
                detail="Code paths changed, but no test, fixture, or spec-test paths were changed in the current diff.",
                source=SourceReference(kind="validation", title="diff path analysis"),
            )
        )
    return findings, _dedupe_strings(required_tests)


def _evaluate_roadmap_alignment(
    diff_context: GitDiffContext,
    openspec_context: OpenSpecContext,
    project_context: ProjectContext,
) -> list[GovernanceFinding]:
    if not diff_context.has_code_changes or not project_context.roadmap_refs or not openspec_context.active_changes:
        return []
    haystack = "\n".join(openspec_context.text_by_path.values()).lower()
    changed_terms = _tokens_from_paths(diff_context.all_paths)
    if not changed_terms:
        return []
    roadmap_text = "\n".join(ref.excerpt or "" for ref in project_context.roadmap_refs).lower()
    aligned_terms = [term for term in changed_terms if term in haystack or term in roadmap_text]
    if aligned_terms:
        return []
    return [
        GovernanceFinding(
            id="ambiguous-roadmap-alignment",
            severity="warning",
            title="Roadmap alignment needs human review",
            detail="The current code paths do not obviously match active OpenSpec or roadmap terms. Review before merge.",
            source=project_context.roadmap_refs[0],
        )
    ]


def _status_from_findings(findings: Iterable[GovernanceFinding]) -> str:
    severities = {finding.severity for finding in findings}
    if "blocker" in severities:
        return "blocked"
    if "warning" in severities:
        return "warning"
    return "pass"


def _recommended_next_action(status: str, findings: list[GovernanceFinding], required_tests: list[str]) -> str:
    if status == "blocked":
        blocker = next((finding for finding in findings if finding.severity == "blocker"), None)
        return blocker.detail if blocker else "Resolve blocker findings before merge."
    if required_tests:
        return required_tests[0]
    if status == "warning":
        warning = next((finding for finding in findings if finding.severity == "warning"), None)
        return warning.detail if warning else "Review warning findings before merge."
    return "No governance blockers detected. Continue with normal review."


def _normalize_rule(rule: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": rule.get("id"),
        "title": str(rule.get("title") or "Untitled governance rule"),
        "description": str(rule.get("description") or ""),
        "severity": str(rule.get("severity") or "warning").lower(),
        "scope": str(rule.get("scope") or "all").lower(),
        "source_title": rule.get("source_title"),
        "source_excerpt": rule.get("source_excerpt"),
        "review_state": str(rule.get("review_state") or "accepted").lower(),
        "status": str(rule.get("status") or "active").lower(),
    }


def _is_accepted_rule(rule: dict[str, Any]) -> bool:
    return str(rule.get("review_state", "accepted")).lower() == "accepted" and str(rule.get("status", "active")).lower() == "active"


def _matched_rule(rule: dict[str, Any]) -> MatchedRule:
    return MatchedRule(
        id=rule.get("id"),
        title=rule["title"],
        severity=_normalize_finding_severity(rule.get("severity", "warning")),
        scope=rule.get("scope", "all"),
        source_title=rule.get("source_title"),
        source_excerpt=rule.get("source_excerpt"),
    )


def _rule_requires_tests(rule: dict[str, Any]) -> bool:
    text = f"{rule.get('title', '')} {rule.get('description', '')} {rule.get('source_excerpt', '')}".lower()
    return any(marker in text for marker in ("test", "tests", "pytest", "validation", "验证", "测试"))


def _rule_text_overlaps_diff(rule: dict[str, Any], diff_context: GitDiffContext) -> bool:
    if not diff_context.diff.strip():
        return False
    rule_tokens = set(_tokens(f"{rule.get('title', '')} {rule.get('description', '')}"))
    if not rule_tokens:
        return False
    diff_tokens = set(_tokens(diff_context.diff))
    return len(rule_tokens & diff_tokens) >= 2


def _rule_scope_matches_diff(rule: dict[str, Any], diff_context: GitDiffContext) -> bool:
    scope = str(rule.get("scope") or "all").lower()
    if scope == "all":
        return True
    return any(_path_matches_scope(path, scope) for path in diff_context.all_paths)


def _path_matches_scope(path: str, scope: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    if scope == "engine":
        return normalized.startswith("services/engine/")
    if scope == "api":
        return normalized.startswith("apps/api/")
    if scope == "frontend":
        return normalized.startswith("apps/web/")
    if scope == "docs":
        return normalized.startswith("docs/") or normalized.endswith(".md")
    if scope == "release":
        return "release" in normalized or normalized.startswith("scripts/ci/")
    if scope == "security":
        return "auth" in normalized or "security" in normalized or "token" in normalized
    if scope == "roadmap":
        return normalized.startswith("docs/plans/") or "roadmap" in normalized
    return True


def _is_code_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    suffix = Path(normalized).suffix.lower()
    if suffix not in CODE_EXTENSIONS:
        return False
    return not _is_test_path(normalized)


def _is_test_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    parts = set(normalized.split("/"))
    if parts & set(TEST_MARKERS):
        return True
    name = Path(normalized).name
    return name.startswith("test_") or name.endswith(".test.ts") or name.endswith(".test.tsx") or name.endswith(".spec.ts")


def _validation_tasks_from_text(text: str) -> list[str]:
    tasks: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- ["):
            continue
        lowered = stripped.lower()
        if any(marker in lowered for marker in ("test", "validation", "validate", "pytest", "playwright", "校验", "验证")):
            tasks.append(re.sub(r"^- \[[ xX]\]\s*", "", stripped))
    return tasks


def _tokens_from_paths(paths: list[str]) -> list[str]:
    tokens: list[str] = []
    for path in paths:
        tokens.extend(_tokens(Path(path).stem.replace("-", " ").replace("_", " ")))
        tokens.extend(part for part in path.replace("\\", "/").split("/") if len(part) > 3)
    return _dedupe_strings(tokens)


def _tokens(text: str) -> list[str]:
    stop_words = {"the", "and", "for", "with", "from", "that", "this", "shall", "must", "should"}
    return [token for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_]{2,}", text.lower()) if token not in stop_words]


def _normalize_finding_severity(value: str) -> str:
    normalized = str(value).lower()
    if normalized == "blocked":
        return "blocker"
    return normalized if normalized in FINDING_SEVERITIES else "warning"


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
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _dedupe_findings(findings: Iterable[GovernanceFinding]) -> list[GovernanceFinding]:
    seen: set[str] = set()
    result: list[GovernanceFinding] = []
    for finding in findings:
        if finding.id in seen:
            continue
        seen.add(finding.id)
        result.append(finding)
    return result


def _dedupe_matched_rules(rules: Iterable[MatchedRule]) -> list[MatchedRule]:
    seen: set[tuple[str | int | None, str]] = set()
    result: list[MatchedRule] = []
    for rule in rules:
        key = (rule.id, rule.title)
        if key in seen:
            continue
        seen.add(key)
        result.append(rule)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
