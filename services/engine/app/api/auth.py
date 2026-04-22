from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.auth import SESSION_HEADER, require_actor
from app.db.session import get_db_session
from app.repositories.auth import AuthRepository, ensure_bootstrap_identity, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class ScopeSwitchRequest(BaseModel):
    owner_scope: str


@router.post("/bootstrap")
def bootstrap_auth() -> dict:
    session = get_db_session()
    try:
        actor, scope, membership = ensure_bootstrap_identity(session)
        auth_session = AuthRepository(session).create_session(actor_id=actor.id, owner_scope_id=scope.id)
        session.commit()
        return {
            "session_token": auth_session.session_token,
            "actor": {
                "id": actor.id,
                "username": actor.username,
            },
            "current_owner_scope": scope.scope_key,
            "role": membership.role,
        }
    finally:
        session.close()


@router.post("/login")
def login(request: LoginRequest) -> dict:
    session = get_db_session()
    try:
        repo = AuthRepository(session)
        actor = repo.get_actor_by_username(request.username)
        if actor is None or not verify_password(request.password, actor.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        memberships = repo.list_memberships_for_actor(actor.id)
        if not memberships:
            raise HTTPException(status_code=403, detail="Owner scope membership required")
        membership, scope = memberships[0]
        auth_session = repo.create_session(actor_id=actor.id, owner_scope_id=scope.id)
        session.commit()
        return {
            "session_token": auth_session.session_token,
            "actor": {"id": actor.id, "username": actor.username},
            "current_owner_scope": scope.scope_key,
            "role": membership.role,
            "available_scopes": [
                {"owner_scope": member_scope.scope_key, "role": member.role}
                for member, member_scope in memberships
            ],
        }
    finally:
        session.close()


@router.get("/session")
def get_session(
    x_decisionatlas_session_token: str | None = Header(default=None, alias=SESSION_HEADER),
) -> dict:
    auth = require_actor(x_decisionatlas_session_token)
    session = get_db_session()
    try:
        memberships = AuthRepository(session).list_memberships_for_actor(auth.actor_id)
        return {
            "actor": {"id": auth.actor_id, "username": auth.username, "bootstrap": auth.bootstrap},
            "current_owner_scope": auth.owner_scope,
            "role": auth.role,
            "available_scopes": [
                {"owner_scope": scope.scope_key, "role": membership.role}
                for membership, scope in memberships
            ],
            "session_token": auth.session_token,
        }
    finally:
        session.close()


@router.post("/scope")
def switch_scope(
    request: ScopeSwitchRequest,
    x_decisionatlas_session_token: str | None = Header(default=None, alias=SESSION_HEADER),
) -> dict:
    auth = require_actor(x_decisionatlas_session_token)
    session = get_db_session()
    try:
        repo = AuthRepository(session)
        auth_session = repo.get_auth_session(auth.session_token)
        target_scope = repo.get_scope_by_key(request.owner_scope)
        if auth_session is None or target_scope is None:
            raise HTTPException(status_code=404, detail="Owner scope not found")
        membership = repo.get_membership(actor_id=auth.actor_id, owner_scope_id=target_scope.id)
        if membership is None:
            raise HTTPException(status_code=403, detail="Forbidden")
        repo.switch_scope(auth_session, owner_scope_id=target_scope.id)
        session.commit()
        return {
            "current_owner_scope": target_scope.scope_key,
            "role": membership.role,
            "session_token": auth.session_token,
        }
    finally:
        session.close()
