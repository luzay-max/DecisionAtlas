from __future__ import annotations

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

    def import_repo(self, *, workspace_slug: str, repo: str) -> int:
        workspace = self.workspaces.get_by_slug(workspace_slug)
        if workspace is None:
            raise ValueError(f"Workspace not found: {workspace_slug}")

        total = 0
        for payload in (
            self.client.fetch_issues(repo)
            + self.client.fetch_pull_requests(repo)
            + self.client.fetch_commits(repo)
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
