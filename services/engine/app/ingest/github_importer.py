from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import PurePosixPath

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
                metadata_json=payload.metadata_json,
            )
            total += 1
            artifact_counts[payload.artifact_type] += 1

        for repository_file in selected_documents:
            source_id = repository_file.path
            signal_category = classify_repository_document(source_id)
            self.artifacts.upsert(
                workspace_id=workspace.id,
                artifact_type="doc",
                source_id=source_id,
                repo=repo,
                title=PurePosixPath(source_id).stem,
                content=self.client.fetch_markdown_document(repo, path=source_id, ref=default_branch),
                author=None,
                url=_repo_doc_url(workspace.repo_url, repo=repo, ref=default_branch, path=source_id),
                timestamp=None,
                metadata_json={
                    "path": source_id,
                    "ref": default_branch,
                    "source": "github_repo_doc",
                    "signal_category": signal_category,
                },
            )
            total += 1
            artifact_counts["doc"] += 1

        self.session.commit()
        return GitHubImportResult(
            imported_count=total,
            artifact_counts=artifact_counts,
            selected_document_count=len(selected_documents),
            imported_document_count=artifact_counts["doc"],
            skipped_document_counts=skipped_document_counts,
            selected_document_categories=dict(selected_document_categories),
        )


def _repo_doc_url(repo_url: str | None, *, repo: str, ref: str, path: str) -> str:
    base = repo_url.rstrip("/") if repo_url else f"https://github.com/{repo}"
    return f"{base}/blob/{ref}/{path}"
