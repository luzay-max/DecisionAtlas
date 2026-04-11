from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import GitHubAppInstallation


class GitHubAppInstallationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_owner_scope_and_installation(self, *, owner_scope: str, installation_id: str) -> GitHubAppInstallation | None:
        stmt = select(GitHubAppInstallation).where(
            GitHubAppInstallation.owner_scope == owner_scope,
            GitHubAppInstallation.installation_id == installation_id,
        )
        return self.session.scalar(stmt)

    def get_by_installation_id(self, installation_id: str) -> GitHubAppInstallation | None:
        stmt = select(GitHubAppInstallation).where(GitHubAppInstallation.installation_id == installation_id)
        return self.session.scalar(stmt)

    def upsert(
        self,
        *,
        owner_scope: str,
        installation_id: str,
        account_login: str | None,
        account_type: str | None,
    ) -> GitHubAppInstallation:
        record = self.get_by_owner_scope_and_installation(owner_scope=owner_scope, installation_id=installation_id)
        if record is None:
            record = GitHubAppInstallation(
                owner_scope=owner_scope,
                installation_id=installation_id,
                account_login=account_login,
                account_type=account_type,
            )
            self.session.add(record)
        else:
            record.account_login = account_login
            record.account_type = account_type
        self.session.flush()
        return record
