from __future__ import annotations

import json
from pathlib import Path

from app.governance.drift_detector import collect_governance_drift_context, main, run_governance_drift_detection


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "governance_drift_detector"


def _fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _write_project_context(root: Path, *, roadmap: str | None = None, spec_name: str = "governance-drift-detection") -> None:
    plan_dir = root / "docs" / "plans"
    plan_dir.mkdir(parents=True)
    (plan_dir / "master-plan.md").write_text(
        roadmap or "# Roadmap\n\nGovernance drift detection keeps OpenSpec specs and accepted governance rules aligned.\n",
        encoding="utf-8",
    )
    spec_dir = root / "openspec" / "specs" / spec_name
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "## Purpose\nTrack governance drift.\n\n## Requirements\n\n### Requirement: Governance drift report exists\nThe system SHALL produce a report.\n",
        encoding="utf-8",
    )


def _write_archived_change(
    root: Path,
    *,
    name: str = "2026-05-01-add-governance-drift-detection",
    capability: str = "governance-drift-detection",
    design: str = "## Context\nNo explicit decision marker.\n",
) -> None:
    change_dir = root / "openspec" / "changes" / "archive" / name
    change_dir.mkdir(parents=True)
    (change_dir / ".openspec.yaml").write_text("schema: spec-driven\n", encoding="utf-8")
    (change_dir / "proposal.md").write_text(
        "## Capabilities\n\n### New Capabilities\n\n"
        f"- `{capability}`: Adds a capability for governance drift reporting.\n",
        encoding="utf-8",
    )
    (change_dir / "design.md").write_text(design, encoding="utf-8")
    (change_dir / "tasks.md").write_text("- [x] 1.1 Run targeted tests.\n", encoding="utf-8")


def _write_project_log(root: Path, text: str) -> None:
    docs_dir = root / "docs" / "project"
    docs_dir.mkdir(parents=True)
    (docs_dir / "2026-05-01-update-log.md").write_text(text, encoding="utf-8")


def test_clean_report_has_machine_readable_shape(tmp_path: Path) -> None:
    data = _fixture("clean.json")
    _write_project_context(tmp_path, roadmap=data["roadmap"], spec_name=data["spec_name"])

    report = run_governance_drift_detection(root=tmp_path, governance_rules=[])

    assert report.status == data["expected_status"]
    assert report.signals == []
    body = report.to_dict()
    assert "status" in body
    assert "signals" in body
    assert "human_decisions_needed" in body
    assert "recommended_next_actions" in body
    assert body["context"]["advisory_only"] is True


def test_context_collection_reads_roadmap_specs_archives_logs_rules_and_diff(tmp_path: Path) -> None:
    _write_project_context(tmp_path)
    _write_archived_change(tmp_path)
    _write_project_log(tmp_path, "# Update\n\n- Issue: Redis timeout error caused import retry failure.\n")

    context = collect_governance_drift_context(
        tmp_path,
        governance_rules=[
            {
                "id": 1,
                "title": "Accepted validation rule",
                "description": "Run targeted tests.",
                "review_state": "accepted",
                "status": "active",
            }
        ],
        diff_text="diff --git a/services/engine/app/foo.py b/services/engine/app/foo.py\n",
    )

    assert len(context.roadmap_refs) == 1
    assert [spec.name for spec in context.spec_refs] == ["governance-drift-detection"]
    assert len(context.archived_changes) == 1
    assert len(context.log_refs) == 1
    assert len(context.accepted_rules) == 1
    assert context.diff_context.paths == ["services/engine/app/foo.py"]


def test_watch_status_for_ambiguous_roadmap_alignment(tmp_path: Path) -> None:
    data = _fixture("watch.json")
    _write_project_context(tmp_path)

    report = run_governance_drift_detection(root=tmp_path, governance_rules=[], diff_text=data["diff"], status_text="")

    assert report.status == data["expected_status"]
    assert any(signal.type == "roadmap_mismatch" for signal in report.signals)


def test_spec_gap_signal_for_archived_capability_missing_from_main_specs(tmp_path: Path) -> None:
    data = _fixture("drift_detected.json")
    _write_project_context(tmp_path)
    _write_archived_change(tmp_path, capability=data["missing_capability"])

    report = run_governance_drift_detection(root=tmp_path, governance_rules=[])

    assert report.status == data["expected_status"]
    assert any(signal.type == "spec_gap" for signal in report.signals)


def test_stale_rule_signal_uses_inactive_rules_as_review_evidence(tmp_path: Path) -> None:
    _write_project_context(tmp_path)
    diff = "diff --git a/services/engine/app/token_policy.py b/services/engine/app/token_policy.py\n+legacy token handling remains active\n"

    report = run_governance_drift_detection(
        root=tmp_path,
        diff_text=diff,
        governance_rules=[
            {
                "id": 9,
                "title": "Legacy token handling",
                "description": "Legacy token handling was rejected and should not be reused.",
                "review_state": "rejected",
                "status": "rejected",
                "source_excerpt": "Legacy token handling",
            }
        ],
    )

    assert report.status == "review_required"
    assert any(signal.type == "stale_rule" for signal in report.signals)
    assert report.human_decisions_needed


def test_superseded_rule_reuse_is_lifecycle_review_signal_not_active_rule(tmp_path: Path) -> None:
    _write_project_context(tmp_path)
    diff = "diff --git a/services/engine/app/token_policy.py b/services/engine/app/token_policy.py\n+legacy token handling remains active\n"

    report = run_governance_drift_detection(
        root=tmp_path,
        diff_text=diff,
        governance_rules=[
            {
                "id": 10,
                "title": "Legacy token handling",
                "description": "Legacy token handling should not be reused.",
                "review_state": "accepted",
                "status": "active",
                "lifecycle_status": "superseded",
                "superseded_by_rule_id": 11,
                "lifecycle_rationale": "Replacement requires scoped token access.",
                "source_excerpt": "Legacy token handling",
            },
            {
                "id": 11,
                "title": "Scoped token access",
                "description": "Use scoped token access for repository imports.",
                "review_state": "accepted",
                "status": "active",
                "lifecycle_status": "current",
            },
        ],
    )

    assert report.context["accepted_rule_count"] == 1
    signal = next(signal for signal in report.signals if signal.type == "stale_rule")
    assert signal.evidence[0].lifecycle_status == "superseded"
    assert signal.evidence[0].superseded_by_rule_id == 11
    assert "recorded replacement" in (signal.recommended_next_action or "")


def test_repeated_postmortem_issue_signal_links_prior_and_recent_evidence(tmp_path: Path) -> None:
    _write_project_context(tmp_path)
    _write_project_log(tmp_path, "# Postmortem\n\n- Issue: Redis timeout error caused import retry failure.\n")
    diff = "diff --git a/services/engine/app/import_retry.py b/services/engine/app/import_retry.py\n+redis timeout error import retry failure\n"

    report = run_governance_drift_detection(root=tmp_path, governance_rules=[], diff_text=diff)

    assert any(signal.type == "repeated_postmortem_issue" for signal in report.signals)
    repeated = next(signal for signal in report.signals if signal.type == "repeated_postmortem_issue")
    assert len(repeated.evidence) >= 2


def test_unsynced_decision_signal_requests_human_review(tmp_path: Path) -> None:
    data = _fixture("review_required.json")
    _write_project_context(tmp_path)
    _write_archived_change(
        tmp_path,
        design=f"## Context\n\nDecision: {data['decision_marker']}\n",
    )

    report = run_governance_drift_detection(root=tmp_path, governance_rules=[])

    assert report.status == data["expected_status"]
    assert any(signal.type == "unsynced_decision" for signal in report.signals)
    assert any("accepted governance rules" in decision or "main specs" in decision for decision in report.human_decisions_needed)


def test_cli_accepts_api_shaped_rules_json(tmp_path: Path, capsys) -> None:
    _write_project_context(tmp_path)
    rules_file = tmp_path / "rules.json"
    rules_file.write_text(
        json.dumps(
            {
                "rules": [
                    {
                        "id": 3,
                        "title": "Accepted governance rule",
                        "description": "Keep drift reports advisory.",
                        "review_state": "accepted",
                        "status": "active",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["--root", str(tmp_path), "--rules-json", str(rules_file)])

    assert exit_code == 0
    body = json.loads(capsys.readouterr().out)
    assert body["context"]["governance_rules"] == 1
    assert body["context"]["accepted_rule_count"] == 1
