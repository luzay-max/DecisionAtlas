from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_GIT_PROVIDERS = {"github", "gitlab", "gitee", "local"}
SUPPORTED_ACCESS_MODES = {"public", "token", "local_path"}


@dataclass(frozen=True)
class GitSourceRequest:
    provider: str
    access_mode: str
    repo: str
    token: str | None = None
    source_ref: str | None = None
    source_label: str | None = None
    workspace_slug: str | None = None


def normalize_provider(value: str | None) -> str:
    provider = (value or "").strip().lower()
    if provider not in SUPPORTED_GIT_PROVIDERS:
        raise ValueError("Unsupported Git provider. Use github, gitlab, gitee, or local.")
    return provider


def normalize_access_mode(value: str | None) -> str:
    access_mode = (value or "").strip().lower()
    if access_mode not in SUPPORTED_ACCESS_MODES:
        raise ValueError("Unsupported Git access mode. Use public, token, or local_path.")
    return access_mode


def provider_access_label(*, provider: str, access_mode: str, source_label: str | None = None) -> str:
    provider_label = {
        "github": "GitHub",
        "gitlab": "GitLab",
        "gitee": "Gitee",
        "local": "Local repository",
    }.get(provider, provider)
    mode_label = {
        "public": "public access",
        "token": "token access",
        "local_path": "server local path",
    }.get(access_mode, access_mode)
    if source_label:
        return f"{provider_label} {mode_label} source {source_label}"
    return f"{provider_label} {mode_label}"


def provider_unsupported_result(
    *,
    provider: str,
    access_mode: str,
    owner_scope: str,
    repo: str,
    source_label: str | None = None,
) -> dict[str, object | None]:
    return {
        "owner_scope": owner_scope,
        "provider": provider,
        "access_mode": access_mode,
        "repo": repo,
        "repo_url": None,
        "workspace_exists": False,
        "workspace_slug": None,
        "has_successful_import": False,
        "can_incremental_sync": False,
        "has_running_import": False,
        "latest_import": None,
        "active_import": None,
        "access_source_type": f"{provider}_{access_mode}",
        "access_source_label": provider_access_label(
            provider=provider,
            access_mode=access_mode,
            source_label=source_label,
        ),
        "access_source_status": "not_implemented",
        "access_source_status_detail": f"{provider} {access_mode} ingestion is not implemented in this self-hosted build.",
        "setup_outcome": "provider_unsupported",
        "next_action": "plan_provider_importer",
    }


def local_path_guided_result(
    *,
    owner_scope: str,
    source_label: str | None = None,
) -> dict[str, object | None]:
    return {
        "owner_scope": owner_scope,
        "provider": "local",
        "access_mode": "local_path",
        "repo": "local_path",
        "repo_url": None,
        "workspace_exists": False,
        "workspace_slug": None,
        "has_successful_import": False,
        "can_incremental_sync": False,
        "has_running_import": False,
        "latest_import": None,
        "active_import": None,
        "access_source_type": "local_path",
        "access_source_label": provider_access_label(
            provider="local",
            access_mode="local_path",
            source_label=source_label,
        ),
        "access_source_status": "operator_guided",
        "access_source_status_detail": "Local path import is server-operator-guided and not enabled from the browser yet.",
        "setup_outcome": "local_path_unavailable",
        "next_action": "configure_server_local_path_import",
    }


def decorate_github_result(*, result: dict, access_mode: str, setup_outcome: str) -> dict:
    return {
        **result,
        "provider": "github",
        "access_mode": access_mode,
        "setup_outcome": setup_outcome,
        "next_action": "run_import_or_open_workspace",
    }
