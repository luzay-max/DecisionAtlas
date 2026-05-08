from __future__ import annotations

import json
from pathlib import Path

from app.governance.agent_guardrail import (
    aggregate_governance_guardrail,
    build_development_protocol_status,
    build_enforcement_preview,
    main,
)


def _diff_check(
    *,
    status: str = "pass",
    findings: list[dict] | None = None,
    conflicts: list[dict] | None = None,
    required_tests: list[str] | None = None,
) -> dict:
    return {
        "status": status,
        "findings": findings or [],
        "matched_rules": [{"id": 1, "title": "Accepted validation rule"}] if conflicts else [],
        "conflicts": conflicts or [],
        "required_tests": required_tests or [],
        "recommended_next_action": "No governance blockers detected.",
        "context": {"advisory_only": True},
    }


def _drift_report(
    *,
    status: str = "clean",
    signals: list[dict] | None = None,
    human_decisions_needed: list[str] | None = None,
) -> dict:
    return {
        "status": status,
        "signals": signals or [],
        "human_decisions_needed": human_decisions_needed or [],
        "recommended_next_actions": ["No governance drift signals detected."],
        "context": {"advisory_only": True},
    }


def test_guardrail_returns_continue_for_clean_sources() -> None:
    result = aggregate_governance_guardrail(diff_check=_diff_check(), drift_report=_drift_report())

    assert result.agent_status == "continue"
    assert result.workflow_protocol["name"] == "decisionatlas-agent-governance-workflow"
    assert result.workflow_protocol["advisory_only"] is True
    assert "continue_implementation" in result.allowed_next_actions
    assert "run_required_tests" in result.allowed_next_actions
    assert "skip_targeted_validation" in result.disallowed_next_actions
    assert result.handoff_summary["agent_status"] == "continue"
    assert result.handoff_summary["diff_status"] == "pass"
    assert result.handoff_summary["drift_status"] == "clean"
    body = result.to_dict()
    assert body["source_results"]["diff_check"]["status"] == "pass"
    assert body["source_results"]["drift_report"]["status"] == "clean"
    assert body["agent_instruction"].startswith("Continue normal work")


def test_guardrail_returns_caution_for_non_blocking_warnings() -> None:
    result = aggregate_governance_guardrail(
        diff_check=_diff_check(
            status="warning",
            findings=[
                {
                    "id": "ambiguous-roadmap-alignment",
                    "severity": "warning",
                    "detail": "Roadmap alignment needs human review.",
                }
            ],
            required_tests=["Run targeted tests.", "Run targeted tests."],
        ),
        drift_report=_drift_report(status="watch"),
    )

    assert result.agent_status == "caution"
    assert result.required_tests == ["Run targeted tests."]
    assert "continue_with_explicit_caution_handoff" in result.allowed_next_actions
    assert "claim_completion_without_disclosing_caution" in result.disallowed_next_actions
    assert result.handoff_summary["recommended_next_actions"]
    assert result.handoff_summary["required_tests"] == ["Run targeted tests."]
    assert any("Roadmap alignment" in action for action in result.recommended_next_actions)


def test_guardrail_pauses_for_blocked_diff_and_preserves_evidence() -> None:
    conflict = {
        "id": "accepted-rule-7-missing-tests",
        "severity": "blocker",
        "title": "Accepted governance rule expects validation",
        "detail": "Rule applies but no validation evidence was found.",
        "source": {"kind": "governance_rule", "id": 7, "title": "Engineering Standards"},
    }

    result = aggregate_governance_guardrail(
        diff_check=_diff_check(status="blocked", findings=[conflict], conflicts=[conflict]),
        drift_report=_drift_report(),
    )

    assert result.agent_status == "pause"
    assert result.agent_instruction.startswith("Stop implementation")
    assert "ask_human_for_decision" in result.allowed_next_actions
    assert "silently_rewrite_openspec_to_clear_guardrail" in result.disallowed_next_actions
    assert result.human_questions
    assert result.human_questions[0]["evidence_type"] == "finding"
    assert result.findings[0]["source"]["title"] == "Engineering Standards"
    assert result.source_results["diff_check"]["conflicts"][0]["id"] == "accepted-rule-7-missing-tests"


def test_guardrail_pauses_for_unsynced_human_decision() -> None:
    result = aggregate_governance_guardrail(
        diff_check=_diff_check(),
        drift_report=_drift_report(
            status="review_required",
            signals=[
                {
                    "id": "unsynced-decision-x",
                    "type": "unsynced_decision",
                    "severity": "warning",
                    "title": "Archived human decision may not be synchronized",
                    "recommended_next_action": "Sync the decision into specs or accepted rules.",
                }
            ],
            human_decisions_needed=["Decide whether the human decision should update specs."],
        ),
    )

    assert result.agent_status == "pause"
    assert result.human_decisions_needed == ["Decide whether the human decision should update specs."]
    assert {
        "id": "human-decision-1",
        "question": "Decide whether the human decision should update specs.",
        "evidence_type": "human_decision",
        "evidence_id": "human_decisions_needed[0]",
    } in result.human_questions
    assert any(question["evidence_type"] == "signal" for question in result.human_questions)
    assert any("Sync the decision" in action for action in result.recommended_next_actions)


def test_guardrail_stale_rule_question_mentions_lifecycle_replacement() -> None:
    result = aggregate_governance_guardrail(
        diff_check=_diff_check(),
        drift_report=_drift_report(
            status="review_required",
            signals=[
                {
                    "id": "stale-rule-10",
                    "type": "stale_rule",
                    "severity": "warning",
                    "title": "Inactive governance source appears in recent context",
                    "recommended_next_action": "Confirm whether this inactive lifecycle rule should use the recorded replacement.",
                }
            ],
            human_decisions_needed=["Decide whether the inactive governance rule should remain inactive or be replaced."],
        ),
    )

    assert result.agent_status == "pause"
    assert any("recorded replacement" in question["question"] for question in result.human_questions)


def test_pause_result_is_advisory_and_does_not_mutate_files(tmp_path: Path) -> None:
    marker = tmp_path / "marker.txt"
    marker.write_text("unchanged", encoding="utf-8")

    result = aggregate_governance_guardrail(
        diff_check=_diff_check(
            status="warning",
            findings=[
                {
                    "id": "missing-validation-evidence",
                    "severity": "warning",
                    "detail": "Code paths changed without validation evidence.",
                }
            ],
        ),
        drift_report=_drift_report(),
    )

    assert result.agent_status == "pause"
    assert result.context["advisory_only"] is True
    assert result.handoff_summary["advisory_only"] is True
    assert any(
        question["question"] == "What validation evidence is required before the agent may continue or claim completion?"
        for question in result.human_questions
    )
    assert marker.read_text(encoding="utf-8") == "unchanged"


def test_cli_outputs_machine_readable_json_and_returns_success(tmp_path: Path, capsys) -> None:
    exit_code = main(["--root", str(tmp_path)])

    assert exit_code == 0
    body = json.loads(capsys.readouterr().out)
    assert set(
        [
            "agent_status",
            "summary",
            "findings",
            "signals",
            "matched_rules",
            "required_tests",
            "human_decisions_needed",
            "recommended_next_actions",
            "source_results",
            "workflow_protocol",
            "agent_instruction",
            "allowed_next_actions",
            "disallowed_next_actions",
            "human_questions",
            "handoff_summary",
        ]
    ).issubset(body)
    assert body["context"]["advisory_only"] is True
    assert body["workflow_protocol"]["advisory_only"] is True


def test_cli_summary_outputs_checkpoint_friendly_status_and_returns_success(tmp_path: Path, capsys) -> None:
    exit_code = main(["--root", str(tmp_path), "--summary"])

    assert exit_code == 0
    summary = capsys.readouterr().out
    assert "Agent status:" in summary
    assert "Diff check:" in summary
    assert "Drift report:" in summary


def test_summary_output_includes_human_questions_for_pause(tmp_path: Path, capsys, monkeypatch) -> None:
    def fake_run(*, root, owner_scope, database_url, governance_rules, archived_change_limit):
        return aggregate_governance_guardrail(
            diff_check=_diff_check(
                status="blocked",
                findings=[
                    {
                        "id": "missing-openspec-context",
                        "severity": "blocker",
                        "detail": "Behavior changed without an active OpenSpec change.",
                    }
                ],
            ),
            drift_report=_drift_report(),
        )

    monkeypatch.setattr("app.governance.agent_guardrail.run_agent_governance_guardrail", fake_run)

    exit_code = main(["--root", str(tmp_path), "--summary"])

    assert exit_code == 0
    summary = capsys.readouterr().out
    assert "Human questions:" in summary
    assert "Should this behavior change get OpenSpec context" in summary


def test_default_cli_json_remains_success_for_advisory_pause(tmp_path: Path, capsys, monkeypatch) -> None:
    def fake_run(*, root, owner_scope, database_url, governance_rules, archived_change_limit):
        return aggregate_governance_guardrail(
            diff_check=_diff_check(status="blocked"),
            drift_report=_drift_report(),
        )

    monkeypatch.setattr("app.governance.agent_guardrail.run_agent_governance_guardrail", fake_run)

    exit_code = main(["--root", str(tmp_path)])

    assert exit_code == 0
    body = json.loads(capsys.readouterr().out)
    assert body["agent_status"] == "pause"
    assert body["context"]["advisory_only"] is True
    assert "enforcement_preview" not in body


def test_enforcement_preview_maps_continue_caution_and_pause() -> None:
    continue_result = aggregate_governance_guardrail(diff_check=_diff_check(), drift_report=_drift_report())
    caution_result = aggregate_governance_guardrail(
        diff_check=_diff_check(
            status="warning",
            findings=[
                {
                    "id": "ambiguous-roadmap-alignment",
                    "severity": "warning",
                    "detail": "Roadmap alignment needs review.",
                }
            ],
        ),
        drift_report=_drift_report(status="watch"),
    )
    pause_result = aggregate_governance_guardrail(
        diff_check=_diff_check(status="blocked"),
        drift_report=_drift_report(status="review_required"),
    )

    continue_preview = build_enforcement_preview(continue_result, mode="local-strict")
    caution_preview = build_enforcement_preview(caution_result, mode="local-strict")
    pause_preview = build_enforcement_preview(pause_result, mode="local-strict")

    assert continue_preview.would_block is False
    assert continue_preview.severity == "pass"
    assert caution_preview.would_block is False
    assert caution_preview.severity == "warning"
    assert any("Roadmap alignment" in reason for reason in caution_preview.warning_reasons)
    assert pause_preview.would_block is True
    assert pause_preview.severity == "blocker"
    assert pause_preview.override_required is True
    assert "human-authored override" in pause_preview.override_prompt
    assert pause_preview.source_evidence["diff_status"] == "blocked"
    assert pause_preview.source_evidence["drift_status"] == "review_required"


def test_strict_exit_fails_only_when_preview_would_block(tmp_path: Path, capsys, monkeypatch) -> None:
    def fake_caution(*, root, owner_scope, database_url, governance_rules, archived_change_limit):
        return aggregate_governance_guardrail(
            diff_check=_diff_check(status="warning"),
            drift_report=_drift_report(status="watch"),
        )

    monkeypatch.setattr("app.governance.agent_guardrail.run_agent_governance_guardrail", fake_caution)

    caution_exit = main(
        ["--root", str(tmp_path), "--enforcement-preview", "local-strict", "--strict-exit"]
    )
    capsys.readouterr()

    def fake_pause(*, root, owner_scope, database_url, governance_rules, archived_change_limit):
        return aggregate_governance_guardrail(
            diff_check=_diff_check(status="blocked"),
            drift_report=_drift_report(),
        )

    monkeypatch.setattr("app.governance.agent_guardrail.run_agent_governance_guardrail", fake_pause)

    pause_exit = main(
        ["--root", str(tmp_path), "--enforcement-preview", "local-strict", "--strict-exit"]
    )

    assert caution_exit == 0
    assert pause_exit == 1


def test_pr_annotation_preview_is_local_report_with_source_evidence(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    def fake_run(*, root, owner_scope, database_url, governance_rules, archived_change_limit):
        return aggregate_governance_guardrail(
            diff_check=_diff_check(
                status="blocked",
                findings=[
                    {
                        "id": "accepted-rule-7-missing-tests",
                        "severity": "blocker",
                        "title": "Accepted governance rule expects validation",
                        "detail": "Rule applies but no validation evidence was found.",
                        "source": {"kind": "governance_rule", "id": 7},
                    }
                ],
            ),
            drift_report=_drift_report(),
        )

    monkeypatch.setattr("app.governance.agent_guardrail.run_agent_governance_guardrail", fake_run)

    exit_code = main(["--root", str(tmp_path), "--enforcement-preview", "pr-annotation"])

    assert exit_code == 0
    body = json.loads(capsys.readouterr().out)
    preview = body["enforcement_preview"]
    assert preview["mode"] == "pr-annotation"
    assert preview["would_block"] is True
    assert "no GitHub API call was made" in preview["report_text"]
    assert preview["source_evidence"]["findings"][0]["source"]["kind"] == "governance_rule"


def test_release_checklist_preview_summary_is_advisory_evidence(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    def fake_run(*, root, owner_scope, database_url, governance_rules, archived_change_limit):
        return aggregate_governance_guardrail(
            diff_check=_diff_check(status="warning"),
            drift_report=_drift_report(status="watch"),
        )

    monkeypatch.setattr("app.governance.agent_guardrail.run_agent_governance_guardrail", fake_run)

    exit_code = main(
        ["--root", str(tmp_path), "--summary", "--enforcement-preview", "release-checklist"]
    )

    assert exit_code == 0
    summary = capsys.readouterr().out
    assert "Governance enforcement preview:" in summary
    assert "Would block: false" in summary
    assert "not as a default release gate" in summary


def test_protocol_status_reports_no_active_openspec_change(tmp_path: Path, monkeypatch) -> None:
    result = aggregate_governance_guardrail(diff_check=_diff_check(), drift_report=_drift_report())

    monkeypatch.setattr(
        "app.governance.agent_guardrail._openspec_context",
        lambda root: {
            "state": "none",
            "active_changes": [],
            "command": "openspec list --json",
        },
    )

    status = build_development_protocol_status(result, root=tmp_path)
    body = status.to_dict()

    assert body["advisory_only"] is True
    assert body["openspec_context"]["state"] == "none"
    assert body["openspec_context"]["active_changes"] == []
    assert body["guardrail"]["agent_status"] == "continue"
    assert body["handoff_guidance"]["active_openspec_changes"] == []


def test_protocol_status_continue_requires_validation(tmp_path: Path, monkeypatch) -> None:
    result = aggregate_governance_guardrail(
        diff_check=_diff_check(required_tests=["Run focused protocol tests."]),
        drift_report=_drift_report(),
    )

    monkeypatch.setattr(
        "app.governance.agent_guardrail._openspec_context",
        lambda root: {
            "state": "active",
            "active_changes": ["default-governance-development-protocol"],
            "command": "openspec list --json",
        },
    )

    body = build_development_protocol_status(result, root=tmp_path).to_dict()

    assert body["guardrail"]["agent_status"] == "continue"
    assert body["guardrail"]["required_tests"] == ["Run focused protocol tests."]
    assert "targeted validation" in body["handoff_guidance"]["completion_claim"]
    assert "skip_targeted_validation" in body["guardrail"]["disallowed_next_actions"]


def test_protocol_status_caution_requires_disclosure(tmp_path: Path, monkeypatch) -> None:
    result = aggregate_governance_guardrail(
        diff_check=_diff_check(
            status="warning",
            findings=[
                {
                    "id": "ambiguous-roadmap-alignment",
                    "severity": "warning",
                    "detail": "Disclose roadmap alignment evidence.",
                }
            ],
        ),
        drift_report=_drift_report(status="watch"),
    )

    monkeypatch.setattr(
        "app.governance.agent_guardrail._openspec_context",
        lambda root: {
            "state": "active",
            "active_changes": ["default-governance-development-protocol"],
            "command": "openspec list --json",
        },
    )

    body = build_development_protocol_status(result, root=tmp_path).to_dict()

    assert body["guardrail"]["agent_status"] == "caution"
    assert "claim_completion_without_disclosing_caution" in body["guardrail"]["disallowed_next_actions"]
    assert "explicitly disclosing caution evidence" in body["handoff_guidance"]["completion_claim"]
    assert any("Disclose roadmap" in action for action in body["guardrail"]["recommended_next_actions"])


def test_protocol_status_pause_preserves_human_questions_and_disallows_self_remediation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    result = aggregate_governance_guardrail(
        diff_check=_diff_check(
            status="blocked",
            findings=[
                {
                    "id": "missing-openspec-context",
                    "severity": "blocker",
                    "detail": "Behavior changed without OpenSpec context.",
                }
            ],
        ),
        drift_report=_drift_report(),
    )

    monkeypatch.setattr(
        "app.governance.agent_guardrail._openspec_context",
        lambda root: {
            "state": "active",
            "active_changes": ["default-governance-development-protocol"],
            "command": "openspec list --json",
        },
    )

    body = build_development_protocol_status(result, root=tmp_path).to_dict()

    assert body["guardrail"]["agent_status"] == "pause"
    assert body["guardrail"]["human_questions"]
    assert "silently_rewrite_code_to_clear_guardrail" in body["guardrail"]["disallowed_next_actions"]
    assert "Do not claim completion" in body["handoff_guidance"]["completion_claim"]
    assert body["handoff_guidance"]["advisory_only"] is True


def test_cli_protocol_status_outputs_machine_readable_json(tmp_path: Path, capsys, monkeypatch) -> None:
    def fake_run(*, root, owner_scope, database_url, governance_rules, archived_change_limit):
        return aggregate_governance_guardrail(diff_check=_diff_check(), drift_report=_drift_report())

    monkeypatch.setattr("app.governance.agent_guardrail.run_agent_governance_guardrail", fake_run)
    monkeypatch.setattr(
        "app.governance.agent_guardrail._openspec_context",
        lambda root: {
            "state": "none",
            "active_changes": [],
            "command": "openspec list --json",
        },
    )

    exit_code = main(["--root", str(tmp_path), "--protocol-status"])

    assert exit_code == 0
    body = json.loads(capsys.readouterr().out)
    assert body["protocol_name"] == "decisionatlas-default-governance-development-protocol"
    assert body["openspec_context"]["state"] == "none"
    assert body["guardrail"]["agent_status"] == "continue"


def test_cli_protocol_status_summary_outputs_handoff_guidance(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    def fake_run(*, root, owner_scope, database_url, governance_rules, archived_change_limit):
        return aggregate_governance_guardrail(
            diff_check=_diff_check(status="blocked"),
            drift_report=_drift_report(),
        )

    monkeypatch.setattr("app.governance.agent_guardrail.run_agent_governance_guardrail", fake_run)
    monkeypatch.setattr(
        "app.governance.agent_guardrail._openspec_context",
        lambda root: {
            "state": "none",
            "active_changes": [],
            "command": "openspec list --json",
        },
    )

    exit_code = main(["--root", str(tmp_path), "--protocol-status", "--summary"])

    assert exit_code == 0
    summary = capsys.readouterr().out
    assert "Protocol: decisionatlas-default-governance-development-protocol v1" in summary
    assert "Agent status: pause" in summary
    assert "Handoff: Do not claim completion" in summary
