from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
import hashlib
import re
from pathlib import PurePosixPath
from typing import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from sqlalchemy.orm import Session

from app.ingest.github_client import GitHubClient
from app.ingest.github_document_selection import classify_repository_document, select_high_signal_repository_documents
from app.ingest.github_types import GitHubImportResult
from app.repositories.artifacts import ArtifactRepository
from app.repositories.workspaces import WorkspaceRepository


class GitHubImporter:
    def __init__(self, session: Session, client: GitHubClient) -> None:
        self.session = session
        self.client = client
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

        def fetch_doc(repository_file):
            source_id = repository_file.path
            signal_category = classify_repository_document(source_id)
            content = self.client.fetch_markdown_document(repo, path=source_id, ref=default_branch)
            expected_blob_sha = repository_file.sha
            if isinstance(expected_blob_sha, str) and re.fullmatch(r"[0-9a-f]{40}", expected_blob_sha):
                actual_blob_sha = _git_blob_sha(content)
                if actual_blob_sha != expected_blob_sha:
                    raise ValueError(
                        f"GitHub document changed between tree listing and content fetch: {source_id}"
                    )
            return repository_file, signal_category, content

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_doc, doc): doc for doc in selected_documents}
            for future in as_completed(futures):
                repository_file, signal_category, content = future.result()
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
