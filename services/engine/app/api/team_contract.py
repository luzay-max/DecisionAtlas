from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


TeamRole = Literal["viewer", "reviewer", "admin"]
TeamActorStatus = Literal["active", "disabled"]


class TeamContractModel(BaseModel):
    """Strict response DTOs for existing team/account/member operations."""

    model_config = ConfigDict(extra="forbid")


class TeamAccountResponse(TeamContractModel):
    id: int
    username: str
    display_name: str | None
    status: TeamActorStatus
    bootstrap: bool
    role: TeamRole


class TeamWorkspaceActorResponse(TeamContractModel):
    id: int
    username: str
    display_name: str | None
    status: TeamActorStatus
    bootstrap: bool
    role: TeamRole | None


class TeamWorkspaceMemberResponse(TeamContractModel):
    workspace_id: int
    actor: TeamWorkspaceActorResponse
    role: TeamRole


class TeamAccountListResponse(TeamContractModel):
    accounts: list[TeamAccountResponse]


class TeamAccountMutationResponse(TeamContractModel):
    account: TeamAccountResponse


class TeamWorkspaceMembersResponse(TeamContractModel):
    workspace_slug: str
    members: list[TeamWorkspaceMemberResponse]


class TeamWorkspaceMemberMutationResponse(TeamContractModel):
    member: TeamWorkspaceMemberResponse


class TeamWorkspaceMemberRemovalResponse(TeamContractModel):
    removed: bool
