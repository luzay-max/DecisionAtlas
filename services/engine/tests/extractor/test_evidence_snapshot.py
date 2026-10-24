"""Offline-only regression for the reviewed public workspace export boundary."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import Artifact, Decision, SourceRef, Workspace
from app.extractor.evidence_snapshot import export_workspace_evidence

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "scripts/eval/export_workspace_evidence.py"
TEXT = "We selected a local cache because repeated reads were too slow."
SHA = "a" * 40
PUBLIC_URL = f"https://github.com/example/project/blob/{SHA}/docs/adr.md"


def seeded_db(tmp_path: Path, *, access_type: str = "public", url: str = PUBLIC_URL) -> Path:
    db = tmp_path / "public.db"
    engine = create_engine(f"sqlite:///{db}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(Workspace(slug="public-project", name="public", repo_url="https://github.com/example/project", access_source_type=access_type))
        session.flush()
        workspace = session.scalar(select(Workspace).where(Workspace.slug == "public-project"))
        decision = Decision(
            workspace_id=workspace.id, title="Use local cache", problem="Slow repeated reads",
            chosen_option="Use a local cache", tradeoffs="Cache invalidation is harder",
            review_state="candidate", confidence=0.5,
        )
        artifact = Artifact(
            workspace_id=workspace.id, type="doc", source_id="docs/adr.md", repo="example/project",
            title="Architecture decision", content=TEXT, url=url,
        )
        session.add_all([decision, artifact])
        session.flush()
        session.add(SourceRef(
            decision_id=decision.id, artifact_id=artifact.id, span_start=0,
            span_end=len(TEXT), quote=TEXT, url=url,
        ))
        session.commit()
    engine.dispose()
    return db


def export_from_db(path: Path, **kwargs) -> dict:
    engine = create_engine(f"sqlite:///{path}")
    try:
        with Session(engine) as session:
            return export_workspace_evidence(session, workspace_slug="public-project", **kwargs)
    finally:
        engine.dispose()


def test_read_only_export_preserves_original_quote_and_does_not_invent_adoption(tmp_path):
    path = seeded_db(tmp_path)
    a = export_from_db(path, public_data_approved=True)
    b = export_from_db(path, public_data_approved=True)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert a["candidate_count"] == 1
    assert a["citation_count"] == 1
    assert a["source_authenticity"] == "remote_not_verified"
    assert a["model_accuracy"] == "not_evaluated"
    assert a["human_review"] == "not_run"
    row = a["rows"][0]
    assert row["stored_review_state"] == "candidate"
    assert row["candidate"]["provider_kind"] == "unknown"
    assert row["diagnostics"]["automatic_acceptance"] is False
    assert row["diagnostics"]["review_required"] is True
    citation = row["candidate"]["citations"][0]
    assert citation["snapshot_text"] == TEXT
    assert citation["quote"] == TEXT
    assert citation["start"] == 0 and citation["end"] == len(TEXT)
    assert citation["snapshot_sha256"] == hashlib.sha256(TEXT.encode()).hexdigest()
    assert citation["revision"] == SHA
    assert citation["merged"] is None  # No trustworthy merge flag stored on the artifact.
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(Decision)) == 1
        assert session.scalar(select(Decision.review_state)) == "candidate"
    engine.dispose()


def test_operator_declares_fake_but_cannot_claim_unverified_live(tmp_path):
    path = seeded_db(tmp_path)
    assert export_from_db(path, public_data_approved=True, provider_kind="fake")["rows"][0]["candidate"]["provider_kind"] == "fake"
    with pytest.raises(ValueError, match="only unknown"):
        export_from_db(path, public_data_approved=True, provider_kind="live")
    with pytest.raises(ValueError, match="approval"):
        export_from_db(path)


@pytest.mark.parametrize("access_type", ["github_app_installation", "github_token", "private"])
def test_bound_or_private_workspace_is_refused(tmp_path, access_type):
    path = seeded_db(tmp_path, access_type=access_type)
    with pytest.raises(ValueError, match="private or bound"):
        export_from_db(path, public_data_approved=True)


@pytest.mark.parametrize("url", [
    "https://github.com/other/project/pull/1",
    "https://github.com/example/project/pull/1?token=private",
    "https://user:secret@github.com/example/project/pull/1",
    "https://github.com:wrong/example/project/pull/1",
    "https://github.com:/example/project/pull/1",
    "http://github.com/example/project/pull/1",
])
def test_untrusted_source_url_never_exports_stored_content(tmp_path, url):
    path = seeded_db(tmp_path, url=url)
    # The Artifact URL can be rejected before the matching SourceRef URL.
    with pytest.raises(ValueError, match="URL"):
        export_from_db(path, public_data_approved=True)


def test_cross_workspace_reference_fails_closed(tmp_path):
    path = seeded_db(tmp_path)
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        other = Workspace(slug="private-other", name="other", repo_url="https://github.com/other/private", access_source_type="private")
        session.add(other)
        session.flush()
        artifact = session.scalar(select(Artifact))
        artifact.workspace_id = other.id
        session.commit()
    engine.dispose()
    with pytest.raises(ValueError, match="cross-workspace"):
        export_from_db(path, public_data_approved=True)


def test_workspace_not_found_is_not_fallback_to_another_scope(tmp_path):
    path = seeded_db(tmp_path)
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        with pytest.raises(ValueError, match="not found"):
            export_workspace_evidence(session, workspace_slug="typo", public_data_approved=True)
    engine.dispose()



def test_public_mode_with_stale_private_source_binding_is_refused(tmp_path):
    path = seeded_db(tmp_path)
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        workspace = session.scalar(select(Workspace))
        workspace.access_source_ref = "previous-private-credential"
        session.commit()
    engine.dispose()
    with pytest.raises(ValueError, match="private or bound"):
        export_from_db(path, public_data_approved=True)


def test_workspace_repo_identity_mismatch_is_refused(tmp_path):
    path = seeded_db(tmp_path)
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        workspace = session.scalar(select(Workspace))
        workspace.repo_identity = "other/secret"
        session.commit()
    engine.dispose()
    with pytest.raises(ValueError, match="repository identity"):
        export_from_db(path, public_data_approved=True)


def test_artifact_repo_mismatch_is_refused(tmp_path):
    path = seeded_db(tmp_path)
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        artifact = session.scalar(select(Artifact))
        artifact.repo = "other/secret"
        session.commit()
    engine.dispose()
    with pytest.raises(ValueError, match="artifact repository"):
        export_from_db(path, public_data_approved=True)


def test_artifact_url_cannot_be_masked_by_valid_source_reference(tmp_path):
    path = seeded_db(tmp_path)
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        artifact = session.scalar(select(Artifact))
        artifact.url = "https://github.com/private-org/secret/blob/main/README.md"
        session.commit()
    engine.dispose()
    with pytest.raises(ValueError, match="artifact URL"):
        export_from_db(path, public_data_approved=True)


def test_source_url_cannot_disagree_with_artifact_url(tmp_path):
    path = seeded_db(tmp_path)
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        ref = session.scalar(select(SourceRef))
        ref.url = "https://github.com/example/project/blob/main/other.md"
        session.commit()
    engine.dispose()
    with pytest.raises(ValueError, match="disagree"):
        export_from_db(path, public_data_approved=True)


@pytest.mark.parametrize("url", [
    " https://github.com/example/project/blob/main/adr.md",
    "https://github.com/example/project/blob/main/adr.md\n",
    "https://github.com/example/project/blob/../private",
])
def test_controls_and_dot_segments_not_exported(tmp_path, url):
    path = seeded_db(tmp_path, url=url)
    with pytest.raises(ValueError, match="URL"):
        export_from_db(path, public_data_approved=True)


def test_cli_requires_public_approval_refuses_checkout_and_never_overwrites(tmp_path):
    path = seeded_db(tmp_path)
    output = tmp_path / "snapshot.json"
    basic = [sys.executable, str(SCRIPT), "--sqlite", str(path), "--workspace", "public-project", "--output", str(output)]
    assert subprocess.run(basic, capture_output=True).returncode != 0
    assert not output.exists()
    assert subprocess.run(basic + ["--approve-public-data"], capture_output=True).returncode == 0
    first = output.read_bytes()
    assert json.loads(first)["candidate_count"] == 1
    assert subprocess.run(basic + ["--approve-public-data"], capture_output=True).returncode != 0
    assert output.read_bytes() == first
    internal = ROOT / "artifacts" / "should-not-write-sensitive-data.json"
    assert subprocess.run(basic[:-1] + [str(internal), "--approve-public-data"], capture_output=True).returncode != 0
    assert not internal.exists()


def test_cli_does_not_create_missing_sqlite(tmp_path):
    absent = tmp_path / "absent.db"
    cmd = [sys.executable, str(SCRIPT), "--sqlite", str(absent), "--workspace", "public-project", "--output", str(tmp_path / "out.json"), "--approve-public-data"]
    assert subprocess.run(cmd, capture_output=True).returncode != 0
    assert not absent.exists()
