from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import GitHubTokenAccessSource


class GitHubTokenAccessSourceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_owner_scope_and_source_ref(self, *, owner_scope: str, source_ref: str) -> GitHubTokenAccessSource | None:
        stmt = select(GitHubTokenAccessSource).where(
            GitHubTokenAccessSource.owner_scope == owner_scope,
            GitHubTokenAccessSource.source_ref == source_ref,
        )
        return self.session.scalar(stmt)

    def get_by_owner_scope_and_repo_identity(
        self,
        *,
        owner_scope: str,
        repo_identity: str,
    ) -> GitHubTokenAccessSource | None:
        stmt = select(GitHubTokenAccessSource).where(
            GitHubTokenAccessSource.owner_scope == owner_scope,
            GitHubTokenAccessSource.repo_identity == repo_identity,
        )
        return self.session.scalar(stmt)

    def upsert(
        self,
        *,
        owner_scope: str,
        source_ref: str,
        display_label: str,
        repo_identity: str,
        token_secret: str,
        authorization_status: str,
        last_error: str | None,
        validated_at: datetime | None,
    ) -> GitHubTokenAccessSource:
        record = self.get_by_owner_scope_and_source_ref(owner_scope=owner_scope, source_ref=source_ref)
        if record is None:
            record = GitHubTokenAccessSource(
                owner_scope=owner_scope,
                source_ref=source_ref,
                display_label=display_label,
                repo_identity=repo_identity,
                token_secret=token_secret,
                authorization_status=authorization_status,
                last_error=last_error,
                last_validated_at=validated_at,
            )
            self.session.add(record)
        else:
            record.display_label = display_label
            record.repo_identity = repo_identity
            record.token_secret = token_secret
            record.authorization_status = authorization_status
            record.last_error = last_error
            record.last_validated_at = validated_at
        self.session.flush()
        return record

    def mark_authorized(self, record: GitHubTokenAccessSource, *, validated_at: datetime) -> GitHubTokenAccessSource:
        record.authorization_status = "authorized"
        record.last_validated_at = validated_at
        record.last_error = None
        self.session.flush()
        return record

    def mark_invalid(
        self,
        record: GitHubTokenAccessSource,
        *,
        validated_at: datetime,
        error_message: str,
    ) -> GitHubTokenAccessSource:
        record.authorization_status = "invalid"
        record.last_validated_at = validated_at
        record.last_error = error_message
        self.session.flush()
        return record

    def mark_status(
        self,
        record: GitHubTokenAccessSource,
        *,
        status: str,
        validated_at: datetime,
        error_message: str | None,
    ) -> GitHubTokenAccessSource:
        record.authorization_status = status
        record.last_validated_at = validated_at
        record.last_error = error_message
        self.session.flush()
        return record
