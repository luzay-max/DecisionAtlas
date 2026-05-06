from __future__ import annotations

import json
from pathlib import Path

from app.governance.agent_guardrail import aggregate_governance_guardrail, main


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
    body = result.to_dict()
    assert body["source_results"]["diff_check"]["status"] == "pass"
    assert body["source_results"]["drift_report"]["status"] == "clean"


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
    assert any("Sync the decision" in action for action in result.recommended_next_actions)


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
        ]
    ).issubset(body)
    assert body["context"]["advisory_only"] is True
