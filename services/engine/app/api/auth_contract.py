from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


AuthRole = Literal["viewer", "reviewer", "admin"]
AuthActorStatus = Literal["active", "disabled"]


class AuthContractModel(BaseModel):
    """Strict response DTOs for the existing authentication API."""

    model_config = ConfigDict(extra="forbid")


class AuthSessionActorResponse(AuthContractModel):
    id: int
    username: str
    bootstrap: bool


class AuthBootstrapActorResponse(AuthContractModel):
    id: int
    username: str
    bootstrap: bool
    status: AuthActorStatus


class AuthOwnerScopeMembershipResponse(AuthContractModel):
    owner_scope: str
    role: AuthRole


class AuthBootstrapResponse(AuthContractModel):
    session_token: str
    actor: AuthBootstrapActorResponse
    current_owner_scope: str
    role: AuthRole


class AuthLoginResponse(AuthContractModel):
    session_token: str
    actor: AuthBootstrapActorResponse
    current_owner_scope: str
    role: AuthRole
    available_scopes: list[AuthOwnerScopeMembershipResponse]


class AuthSessionResponse(AuthContractModel):
    session_token: str
    actor: AuthSessionActorResponse
    current_owner_scope: str
    role: AuthRole
    available_scopes: list[AuthOwnerScopeMembershipResponse]


class AuthLogoutResponse(AuthContractModel):
    status: Literal["signed_out"]
