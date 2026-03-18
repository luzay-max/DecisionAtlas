from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.ingest.github_client import GitHubClient
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
    ) -> int:
        workspace = self.workspaces.get_by_slug(workspace_slug)
        if workspace is None:
            raise ValueError(f"Workspace not found: {workspace_slug}")
        if mode not in {"full", "since_last_sync"}:
            raise ValueError(f"Unsupported import mode: {mode}")

        effective_since = since if mode == "since_last_sync" else None

        total = 0
        for payload in (
            self.client.fetch_issues(repo, since=effective_since)
            + self.client.fetch_pull_requests(repo, since=effective_since)
            + self.client.fetch_commits(repo, since=effective_since)
        ):
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

        self.session.commit()
        return total
