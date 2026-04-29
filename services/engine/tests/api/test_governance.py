from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from app.governance.markdown_ingest import extract_rule_drafts
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
    assert "tasks.md" in drafts[0].description


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

    accept_response = client.post(f"/governance/rules/{drafts[0]['id']}/review", json={"review_state": "accepted"})
    reject_response = client.post(f"/governance/rules/{drafts[1]['id']}/review", json={"review_state": "rejected"})

    assert accept_response.status_code == 200
    assert accept_response.json()["rule"]["review_state"] == "accepted"
    assert accept_response.json()["rule"]["status"] == "active"
    assert accept_response.json()["rule"]["source_title"] == "Postmortem Lessons"
    assert "ECONNREFUSED" in accept_response.json()["rule"]["source_excerpt"]
    assert reject_response.status_code == 200
    assert reject_response.json()["rule"]["status"] == "rejected"

    accepted_response = client.get("/governance/rules", params={"review_state": "accepted"})
    assert accepted_response.status_code == 200
    accepted_rules = accepted_response.json()["rules"]
    assert len(accepted_rules) == 1
    assert accepted_rules[0]["title"] == "Rule: Playwright smoke must own its server"
