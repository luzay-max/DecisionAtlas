from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import AuthContext, require_actor, require_scope_role
from app.db.models import Actor, WorkspaceMembership
from app.db.session import get_db_session
from app.repositories.auth import ROLE_ORDER, AuthRepository
from app.repositories.workspaces import WorkspaceRepository

router = APIRouter(prefix="/team", tags=["team"])


class TeamAccountCreateRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=8)
    display_name: str | None = None
    role: str = "viewer"


class TeamAccountRoleRequest(BaseModel):
    role: str


class TeamAccountPasswordResetRequest(BaseModel):
    password: str = Field(min_length=8)


class WorkspaceMemberRoleRequest(BaseModel):
    role: str


def _require_valid_role(role: str) -> str:
    if role not in ROLE_ORDER:
        raise HTTPException(status_code=400, detail=f"Unsupported role: {role}")
    return role


def _require_admin(auth: AuthContext) -> AuthContext:
    return require_scope_role(auth, owner_scope=auth.owner_scope, required_role="admin")


def _serialize_actor(actor: Actor, *, role: str | None = None) -> dict:
    return {
        "id": actor.id,
        "username": actor.username,
        "display_name": actor.display_name,
        "status": actor.status,
        "bootstrap": actor.is_bootstrap,
        "role": role,
    }


def _serialize_workspace_member(membership: WorkspaceMembership, actor: Actor) -> dict:
    return {
        "workspace_id": membership.workspace_id,
        "actor": _serialize_actor(actor),
        "role": membership.role,
    }


@router.get("/accounts")
def list_team_accounts(auth: AuthContext = Depends(require_actor)) -> dict:
    _require_admin(auth)
    session = get_db_session()
    try:
        repo = AuthRepository(session)
        scoped_memberships = {
            actor.id: membership.role
            for membership, actor in repo.list_memberships_for_scope(auth.owner_scope_id)
        }
        return {
            "accounts": [
                _serialize_actor(actor, role=scoped_memberships.get(actor.id))
                for actor in repo.list_actors()
                if actor.id in scoped_memberships
            ]
        }
    finally:
        session.close()


@router.post("/accounts")
def create_team_account(
    request: TeamAccountCreateRequest,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    _require_admin(auth)
    role = _require_valid_role(request.role)
    session = get_db_session()
    try:
        repo = AuthRepository(session)
        if repo.get_actor_by_username(request.username) is not None:
            raise HTTPException(status_code=409, detail="Username already exists")
        actor = repo.create_team_actor(
            username=request.username,
            password=request.password,
            display_name=request.display_name,
            owner_scope_id=auth.owner_scope_id,
            role=role,
        )
        session.commit()
        return {"account": _serialize_actor(actor, role=role)}
    finally:
        session.close()


@router.post("/accounts/{actor_id}/disable")
def disable_team_account(actor_id: int, auth: AuthContext = Depends(require_actor)) -> dict:
    _require_admin(auth)
    session = get_db_session()
    try:
        repo = AuthRepository(session)
        actor = repo.get_actor(actor_id)
        if actor is None:
            raise HTTPException(status_code=404, detail="Account not found")
        membership = repo.get_membership(actor_id=actor.id, owner_scope_id=auth.owner_scope_id)
        if membership is None:
            raise HTTPException(status_code=404, detail="Account not found")
        repo.set_actor_status(actor_id=actor_id, status="disabled")
        session.commit()
        return {"account": _serialize_actor(actor, role=membership.role)}
    finally:
        session.close()


@router.post("/accounts/{actor_id}/reset-password")
def reset_team_account_password(
    actor_id: int,
    request: TeamAccountPasswordResetRequest,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    _require_admin(auth)
    session = get_db_session()
    try:
        repo = AuthRepository(session)
        membership = repo.get_membership(actor_id=actor_id, owner_scope_id=auth.owner_scope_id)
        if membership is None:
            raise HTTPException(status_code=404, detail="Account not found")
        actor = repo.reset_actor_password(actor_id=actor_id, password=request.password)
        if actor is None:
            raise HTTPException(status_code=404, detail="Account not found")
        session.commit()
        return {"account": _serialize_actor(actor, role=membership.role)}
    finally:
        session.close()


@router.post("/accounts/{actor_id}/role")
def update_team_account_role(
    actor_id: int,
    request: TeamAccountRoleRequest,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    _require_admin(auth)
    role = _require_valid_role(request.role)
    session = get_db_session()
    try:
        repo = AuthRepository(session)
        actor = repo.get_actor(actor_id)
        if actor is None:
            raise HTTPException(status_code=404, detail="Account not found")
        repo.ensure_membership(actor_id=actor.id, owner_scope_id=auth.owner_scope_id, role=role)
        session.commit()
        return {"account": _serialize_actor(actor, role=role)}
    finally:
        session.close()


@router.get("/workspaces/{workspace_slug}/members")
def list_workspace_members(workspace_slug: str, auth: AuthContext = Depends(require_actor)) -> dict:
    _require_admin(auth)
    session = get_db_session()
    try:
        workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
        if workspace is None or workspace.owner_scope != auth.owner_scope:
            raise HTTPException(status_code=404, detail="Workspace not found")
        members = AuthRepository(session).list_workspace_memberships(workspace.id)
        return {
            "workspace_slug": workspace.slug,
            "members": [_serialize_workspace_member(membership, actor) for membership, actor in members],
        }
    finally:
        session.close()


@router.put("/workspaces/{workspace_slug}/members/{actor_id}")
def assign_workspace_member(
    workspace_slug: str,
    actor_id: int,
    request: WorkspaceMemberRoleRequest,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    _require_admin(auth)
    role = _require_valid_role(request.role)
    session = get_db_session()
    try:
        repo = AuthRepository(session)
        workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
        actor = repo.get_actor(actor_id)
        if workspace is None or workspace.owner_scope != auth.owner_scope:
            raise HTTPException(status_code=404, detail="Workspace not found")
        if actor is None or repo.get_membership(actor_id=actor.id, owner_scope_id=auth.owner_scope_id) is None:
            raise HTTPException(status_code=404, detail="Account not found")
        membership = repo.assign_workspace_membership(workspace_id=workspace.id, actor_id=actor.id, role=role)
        session.commit()
        return {"member": _serialize_workspace_member(membership, actor)}
    finally:
        session.close()


@router.delete("/workspaces/{workspace_slug}/members/{actor_id}")
def remove_workspace_member(
    workspace_slug: str,
    actor_id: int,
    auth: AuthContext = Depends(require_actor),
) -> dict:
    _require_admin(auth)
    session = get_db_session()
    try:
        repo = AuthRepository(session)
        workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
        if workspace is None or workspace.owner_scope != auth.owner_scope:
            raise HTTPException(status_code=404, detail="Workspace not found")
        removed = repo.remove_workspace_membership(workspace_id=workspace.id, actor_id=actor_id)
        session.commit()
        return {"removed": removed}
    finally:
        session.close()
