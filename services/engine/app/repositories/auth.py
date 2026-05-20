from __future__ import annotations

from datetime import UTC, datetime
from secrets import token_urlsafe

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import Actor, AuthSession, OwnerScope, OwnerScopeMembership, Workspace, WorkspaceMembership


ROLE_ORDER = {"viewer": 0, "reviewer": 1, "admin": 2}


class AuthRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_actor_by_username(self, username: str) -> Actor | None:
        return self.session.scalar(select(Actor).where(Actor.username == username))

    def list_actors(self) -> list[Actor]:
        return list(self.session.scalars(select(Actor).order_by(Actor.username.asc())).all())

    def get_actor(self, actor_id: int) -> Actor | None:
        return self.session.get(Actor, actor_id)

    def get_scope_by_key(self, scope_key: str) -> OwnerScope | None:
        return self.session.scalar(select(OwnerScope).where(OwnerScope.scope_key == scope_key))

    def get_membership(self, *, actor_id: int, owner_scope_id: int) -> OwnerScopeMembership | None:
        stmt = select(OwnerScopeMembership).where(
            OwnerScopeMembership.actor_id == actor_id,
            OwnerScopeMembership.owner_scope_id == owner_scope_id,
        )
        return self.session.scalar(stmt)

    def list_memberships_for_actor(self, actor_id: int) -> list[tuple[OwnerScopeMembership, OwnerScope]]:
        stmt = (
            select(OwnerScopeMembership, OwnerScope)
            .join(OwnerScope, OwnerScope.id == OwnerScopeMembership.owner_scope_id)
            .where(OwnerScopeMembership.actor_id == actor_id)
            .order_by(OwnerScope.scope_key.asc())
        )
        return list(self.session.execute(stmt).all())

    def list_memberships_for_scope(self, owner_scope_id: int) -> list[tuple[OwnerScopeMembership, Actor]]:
        stmt = (
            select(OwnerScopeMembership, Actor)
            .join(Actor, Actor.id == OwnerScopeMembership.actor_id)
            .where(OwnerScopeMembership.owner_scope_id == owner_scope_id)
            .order_by(Actor.username.asc())
        )
        return list(self.session.execute(stmt).all())

    def get_auth_session(self, session_token: str) -> AuthSession | None:
        return self.session.scalar(select(AuthSession).where(AuthSession.session_token == session_token))

    def create_actor(
        self,
        *,
        username: str,
        password_hash: str,
        display_name: str | None = None,
        is_bootstrap: bool = False,
    ) -> Actor:
        actor = Actor(
            username=username,
            password_hash=password_hash,
            display_name=display_name,
            is_bootstrap=is_bootstrap,
        )
        self.session.add(actor)
        self.session.flush()
        return actor

    def create_team_actor(
        self,
        *,
        username: str,
        password: str,
        display_name: str | None = None,
        owner_scope_id: int,
        role: str = "viewer",
    ) -> Actor:
        actor = self.create_actor(
            username=username,
            password_hash=hash_password(password),
            display_name=display_name,
        )
        self.ensure_membership(actor_id=actor.id, owner_scope_id=owner_scope_id, role=role)
        return actor

    def set_actor_status(self, *, actor_id: int, status: str) -> Actor | None:
        actor = self.get_actor(actor_id)
        if actor is None:
            return None
        actor.status = status
        actor.disabled_at = datetime.now(UTC) if status != "active" else None
        self.session.flush()
        return actor

    def reset_actor_password(self, *, actor_id: int, password: str) -> Actor | None:
        actor = self.get_actor(actor_id)
        if actor is None:
            return None
        actor.password_hash = hash_password(password)
        self.session.flush()
        return actor

    def create_scope(self, *, scope_key: str, display_name: str, scope_type: str = "local") -> OwnerScope:
        scope = OwnerScope(scope_key=scope_key, display_name=display_name, scope_type=scope_type)
        self.session.add(scope)
        self.session.flush()
        return scope

    def ensure_membership(self, *, actor_id: int, owner_scope_id: int, role: str) -> OwnerScopeMembership:
        membership = self.get_membership(actor_id=actor_id, owner_scope_id=owner_scope_id)
        if membership is None:
            membership = OwnerScopeMembership(actor_id=actor_id, owner_scope_id=owner_scope_id, role=role)
            self.session.add(membership)
            self.session.flush()
            return membership
        membership.role = role
        self.session.flush()
        return membership

    def get_workspace_membership(self, *, workspace_id: int, actor_id: int) -> WorkspaceMembership | None:
        stmt = select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.actor_id == actor_id,
        )
        return self.session.scalar(stmt)

    def list_workspace_memberships(self, workspace_id: int) -> list[tuple[WorkspaceMembership, Actor]]:
        stmt = (
            select(WorkspaceMembership, Actor)
            .join(Actor, Actor.id == WorkspaceMembership.actor_id)
            .where(WorkspaceMembership.workspace_id == workspace_id)
            .order_by(Actor.username.asc())
        )
        return list(self.session.execute(stmt).all())

    def workspace_has_memberships(self, workspace_id: int) -> bool:
        count = self.session.scalar(
            select(func.count(WorkspaceMembership.id)).where(WorkspaceMembership.workspace_id == workspace_id)
        )
        return bool(count)

    def assign_workspace_membership(self, *, workspace_id: int, actor_id: int, role: str) -> WorkspaceMembership:
        membership = self.get_workspace_membership(workspace_id=workspace_id, actor_id=actor_id)
        if membership is None:
            membership = WorkspaceMembership(workspace_id=workspace_id, actor_id=actor_id, role=role)
            self.session.add(membership)
            self.session.flush()
            return membership
        membership.role = role
        self.session.flush()
        return membership

    def remove_workspace_membership(self, *, workspace_id: int, actor_id: int) -> bool:
        membership = self.get_workspace_membership(workspace_id=workspace_id, actor_id=actor_id)
        if membership is None:
            return False
        self.session.delete(membership)
        self.session.flush()
        return True

    def resolve_workspace_role(self, *, actor_id: int, workspace: Workspace, owner_scope_id: int) -> str | None:
        if self.workspace_has_memberships(workspace.id):
            workspace_membership = self.get_workspace_membership(workspace_id=workspace.id, actor_id=actor_id)
            return workspace_membership.role if workspace_membership else None
        scope_membership = self.get_membership(actor_id=actor_id, owner_scope_id=owner_scope_id)
        return scope_membership.role if scope_membership else None

    def create_session(self, *, actor_id: int, owner_scope_id: int) -> AuthSession:
        auth_session = AuthSession(
            session_token=token_urlsafe(32),
            actor_id=actor_id,
            current_owner_scope_id=owner_scope_id,
        )
        self.session.add(auth_session)
        self.session.flush()
        return auth_session

    def touch_session(self, auth_session: AuthSession) -> AuthSession:
        auth_session.last_seen_at = datetime.now(UTC)
        self.session.flush()
        return auth_session

    def switch_scope(self, auth_session: AuthSession, *, owner_scope_id: int) -> AuthSession:
        auth_session.current_owner_scope_id = owner_scope_id
        auth_session.last_seen_at = datetime.now(UTC)
        self.session.flush()
        return auth_session


def ensure_bootstrap_identity(session: Session) -> tuple[Actor, OwnerScope, OwnerScopeMembership]:
    settings = get_settings()
    repo = AuthRepository(session)
    actor = repo.get_actor_by_username(settings.local_bootstrap_username)
    if actor is None:
        actor = repo.create_actor(
            username=settings.local_bootstrap_username,
            password_hash=hash_password(settings.local_bootstrap_password),
            display_name="Local Admin",
            is_bootstrap=True,
        )

    scope = repo.get_scope_by_key(settings.default_owner_scope)
    if scope is None:
        scope = repo.create_scope(
            scope_key=settings.default_owner_scope,
            display_name="Local Default",
            scope_type="local",
        )

    membership = repo.ensure_membership(actor_id=actor.id, owner_scope_id=scope.id, role="admin")
    session.flush()
    return actor, scope, membership


def hash_password(password: str) -> str:
    import hashlib
    import secrets

    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    import hashlib

    try:
        salt, expected = password_hash.split("$", 1)
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return digest.hex() == expected


def role_allows(actual_role: str, required_role: str) -> bool:
    return ROLE_ORDER.get(actual_role, -1) >= ROLE_ORDER.get(required_role, -1)
