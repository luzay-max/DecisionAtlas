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
    if not isinstance(url, str) or any(ord(char) <= 32 or ord(char) == 127 for char in url):
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
    if not isinstance(url, str) or any(ord(char) <= 32 or ord(char) == 127 for char in url):
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
    return (
        len(parts) >= 3
        and not any(part in {"", ".", ".."} for part in parts)
        and (parts[0].casefold(), parts[1].casefold()) == identity
    )


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
    if workspace.access_source_type != "public" or workspace.access_source_ref is not None:
        raise ValueError("private or bound-access workspace export is prohibited")
    repo = _repository_identity(workspace.repo_url)
    if repo is None:
        raise ValueError("workspace must be linked to a canonical public GitHub repository URL")
    if workspace.repo_identity is not None and workspace.repo_identity.casefold() != "/".join(repo):
        raise ValueError("workspace repository identity conflicts with public GitHub URL")

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
            if not isinstance(artifact.repo, str) or artifact.repo.casefold() != "/".join(repo):
                raise ValueError("artifact repository identity conflicts with public workspace")
            if artifact.url is not None and not _source_is_in_repo(artifact.url, repo):
                raise ValueError("artifact URL conflicts with public workspace")
            if ref.url is not None and not _source_is_in_repo(ref.url, repo):
                raise ValueError("source URL is missing, outside the repository, or includes a query string")
            if ref.url is not None and artifact.url is not None and ref.url != artifact.url:
                raise ValueError("source and artifact URL disagree")
            url = ref.url or artifact.url
            if not _source_is_in_repo(url, repo):
                raise ValueError("source URL is missing, outside the repository, or includes a query string")
            snapshot_text = artifact.content
            metadata = artifact.metadata_json if isinstance(artifact.metadata_json, dict) else {}
            capture = metadata.get("decisionatlas_capture")
            if not isinstance(capture, dict):
                capture = {}
            import_digest = capture.get("content_sha256")
            if isinstance(import_digest, str):
                import_capture_status = (
                    "pass"
                    if hashlib.sha256(snapshot_text.encode("utf-8")).hexdigest() == import_digest
                    else "fail"
                )
            else:
                import_capture_status = "not_evaluated"
            merge_state_observed = (
                metadata.get("source_metadata_origin") == "github_api"
                and metadata.get("merge_state_observed") == "github_api"
                and type(metadata.get("merged")) is bool
            )
            upstream_metadata = {
                "origin": metadata.get("source_metadata_origin")
                if isinstance(metadata.get("source_metadata_origin"), str) else "not_recorded",
                "number": metadata.get("number") if type(metadata.get("number")) is int else None,
                "state": metadata.get("state") if isinstance(metadata.get("state"), str) else None,
                "updated_at": metadata.get("updated_at") if isinstance(metadata.get("updated_at"), str) else None,
                "closed_at": metadata.get("closed_at") if isinstance(metadata.get("closed_at"), str) else None,
                "merged_at": metadata.get("merged_at") if isinstance(metadata.get("merged_at"), str) else None,
                "merge_state_observed": "github_api" if merge_state_observed else "unknown",
                "merge_commit_sha": metadata.get("merge_commit_sha") if isinstance(metadata.get("merge_commit_sha"), str) else None,
                "head_sha": metadata.get("head_sha") if isinstance(metadata.get("head_sha"), str) else None,
                "base_ref": metadata.get("base_ref") if isinstance(metadata.get("base_ref"), str) else None,
            }
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
                "import_snapshot_sha256": import_digest if isinstance(import_digest, str) else None,
                "import_capture_status": import_capture_status,
                "import_captured_at": capture.get("captured_at") if isinstance(capture.get("captured_at"), str) else None,
                "import_capture_method": capture.get("method") if isinstance(capture.get("method"), str) else None,
                "upstream_metadata": upstream_metadata,
                # Old imports and partial API payloads remain explicitly unknown.
                "merged": metadata.get("merged") if merge_state_observed else None,
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
