from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from app.db.session import get_db_session
from app.governance.markdown_ingest import extract_rule_drafts, import_governance_markdown, review_rule_draft
from app.main import create_app


def _migrate(tmp_path: Path, monkeypatch, name: str) -> None:
    db_path = tmp_path / name
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")


def test_extract_rule_drafts_reads_markdown_markers() -> None:
    drafts = extract_rule_drafts(
        """
## Every OpenSpec change must have tasks

Severity: blocker
Scope: all
Rationale: Prevent scope creep.

All implementation changes must keep a tracked tasks.md checklist.
"""
    )

    assert len(drafts) == 1
    assert drafts[0].title == "Every OpenSpec change must have tasks"
    assert drafts[0].severity == "blocker"
    assert drafts[0].scope == "all"
    assert drafts[0].rationale == "Prevent scope creep."
    assert drafts[0].rule_type == "standard"
    assert drafts[0].extraction_reason == "bounded severity or scope marker"
    assert "tasks.md" in drafts[0].description


def test_extract_rule_drafts_uses_document_type_signals_and_avoids_plain_prose() -> None:
    standard = extract_rule_drafts(
        """
## Rule: Every change has tests

Every backend behavior change must include a targeted pytest.
""",
        document_type="standard",
    )
    postmortem = extract_rule_drafts(
        """
## Lesson: Playwright smoke must own its server

The smoke flow must start or reuse the expected API/web stack.
""",
        document_type="postmortem",
    )
    decision = extract_rule_drafts(
        """
## Decision: Guardrail pause requires human confirmation

Agents must not silently rewrite governance docs to clear a pause.
""",
        document_type="decision_record",
    )
    anti_pattern = extract_rule_drafts(
        """
## Anti-pattern: Hidden validation skips

Do not claim validation passed when the command was not run.
""",
        document_type="anti_pattern",
    )
    ordinary = extract_rule_drafts(
        """
## Background

This section should help future readers understand context, but it is not a rule.
""",
        document_type="standard",
    )

    assert standard[0].rule_type == "standard"
    assert standard[0].extraction_reason == "rule heading marker"
    assert postmortem[0].rule_type == "postmortem_lesson"
    assert postmortem[0].extraction_reason == "postmortem lesson marker"
    assert decision[0].rule_type == "decision_rule"
    assert decision[0].extraction_reason == "decision outcome marker"
    assert anti_pattern[0].rule_type == "anti_pattern"
    assert anti_pattern[0].extraction_reason == "anti-pattern prohibition marker"
    assert ordinary == []


def test_post_governance_document_imports_markdown_and_creates_pending_drafts(tmp_path: Path, monkeypatch) -> None:
    _migrate(tmp_path, monkeypatch, "governance-import.db")

    client = TestClient(create_app())
    response = client.post(
        "/governance/documents",
        json={
            "title": "Development Standards",
            "document_type": "coding_guideline",
            "scope": "all",
            "source_path": "docs/standards/development.md",
            "content": """
## Rule: Every change has tests

Severity: warning
Scope: engine
Rationale: Regressions should be caught before archive.

Every backend behavior change should include a targeted pytest.
""",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["document"]["title"] == "Development Standards"
    assert body["document"]["document_type"] == "coding_guideline"
    assert body["document"]["source_path"] == "docs/standards/development.md"
    assert body["drafts"][0]["review_state"] == "pending"
    assert body["drafts"][0]["severity"] == "warning"
    assert body["drafts"][0]["scope"] == "engine"
    assert body["drafts"][0]["source_title"] == "Development Standards"
    assert body["drafts"][0]["rule_type"] == "standard"
    assert body["drafts"][0]["extraction_reason"] == "rule heading marker"
    assert body["drafts"][0]["lifecycle_status"] == "current"


def test_governance_document_rejects_unsupported_type(tmp_path: Path, monkeypatch) -> None:
    _migrate(tmp_path, monkeypatch, "governance-invalid-type.db")

    client = TestClient(create_app())
    response = client.post(
        "/governance/documents",
        json={
            "title": "Random Notes",
            "document_type": "notes",
            "content": "## Rule: Keep scope small\n\nMust stay focused.",
        },
    )

    assert response.status_code == 400
    assert "Unsupported document_type" in response.json()["detail"]


def test_governance_document_without_rules_creates_no_accepted_rules(tmp_path: Path, monkeypatch) -> None:
    _migrate(tmp_path, monkeypatch, "governance-empty-rules.db")

    client = TestClient(create_app())
    create_response = client.post(
        "/governance/documents",
        json={
            "title": "Roadmap Notes",
            "document_type": "roadmap",
            "content": "# Roadmap\n\nThis is contextual prose without a rule marker.",
        },
    )
    assert create_response.status_code == 200
    assert create_response.json()["drafts"] == []

    rules_response = client.get("/governance/rules", params={"review_state": "accepted"})
    assert rules_response.status_code == 200
    assert rules_response.json()["rules"] == []


def test_governance_rule_review_accepts_and_rejects_with_source_trace(tmp_path: Path, monkeypatch) -> None:
    _migrate(tmp_path, monkeypatch, "governance-review.db")

    client = TestClient(create_app())
    create_response = client.post(
        "/governance/documents",
        json={
            "title": "Postmortem Lessons",
            "document_type": "postmortem",
            "content": """
## Rule: Playwright smoke must own its server

Severity: blocker
Scope: frontend
Rationale: CI previously failed with ECONNREFUSED.

The smoke flow must start or reuse the expected API/web stack.

## Rule: Keep notes visible

Severity: note
Scope: docs

Document known limitations.
""",
        },
    )
    assert create_response.status_code == 200
    drafts = create_response.json()["drafts"]

    accept_response = client.post(
        f"/governance/rules/{drafts[0]['id']}/review",
        json={"review_state": "accepted", "review_rationale": "Critical smoke stability rule."},
    )
    reject_response = client.post(
        f"/governance/rules/{drafts[1]['id']}/review",
        json={"review_state": "rejected", "review_rationale": "Too broad for an authoritative rule."},
    )

    assert accept_response.status_code == 200
    accepted_body = accept_response.json()
    assert accepted_body["rule"]["review_state"] == "accepted"
    assert accepted_body["rule"]["status"] == "active"
    assert accepted_body["rule"]["source_title"] == "Postmortem Lessons"
    assert "ECONNREFUSED" in accepted_body["rule"]["source_excerpt"]
    assert accepted_body["rule"]["review_rationale"] == "Critical smoke stability rule."
    assert accepted_body["rule"]["reviewed_by"] == "local-admin"
    assert accepted_body["rule"]["rule_type"] == "postmortem_lesson"
    assert accepted_body["rule"]["lifecycle_status"] == "current"
    assert accepted_body["audit_event"]["target_type"] == "governance_rule"
    assert accepted_body["audit_event"]["action"] == "governance_rule_review_accepted"
    assert accepted_body["audit_event"]["previous_state"]["review_state"] == "pending"
    assert accepted_body["audit_event"]["new_state"]["review_state"] == "accepted"
    assert accepted_body["audit_event"]["rationale"] == "Critical smoke stability rule."
    assert accepted_body["rule"]["audit_history"][0]["action"] == "governance_rule_review_accepted"
    assert reject_response.status_code == 200
    assert reject_response.json()["rule"]["status"] == "rejected"
    assert reject_response.json()["rule"]["review_rationale"] == "Too broad for an authoritative rule."

    accepted_response = client.get("/governance/rules", params={"review_state": "accepted"})
    assert accepted_response.status_code == 200
    accepted_rules = accepted_response.json()["rules"]
    assert len(accepted_rules) == 1
    assert accepted_rules[0]["title"] == "Rule: Playwright smoke must own its server"
    assert accepted_rules[0]["review_rationale"] == "Critical smoke stability rule."


def test_governance_rule_lifecycle_marks_stale_without_changing_review_state(tmp_path: Path, monkeypatch) -> None:
    _migrate(tmp_path, monkeypatch, "governance-lifecycle-stale.db")

    client = TestClient(create_app())
    create_response = client.post(
        "/governance/documents",
        json={
            "title": "Release Standards",
            "document_type": "release_policy",
            "content": """
## Rule: Release checklist is manual

Severity: warning
Scope: release

Release checklist review must be manual.
""",
        },
    )
    assert create_response.status_code == 200
    rule_id = create_response.json()["drafts"][0]["id"]
    accept_response = client.post(
        f"/governance/rules/{rule_id}/review",
        json={"review_state": "accepted", "review_rationale": "Accepted as release baseline."},
    )
    assert accept_response.status_code == 200

    lifecycle_response = client.post(
        f"/governance/rules/{rule_id}/lifecycle",
        json={"lifecycle_status": "stale", "lifecycle_rationale": "Release checklist moved to protocol status."},
    )

    assert lifecycle_response.status_code == 200
    lifecycle_body = lifecycle_response.json()
    rule = lifecycle_body["rule"]
    assert rule["review_state"] == "accepted"
    assert rule["status"] == "active"
    assert rule["review_rationale"] == "Accepted as release baseline."
    assert rule["lifecycle_status"] == "stale"
    assert rule["lifecycle_rationale"] == "Release checklist moved to protocol status."
    assert rule["superseded_by_rule_id"] is None
    assert lifecycle_body["audit_event"]["target_type"] == "governance_rule"
    assert lifecycle_body["audit_event"]["action"] == "governance_rule_lifecycle_stale"
    assert lifecycle_body["audit_event"]["previous_state"]["lifecycle_status"] == "current"
    assert lifecycle_body["audit_event"]["new_state"]["lifecycle_status"] == "stale"
    assert lifecycle_body["audit_event"]["rationale"] == "Release checklist moved to protocol status."


def test_governance_rule_lifecycle_supersedes_with_current_accepted_target(tmp_path: Path, monkeypatch) -> None:
    _migrate(tmp_path, monkeypatch, "governance-lifecycle-superseded.db")

    client = TestClient(create_app())
    create_response = client.post(
        "/governance/documents",
        json={
            "title": "Validation Standards",
            "document_type": "coding_guideline",
            "content": """
## Rule: Old validation wording

Severity: warning
Scope: engine

Engine changes should mention validation.

## Rule: Targeted validation evidence

Severity: blocker
Scope: engine

Engine changes must include targeted validation evidence.
""",
        },
    )
    assert create_response.status_code == 200
    old_rule_id = create_response.json()["drafts"][0]["id"]
    replacement_rule_id = create_response.json()["drafts"][1]["id"]
    for rule_id in (old_rule_id, replacement_rule_id):
        response = client.post(
            f"/governance/rules/{rule_id}/review",
            json={"review_state": "accepted", "review_rationale": "Accepted."},
        )
        assert response.status_code == 200

    lifecycle_response = client.post(
        f"/governance/rules/{old_rule_id}/lifecycle",
        json={
            "lifecycle_status": "superseded",
            "lifecycle_rationale": "Replacement is stricter and current.",
            "superseded_by_rule_id": replacement_rule_id,
        },
    )

    assert lifecycle_response.status_code == 200
    rule = lifecycle_response.json()["rule"]
    assert rule["review_state"] == "accepted"
    assert rule["lifecycle_status"] == "superseded"
    assert rule["superseded_by_rule_id"] == replacement_rule_id
    assert rule["lifecycle_rationale"] == "Replacement is stricter and current."


def test_governance_rule_lifecycle_rejects_invalid_targets_and_scope(tmp_path: Path, monkeypatch) -> None:
    _migrate(tmp_path, monkeypatch, "governance-lifecycle-invalid.db")

    client = TestClient(create_app())
    create_response = client.post(
        "/governance/documents",
        json={
            "title": "Engine Standards",
            "document_type": "coding_guideline",
            "content": """
## Rule: Current engine rule

Severity: warning
Scope: engine

Engine changes should include validation.

## Rule: Pending engine rule

Severity: warning
Scope: engine

Pending guidance is not accepted yet.
""",
        },
    )
    assert create_response.status_code == 200
    current_rule_id = create_response.json()["drafts"][0]["id"]
    pending_rule_id = create_response.json()["drafts"][1]["id"]
    assert client.post(
        f"/governance/rules/{current_rule_id}/review",
        json={"review_state": "accepted", "review_rationale": "Accepted."},
    ).status_code == 200

    self_response = client.post(
        f"/governance/rules/{current_rule_id}/lifecycle",
        json={"lifecycle_status": "superseded", "superseded_by_rule_id": current_rule_id},
    )
    pending_response = client.post(
        f"/governance/rules/{current_rule_id}/lifecycle",
        json={"lifecycle_status": "superseded", "superseded_by_rule_id": pending_rule_id},
    )
    missing_response = client.post(
        f"/governance/rules/{current_rule_id}/lifecycle",
        json={"lifecycle_status": "superseded", "superseded_by_rule_id": 99999},
    )

    session = get_db_session()
    try:
        other_document, other_drafts = import_governance_markdown(
            session=session,
            owner_scope="other-team",
            title="Other Standards",
            document_type="coding_guideline",
            content="## Rule: Other owner rule\n\nSeverity: warning\nScope: engine\n\nOther owner validation rule.",
        )
        session.commit()
        other_rule = review_rule_draft(
            session=session,
            owner_scope="other-team",
            draft_id=other_drafts[0].id,
            review_state="accepted",
            reviewer="other-admin",
        )
        session.commit()
        other_rule_id = other_rule.id
        assert other_document.owner_scope == "other-team"
    finally:
        session.close()

    cross_owner_response = client.post(
        f"/governance/rules/{current_rule_id}/lifecycle",
        json={"lifecycle_status": "superseded", "superseded_by_rule_id": other_rule_id},
    )

    assert self_response.status_code == 400
    assert "cannot supersede themselves" in self_response.json()["detail"]
    assert pending_response.status_code == 400
    assert "accepted active" in pending_response.json()["detail"]
    assert missing_response.status_code == 404
    assert cross_owner_response.status_code == 404
