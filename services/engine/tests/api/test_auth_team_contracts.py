from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.api.team_contract import TeamAccountResponse
from app.main import create_app


def _response_schema(schema: dict, path: str, method: str) -> dict:
    return schema["paths"][path][method]["responses"]["200"]["content"]["application/json"]["schema"]


def test_auth_and_team_operations_reference_named_response_dtos() -> None:
    schema = create_app().openapi()
    expected = {
        ("/auth/bootstrap", "post"): "AuthBootstrapResponse",
        ("/auth/login", "post"): "AuthLoginResponse",
        ("/auth/logout", "post"): "AuthLogoutResponse",
        ("/auth/session", "get"): "AuthSessionResponse",
        ("/auth/scope", "post"): "AuthSessionResponse",
        ("/team/accounts", "get"): "TeamAccountListResponse",
        ("/team/accounts", "post"): "TeamAccountMutationResponse",
        ("/team/accounts/{actor_id}/disable", "post"): "TeamAccountMutationResponse",
        ("/team/accounts/{actor_id}/reset-password", "post"): "TeamAccountMutationResponse",
        ("/team/accounts/{actor_id}/role", "post"): "TeamAccountMutationResponse",
        ("/team/workspaces/{workspace_slug}/members", "get"): "TeamWorkspaceMembersResponse",
        ("/team/workspaces/{workspace_slug}/members/{actor_id}", "put"): "TeamWorkspaceMemberMutationResponse",
        ("/team/workspaces/{workspace_slug}/members/{actor_id}", "delete"): "TeamWorkspaceMemberRemovalResponse",
    }

    for (path, method), model_name in expected.items():
        assert _response_schema(schema, path, method)["$ref"] == f"#/components/schemas/{model_name}"

    schemas = schema["components"]["schemas"]
    for name in set(expected.values()):
        assert schemas[name]["additionalProperties"] is False


def test_auth_session_variants_and_team_member_nullability_are_explicit() -> None:
    schemas = create_app().openapi()["components"]["schemas"]

    assert set(schemas["AuthBootstrapActorResponse"]["properties"]) == {"id", "username", "bootstrap", "status"}
    assert set(schemas["AuthSessionActorResponse"]["properties"]) == {"id", "username", "bootstrap"}
    assert "available_scopes" not in schemas["AuthBootstrapResponse"]["properties"]
    assert "available_scopes" in schemas["AuthLoginResponse"]["properties"]
    assert "session_token" in schemas["AuthSessionResponse"]["properties"]

    workspace_actor = schemas["TeamWorkspaceActorResponse"]["properties"]
    assert workspace_actor["role"]["anyOf"][-1] == {"type": "null"}
    assert "password" not in schemas["TeamAccountResponse"]["properties"]
    assert "session_token" not in schemas["TeamAccountResponse"]["properties"]


def test_team_account_response_dto_rejects_unmodeled_credentials() -> None:
    payload = {
        "id": 1,
        "username": "admin",
        "display_name": None,
        "status": "active",
        "bootstrap": False,
        "role": "admin",
    }
    assert TeamAccountResponse.model_validate(payload).role == "admin"

    with pytest.raises(ValidationError):
        TeamAccountResponse.model_validate({**payload, "password": "must-not-leak"})

    with pytest.raises(ValidationError):
        TeamAccountResponse.model_validate({**payload, "session_token": "must-not-leak"})
