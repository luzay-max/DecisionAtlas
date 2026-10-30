from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
import hashlib
import re
from pathlib import PurePosixPath
from typing import Callable
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from itertools import islice

from sqlalchemy.orm import Session

from app.ingest.github_client import GitHubClient, GitHubIncompleteCoverageError
from app.ingest.github_document_selection import classify_repository_document, select_high_signal_repository_documents
from app.ingest.github_types import GitHubImportResult
from app.repositories.artifacts import ArtifactRepository
from app.repositories.workspaces import WorkspaceRepository


# Fail closed rather than silently omitting expensive source documents. These
# caps bound accepted prefetch content, not HTTP response allocation while a
# single remote response is being downloaded or all GitHub API payloads.
MAX_SELECTED_MARKDOWN_DOCUMENTS = 256
MAX_SINGLE_MARKDOWN_BYTES = 4 * 1024 * 1024
MAX_TOTAL_MARKDOWN_BYTES = 32 * 1024 * 1024


class GitHubImporter:
    def __init__(
        self,
        session: Session,
        client: GitHubClient,
        *,
        max_selected_documents: int = MAX_SELECTED_MARKDOWN_DOCUMENTS,
        max_single_document_bytes: int = MAX_SINGLE_MARKDOWN_BYTES,
        max_total_document_bytes: int = MAX_TOTAL_MARKDOWN_BYTES,
    ) -> None:
        if min(max_selected_documents, max_single_document_bytes, max_total_document_bytes) < 1:
            raise ValueError("GitHub document prefetch limits must be positive")
        self.session = session
        self.client = client
        self.max_selected_documents = max_selected_documents
        self.max_single_document_bytes = max_single_document_bytes
        self.max_total_document_bytes = max_total_document_bytes
        self.artifacts = ArtifactRepository(session)
        self.workspaces = WorkspaceRepository(session)

    def import_repo(
        self,
        *,
        workspace_slug: str,
        repo: str,
        mode: str = "full",
        since: datetime | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> GitHubImportResult:
        workspace = self.workspaces.get_by_slug(workspace_slug)
        if workspace is None:
            raise ValueError(f"Workspace not found: {workspace_slug}")
        if mode not in {"full", "since_last_sync"}:
            raise ValueError(f"Unsupported import mode: {mode}")

        effective_since = since if mode == "since_last_sync" else None

        issues = self.client.fetch_issues(repo, since=effective_since)
        pulls = self.client.fetch_pull_requests(repo, since=effective_since)
        commits = self.client.fetch_commits(repo, since=effective_since)
        default_branch = self.client.get_default_branch(repo)
        repository_files = self.client.list_repository_files(repo, ref=default_branch)
        selected_documents, skipped_document_counts = select_high_signal_repository_documents(repository_files)
        selected_document_categories = Counter(classify_repository_document(file.path) for file in selected_documents)

        # The recursive tree includes Git blob sizes. Reject oversized
        # selections before starting any source writes or document downloads.
        # Never truncate the selection: it would silently lose decision evidence.
        if len(selected_documents) > self.max_selected_documents:
            raise GitHubIncompleteCoverageError(
                reason="document_count_budget",
                scope=f"{repo}@{default_branch}",
                detail=f"selected {len(selected_documents)} documents exceeds {self.max_selected_documents} allowed",
            )
        advertised_bytes = 0
        for document in selected_documents:
            size = document.size
            if size is None:
                continue
            if not isinstance(size, int) or size < 0:
                raise GitHubIncompleteCoverageError(
                    reason="invalid_document_size",
                    scope=f"{repo}@{default_branch}",
                    detail=f"invalid Git tree size for {document.path}",
                )
            if size > self.max_single_document_bytes:
                raise GitHubIncompleteCoverageError(
                    reason="document_size_budget",
                    scope=f"{repo}@{default_branch}",
                    detail=f"document {document.path} exceeds {self.max_single_document_bytes} bytes",
                )
            advertised_bytes += size
            if advertised_bytes > self.max_total_document_bytes:
                raise GitHubIncompleteCoverageError(
                    reason="document_total_budget",
                    scope=f"{repo}@{default_branch}",
                    detail=f"selected document tree size exceeds {self.max_total_document_bytes} bytes",
                )

        # Complete all remote document downloads and validate their blob IDs
        # before the first Artifact INSERT/UPDATE. Holding SQLite's writer lock
        # while waiting on GitHub network futures blocks independent pause and
        # resume requests for the whole download duration.
        def fetch_doc(repository_file):
            source_id = repository_file.path
            signal_category = classify_repository_document(source_id)
            content = self.client.fetch_markdown_document(repo, path=source_id, ref=default_branch)
            actual_bytes = len(content.encode("utf-8"))
            if actual_bytes > self.max_single_document_bytes:
                raise GitHubIncompleteCoverageError(
                    reason="document_size_budget",
                    scope=f"{repo}@{default_branch}",
                    detail=f"downloaded document {source_id} exceeds {self.max_single_document_bytes} bytes",
                )
            expected_blob_sha = repository_file.sha
            if isinstance(expected_blob_sha, str) and re.fullmatch(r"[0-9a-f]{40}", expected_blob_sha):
                actual_blob_sha = _git_blob_sha(content)
                if actual_blob_sha != expected_blob_sha:
                    raise ValueError(
                        f"GitHub document changed between tree listing and content fetch: {source_id}"
                    )
            return repository_file, signal_category, content

        prefetched_documents = []
        downloaded_bytes = 0
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Bounded in-flight futures: submitting all selected documents at
            # once lets completed futures retain decoded text before their
            # results are charged against the aggregate byte budget.
            remaining_documents = iter(selected_documents)
            in_flight = {
                executor.submit(fetch_doc, document)
                for document in islice(remaining_documents, 5)
            }
            while in_flight:
                completed, _ = wait(in_flight, return_when=FIRST_COMPLETED)
                for future in completed:
                    in_flight.remove(future)
                    downloaded = future.result()
                    downloaded_bytes += len(downloaded[2].encode("utf-8"))
                    if downloaded_bytes > self.max_total_document_bytes:
                        raise GitHubIncompleteCoverageError(
                            reason="document_total_budget",
                            scope=f"{repo}@{default_branch}",
                            detail=f"downloaded Markdown exceeds {self.max_total_document_bytes} bytes",
                        )
                    prefetched_documents.append(downloaded)
                    next_document = next(remaining_documents, None)
                    if next_document is not None:
                        in_flight.add(executor.submit(fetch_doc, next_document))

        # This is the last write-free checkpoint. The caller may wait for a
        # paused job here, before any Artifact INSERT/UPDATE holds SQLite's
        # single-writer lock. A zero count explicitly means "pre-write".
        if progress_callback:
            progress_callback(0)

        # All sources are now locally fetched/validated. Persist Artifacts in
        # one transaction, keeping the import-stage failure rollback guarantee.
        total = 0
        artifact_counts = {"issue": 0, "pr": 0, "commit": 0, "doc": 0}
        for payload in issues + pulls + commits:
            self.artifacts.upsert(
                workspace_id=workspace.id,
                artifact_type=payload.artifact_type,
                source_id=payload.source_id,
                repo=payload.repo,
                title=payload.title,
                content=payload.content,
                author=payload.author,
                url=payload.url,
                timestamp=payload.timestamp,
                metadata_json=_capture_metadata(
                    payload.metadata_json,
                    payload.content,
                    method="github_api",
                ),
            )
            total += 1
            artifact_counts[payload.artifact_type] += 1
            if progress_callback:
                progress_callback(total)

        for repository_file, signal_category, content in prefetched_documents:
            source_id = repository_file.path
            self.artifacts.upsert(
                workspace_id=workspace.id,
                artifact_type="doc",
                source_id=source_id,
                repo=repo,
                title=PurePosixPath(source_id).stem,
                content=content,
                author=None,
                url=_repo_doc_url(workspace.repo_url, repo=repo, ref=default_branch, path=source_id),
                timestamp=None,
                metadata_json=_capture_metadata(
                    {
                        "source_metadata_origin": "github_contents_api",
                        "path": source_id,
                        "ref": default_branch,
                        "source": "github_repo_doc",
                        "signal_category": signal_category,
                        "blob_sha": repository_file.sha
                        if isinstance(repository_file.sha, str)
                        and re.fullmatch(r"[0-9a-f]{40}", repository_file.sha)
                        else None,
                    },
                    content,
                    method="github_contents_api",
                ),
            )
            total += 1
            artifact_counts["doc"] += 1
            if progress_callback:
                progress_callback(total)

        self.session.commit()
        return GitHubImportResult(
            imported_count=total,
            artifact_counts=artifact_counts,
            selected_document_count=len(selected_documents),
            imported_document_count=artifact_counts["doc"],
            skipped_document_counts=skipped_document_counts,
            selected_document_categories=dict(selected_document_categories),
        )


def _capture_metadata(metadata: dict | None, content: str, *, method: str) -> dict:
    """Record local import-time integrity metadata without claiming remote attestation."""
    result = dict(metadata or {})
    result["decisionatlas_capture"] = {
        "schema_version": 1,
        "captured_at": datetime.now(UTC).isoformat(),
        "method": method,
        "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
    }
    return result


def _git_blob_sha(content: str) -> str:
    """Return Git's SHA-1 object id for UTF-8 text, for tree/content race checks."""
    payload = content.encode("utf-8")
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()


def _repo_doc_url(repo_url: str | None, *, repo: str, ref: str, path: str) -> str:
    base = repo_url.rstrip("/") if repo_url else f"https://github.com/{repo}"
    return f"{base}/blob/{ref}/{path}"
