"""Offline comparison with explicitly captured public GitHub source records.

A capture is auditable input, not cryptographic attestation of remote origin.
Never fetch networks, mutate reviews, or interpret "merged" as human adoption.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import re
from urllib.parse import urlsplit

from app.extractor.evidence_snapshot import _repository_identity, _source_is_in_repo

_HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _git_blob_sha(content: str) -> str:
    data = content.encode("utf-8")
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _validate_capture(entry: dict, repo: tuple[str, str]) -> None:
    if not isinstance(entry, dict) or not _source_is_in_repo(entry.get("url"), repo):
        raise ValueError("capture URL is invalid or outside the workspace repository")
    parts = urlsplit(entry["url"]).path.strip("/").split("/")
    kind = entry.get("kind")
    if kind == "github_blob":
        sha, path, blob_sha, content = (
            entry.get("commit_sha"), entry.get("path"),
            entry.get("git_blob_sha"), entry.get("content"),
        )
        if (len(parts) < 5 or parts[2] != "blob" or not isinstance(sha, str)
                or not _HEX40.fullmatch(sha) or parts[3] != sha
                or not isinstance(path, str) or not path or "/".join(parts[4:]) != path
                or not isinstance(blob_sha, str) or not _HEX40.fullmatch(blob_sha)
                or not isinstance(content, str)):
            raise ValueError("malformed fixed-commit Git blob capture")
        if _git_blob_sha(content) != blob_sha:
            raise ValueError("Git blob content differs from recorded object SHA")
    elif kind == "github_pull_request":
        number, merged, state = entry.get("number"), entry.get("merged"), entry.get("state")
        if (len(parts) != 4 or parts[2] != "pull" or type(number) is not int
                or number <= 0 or parts[3] != str(number)
                or type(merged) is not bool or state not in {"closed", "open"}
                or (merged and state != "closed")):
            raise ValueError("malformed captured GitHub pull request state")
    else:
        raise ValueError("unknown GitHub capture kind")


def evaluate_public_capture(snapshot: dict, manifest: dict) -> dict:
    """Compare Phase-A candidate records to pinned local source captures."""
    if not isinstance(snapshot, dict) or not isinstance(manifest, dict):
        raise ValueError("expected snapshot and manifest objects")
    workspace = snapshot.get("workspace")
    if snapshot.get("schema_version") != 1 or not isinstance(workspace, dict):
        raise ValueError("expected Phase-A snapshot schema_version=1")
    repo = _repository_identity(workspace.get("repo_url"))
    if repo is None or snapshot.get("scope") != "operator_approved_local_public_sqlite_snapshot":
        raise ValueError("snapshot must originate from a reviewed public GitHub workspace")
    if (manifest.get("schema_version") != 1
            or manifest.get("repository") != "/".join(repo)
            or not isinstance(manifest.get("captured_on"), str)
            or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", manifest["captured_on"])
            or not isinstance(manifest.get("sources"), list)
            or not manifest["sources"]):
        raise ValueError("missing or mismatched public GitHub capture manifest")

    source_map = {}
    for entry in manifest["sources"]:
        _validate_capture(entry, repo)
        if entry["url"] in source_map:
            raise ValueError("duplicate public GitHub capture URL")
        source_map[entry["url"]] = entry

    results = []
    rows = snapshot.get("rows")
    if not isinstance(rows, list):
        raise ValueError("Phase-A snapshot rows must be a list")
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("candidate"), dict):
            raise ValueError("invalid candidate row")
        candidate = row["candidate"]
        citations = candidate.get("citations")
        if not isinstance(citations, list):
            raise ValueError("candidate citations must be a list")
        checks = []
        for index, citation in enumerate(citations):
            if not isinstance(citation, dict):
                raise ValueError("malformed candidate citation")
            url = citation.get("url")
            if not _source_is_in_repo(url, repo):
                raise ValueError("candidate source URL is outside public workspace")
            capture = source_map.get(url)
            check = {"citation_index": index, "url": url}
            if capture is None:
                check.update(status="not_evaluated", reason="upstream_capture_missing")
            elif capture["kind"] == "github_pull_request":
                # A merge_commit_sha alone cannot establish adoption; GitHub may
                # populate this field even on closed-but-unmerged pull requests.
                if citation.get("kind") != "pull_request":
                    check.update(status="fail", reason="source_kind_mismatch")
                elif citation.get("merged") is not None and citation.get("merged") is not capture["merged"]:
                    check.update(status="fail", reason="stored_merge_state_conflicts_with_capture")
                elif capture["merged"] is False:
                    check.update(status="fail", reason="unmerged_proposal_not_adoption")
                elif capture["merged"] is True:
                    check.update(status="not_evaluated", reason="merged_still_requires_human_review")
                else:
                    check.update(status="not_evaluated", reason="pr_merge_state_unknown")
            else:
                text = capture["content"]
                quote = citation.get("quote")
                first, last = citation.get("start"), citation.get("end")
                same = citation.get("snapshot_text") == text
                if not same:
                    check.update(status="fail", reason="stored_artifact_differs_from_capture")
                elif citation.get("snapshot_sha256") != hashlib.sha256(text.encode("utf-8")).hexdigest():
                    check.update(status="fail", reason="stored_snapshot_hash_mismatch")
                elif not isinstance(quote, str) or not quote:
                    check.update(status="not_evaluated", reason="missing_exact_quote")
                elif first is None and last is None:
                    check.update(
                        status="pass" if quote in text else "fail",
                        reason="quote_in_recorded_git_blob" if quote in text else "quote_not_in_recorded_git_blob",
                    )
                else:
                    exact = type(first) is int and type(last) is int and 0 <= first < last <= len(text) and text[first:last] == quote
                    check.update(
                        status="pass" if exact else "fail",
                        reason="span_in_recorded_git_blob" if exact else "quote_or_span_mismatch",
                    )
            checks.append(check)
        results.append({
            "id": candidate.get("id"),
            "diagnostic_status": "fail" if any(c["status"] == "fail" for c in checks) else "review_required",
            "automatic_acceptance": False,
            "review_required": True,
            "checks": checks,
        })
    return {
        "schema_version": 1,
        "basis": "operator_supplied_public_capture_not_live_verification",
        "source_authenticity": "capture_not_independently_attested",
        "human_review": "not_run",
        "model_accuracy": "not_evaluated",
        "candidate_count": len(results),
        "citation_status_counts": dict(Counter(check["status"] for result in results for check in result["checks"])),
        "results": results,
    }
