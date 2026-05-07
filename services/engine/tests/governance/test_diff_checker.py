from __future__ import annotations

import json
from pathlib import Path

from app.governance.diff_checker import collect_accepted_governance_rules, run_governance_check


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "governance_diff_checker"


def _fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _write_active_change(root: Path, *, tasks: str | None = None) -> None:
    change_dir = root / "openspec" / "changes" / "add-governance-diff-checker"
    change_dir.mkdir(parents=True)
    (change_dir / ".openspec.yaml").write_text("schema: spec-driven\n", encoding="utf-8")
    (change_dir / "proposal.md").write_text("## Why\nGovernance diff checker.\n", encoding="utf-8")
    (change_dir / "design.md").write_text("## Context\nLocal deterministic checker.\n", encoding="utf-8")
    (change_dir / "tasks.md").write_text(
        tasks or "- [ ] 1.1 Add targeted checker tests and run validation.\n",
        encoding="utf-8",
    )


def _write_project_context(root: Path) -> None:
    plan_dir = root / "docs" / "plans"
    plan_dir.mkdir(parents=True)
    (plan_dir / "master-plan.md").write_text(
        "# Plan\n\nStage 5 Governance Diff Checker should inspect git diff and accepted rules.\n",
        encoding="utf-8",
    )
    spec_dir = root / "openspec" / "specs" / "governance-diff-checker"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "## Purpose\nDefine governance diff checker behavior.\n",
        encoding="utf-8",
    )


def test_missing_openspec_context_blocks_nontrivial_code_change(tmp_path: Path) -> None:
    _write_project_context(tmp_path)
    result = run_governance_check(
        root=tmp_path,
        diff_text=_fixture("blocked_missing_openspec.json")["diff"],
        accepted_rules=[],
    )

    assert result.status == "blocked"
    assert any(finding.id == "missing-openspec-context" for finding in result.findings)


def test_accepted_rule_conflict_is_source_linked(tmp_path: Path) -> None:
    _write_project_context(tmp_path)
    _write_active_change(tmp_path)
    result = run_governance_check(
        root=tmp_path,
        diff_text=_fixture("warning_missing_validation.json")["diff"],
        accepted_rules=[
            {
                "id": 7,
                "title": "Rule: Every change must have targeted tests",
                "description": "Every backend behavior change must include targeted tests.",
                "severity": "blocker",
                "scope": "engine",
                "source_title": "Engineering Standards",
                "source_excerpt": "## Rule: Every change must have targeted tests",
                "review_rationale": "Accepted as validation baseline.",
                "rule_type": "standard",
                "extraction_reason": "rule heading marker",
                "lifecycle_status": "current",
                "review_state": "accepted",
                "status": "active",
            }
        ],
    )

    assert result.status == "blocked"
    assert result.matched_rules[0].id == 7
    assert result.matched_rules[0].review_rationale == "Accepted as validation baseline."
    assert result.matched_rules[0].rule_type == "standard"
    assert result.matched_rules[0].extraction_reason == "rule heading marker"
    assert result.matched_rules[0].lifecycle_status == "current"
    assert result.conflicts[0].source is not None
    assert result.conflicts[0].source.title == "Engineering Standards"
    assert result.conflicts[0].source.review_rationale == "Accepted as validation baseline."


def test_pending_and_rejected_rules_are_not_enforceable(tmp_path: Path) -> None:
    _write_project_context(tmp_path)
    _write_active_change(tmp_path)
    result = run_governance_check(
        root=tmp_path,
        diff_text=_fixture("pass_with_tests.json")["diff"],
        accepted_rules=[
            {
                "id": 11,
                "title": "Rule: Pending changes must block",
                "description": "This pending rule should not be enforced.",
                "severity": "blocker",
                "scope": "engine",
                "review_state": "pending",
                "status": "draft",
            },
            {
                "id": 12,
                "title": "Rule: Rejected changes must block",
                "description": "This rejected rule should not be enforced.",
                "severity": "blocker",
                "scope": "engine",
                "review_state": "rejected",
                "status": "rejected",
            },
            {
                "id": 13,
                "title": "Rule: Stale changes must block",
                "description": "This stale rule should not be enforced.",
                "severity": "blocker",
                "scope": "engine",
                "review_state": "accepted",
                "status": "active",
                "lifecycle_status": "stale",
            },
            {
                "id": 14,
                "title": "Rule: Superseded changes must block",
                "description": "This superseded rule should not be enforced.",
                "severity": "blocker",
                "scope": "engine",
                "review_state": "accepted",
                "status": "active",
                "lifecycle_status": "superseded",
            },
        ],
    )

    assert result.status == "pass"
    assert result.matched_rules == []


def test_missing_validation_evidence_warns_and_returns_required_tests(tmp_path: Path) -> None:
    _write_project_context(tmp_path)
    _write_active_change(tmp_path, tasks="- [ ] 4.4 Run targeted checker tests and OpenSpec validation.\n")
    result = run_governance_check(
        root=tmp_path,
        diff_text=_fixture("warning_missing_validation.json")["diff"],
        accepted_rules=[],
    )

    assert result.status == "warning"
    assert any(finding.id == "missing-validation-evidence" for finding in result.findings)
    assert any("targeted checker tests" in item for item in result.required_tests)
    assert "status" in result.to_dict()
    assert "recommended_next_action" in result.to_dict()


def test_collect_accepted_rules_filters_pending_and_rejected_inputs(tmp_path: Path) -> None:
    rules = collect_accepted_governance_rules(
        repo_root=tmp_path,
        owner_scope="team-a",
        accepted_rules=[
            {"id": 1, "title": "Accepted", "review_state": "accepted", "status": "active"},
            {"id": 2, "title": "Pending", "review_state": "pending", "status": "draft"},
            {"id": 3, "title": "Rejected", "review_state": "rejected", "status": "rejected"},
            {"id": 4, "title": "Stale", "review_state": "accepted", "status": "active", "lifecycle_status": "stale"},
            {
                "id": 5,
                "title": "Superseded",
                "review_state": "accepted",
                "status": "active",
                "lifecycle_status": "superseded",
            },
        ],
    )

    assert [rule["id"] for rule in rules] == [1]


def test_matched_accepted_rule_includes_review_traceability_metadata(tmp_path: Path) -> None:
    _write_project_context(tmp_path)
    _write_active_change(tmp_path)
    result = run_governance_check(
        root=tmp_path,
        diff_text=_fixture("warning_missing_validation.json")["diff"],
        accepted_rules=[
            {
                "id": 21,
                "title": "Rule: Every engine change must have tests",
                "description": "Every backend behavior change must include targeted tests.",
                "severity": "warning",
                "scope": "engine",
                "source_title": "Engineering Standards",
                "source_excerpt": "## Rule: Every engine change must have tests",
                "review_rationale": "Accepted because it is actionable and source-backed.",
                "rule_type": "standard",
                "extraction_reason": "rule heading marker",
                "lifecycle_status": "current",
                "review_state": "accepted",
                "status": "active",
            }
        ],
    )

    assert result.matched_rules
    matched = result.matched_rules[0]
    assert matched.source_excerpt == "## Rule: Every engine change must have tests"
    assert matched.review_rationale == "Accepted because it is actionable and source-backed."
    assert matched.rule_type == "standard"
    assert matched.extraction_reason == "rule heading marker"
    assert matched.lifecycle_status == "current"
