"""Export stored decision evidence for *offline review*, without trusting it.

Public-workspace only; never fetch URLs, infer a model provider, or update reviews.
"""
from __future__ import annotations

import hashlib
import re
from urllib.parse import urlsplit

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Artifact, Decision, SourceRef, Workspace
from app.extractor.evidence import evaluate_evidence


def _repository_identity(url: str | None) -> tuple[str, str] | None:
    if not isinstance(url, str):
        return None
    try:
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or parsed.hostname != "github.com" or
                parsed.username or parsed.password or parsed.port not in (None, 443) or
                parsed.query or parsed.fragment or parsed.netloc.endswith(":")):
            return None
    except ValueError:
        return None
    parts = parsed.path.strip("/").split("/")
    if len(parts) != 2 or not all(parts):
        return None
    owner, repository = parts
    if repository.endswith(".git"):
        repository = repository[:-4]
    if not repository or not re.fullmatch(r"[A-Za-z0-9_.-]+", owner) or not re.fullmatch(r"[A-Za-z0-9_.-]+", repository):
        return None
    return owner.casefold(), repository.casefold()


def _source_is_in_repo(url: str | None, identity: tuple[str, str]) -> bool:
    if not isinstance(url, str):
        return False
    try:
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or parsed.hostname != "github.com" or
                parsed.username or parsed.password or parsed.port not in (None, 443) or
                parsed.query or parsed.fragment or parsed.netloc.endswith(":")):
            return False
    except ValueError:
        return False
    parts = parsed.path.strip("/").split("/")
    return len(parts) >= 3 and (parts[0].casefold(), parts[1].casefold()) == identity


def export_workspace_evidence(
    session: Session,
    *,
    workspace_slug: str,
    provider_kind: str = "unknown",
    public_data_approved: bool = False,
) -> dict:
    """Deterministic snapshot of stored bytes; not a remote provenance attestation.

    Caller must separately authorize use of this *local* database and publication of
    the chosen workspace's content. This API is not an HTTP authorization boundary.
    """
    if not public_data_approved:
        raise ValueError("explicit public-data approval is required")
    if provider_kind not in {"unknown", "fake"}:
        raise ValueError("only unknown or explicitly declared fake provider allowed")
    workspace = session.scalar(select(Workspace).where(Workspace.slug == workspace_slug))
    if workspace is None:
        raise ValueError("workspace not found")
    if workspace.access_source_type != "public":
        raise ValueError("private or bound-access workspace export is prohibited")
    repo = _repository_identity(workspace.repo_url)
    if repo is None:
        raise ValueError("workspace must be linked to a canonical public GitHub repository URL")

    rows = []
    decisions = session.scalars(
        select(Decision).where(Decision.workspace_id == workspace.id).order_by(Decision.id)
    ).all()
    for decision in decisions:
        citations = []
        for ref in session.scalars(select(SourceRef).where(SourceRef.decision_id == decision.id).order_by(SourceRef.id)):
            artifact = session.get(Artifact, ref.artifact_id)
            if artifact is None or artifact.workspace_id != workspace.id:
                raise ValueError("source reference has a missing or cross-workspace artifact")
            url = ref.url or artifact.url
            if not _source_is_in_repo(url, repo):
                raise ValueError("source URL is missing, outside the repository, or includes a query string")
            snapshot_text = artifact.content
            citation = {
                "source_ref_id": ref.id,
                "artifact_id": artifact.id,
                "artifact_type": artifact.type,
                "source_id": artifact.source_id,
                "url": url,
                "kind": "pull_request" if artifact.type in {"pr", "pull_request"} else artifact.type,
                "quote": ref.quote,
                "start": ref.span_start,
                "end": ref.span_end,
                "snapshot_text": snapshot_text,
                "snapshot_sha256": hashlib.sha256(snapshot_text.encode("utf-8")).hexdigest(),
                # The import record does not reliably contain merge status.
                "merged": None,
            }
            # An immutable-looking URL can only indicate syntax. This does not
            # assert that the stored body was fetched from that remote revision.
            match = re.search(r"/blob/([0-9a-f]{40})/", urlsplit(url).path)
            if match:
                citation["revision"] = match.group(1)
            citations.append(citation)
        candidate = {
            "id": str(decision.id),
            "provider_kind": provider_kind,
            "title": decision.title,
            "problem": decision.problem,
            "chosen_option": decision.chosen_option,
            "tradeoffs": decision.tradeoffs,
            "citations": citations,
        }
        rows.append({
            "candidate": candidate,
            "stored_review_state": decision.review_state,
            "diagnostics": evaluate_evidence(candidate),
        })
    return {
        "schema_version": 1,
        "scope": "operator_approved_local_public_sqlite_snapshot",
        "source_authenticity": "remote_not_verified",
        "provider_provenance": "operator_declared_not_recorded_in_decision",
        "human_review": "not_run",
        "model_accuracy": "not_evaluated",
        "workspace": {"slug": workspace.slug, "repo_url": workspace.repo_url},
        "candidate_count": len(rows),
        "citation_count": sum(len(row["candidate"]["citations"]) for row in rows),
        "rows": rows,
    }
