from __future__ import annotations

from dataclasses import dataclass

from fastapi import Header, HTTPException

from app.config import get_settings
from app.db.models import Actor, OwnerScope
from app.db.session import get_db_session
from app.repositories.auth import AuthRepository, ensure_bootstrap_identity, role_allows
from app.repositories.workspaces import WorkspaceRepository

SESSION_HEADER = "x-decisionatlas-session-token"


@dataclass(frozen=True)
class AuthContext:
    actor_id: int
    username: str
    owner_scope: str
    owner_scope_id: int
    role: str
    session_token: str
    bootstrap: bool


def require_actor(
    x_decisionatlas_session_token: str | None = Header(default=None, alias=SESSION_HEADER),
) -> AuthContext:
    session = get_db_session()
    try:
        settings = get_settings()
        repo = AuthRepository(session)
        auth_session = repo.get_auth_session(x_decisionatlas_session_token) if x_decisionatlas_session_token else None

        if auth_session is None:
            if not settings.auth_auto_bootstrap_local:
                raise HTTPException(status_code=401, detail="Authentication required")
            actor, scope, membership = ensure_bootstrap_identity(session)
            auth_session = repo.create_session(actor_id=actor.id, owner_scope_id=scope.id)
            session.commit()
            return AuthContext(
                actor_id=actor.id,
                username=actor.username,
                owner_scope=scope.scope_key,
                owner_scope_id=scope.id,
                role=membership.role,
                session_token=auth_session.session_token,
                bootstrap=True,
            )

        actor = session.get(Actor, auth_session.actor_id)
        scope = session.get(OwnerScope, auth_session.current_owner_scope_id)
        if actor is None or scope is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        membership = repo.get_membership(actor_id=actor.id, owner_scope_id=scope.id)
        if membership is None:
            raise HTTPException(status_code=403, detail="Owner scope membership required")
        repo.touch_session(auth_session)
        session.commit()
        return AuthContext(
            actor_id=actor.id,
            username=actor.username,
            owner_scope=scope.scope_key,
            owner_scope_id=scope.id,
            role=membership.role,
            session_token=auth_session.session_token,
            bootstrap=actor.is_bootstrap,
        )
    finally:
        session.close()


def require_role(auth: AuthContext, required_role: str) -> AuthContext:
    if not role_allows(auth.role, required_role):
        raise HTTPException(status_code=403, detail="Forbidden")
    return auth


def require_scope_role(auth: AuthContext, *, owner_scope: str, required_role: str, hide_not_found: bool = False) -> AuthContext:
    if auth.owner_scope != owner_scope:
        if hide_not_found:
            raise HTTPException(status_code=404, detail="Workspace not found")
        raise HTTPException(status_code=403, detail="Forbidden")
    return require_role(auth, required_role)


def require_workspace_role(
    session,
    auth: AuthContext,
    *,
    workspace_slug: str,
    required_role: str,
    hide_not_found: bool = True,
):
    workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
    if workspace is None:
        raise HTTPException(status_code=404, detail=f"Workspace not found: {workspace_slug}")
    require_scope_role(auth, owner_scope=workspace.owner_scope, required_role=required_role, hide_not_found=hide_not_found)
    return workspace
