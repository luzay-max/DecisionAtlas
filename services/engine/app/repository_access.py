from __future__ import annotations

from app.repositories.github_token_access_sources import GitHubTokenAccessSourceRepository


def access_source_label(
    *,
    access_source_type: str,
    access_source_ref: str | None,
    display_label: str | None = None,
) -> str:
    if access_source_type == "github_app_installation":
        suffix = f" #{access_source_ref}" if access_source_ref else ""
        return f"GitHub App installation{suffix}"
    if access_source_type == "github_token":
        if display_label:
            return f"Private GitHub source {display_label}"
        if access_source_ref:
            return f"Private GitHub source {access_source_ref}"
        return "Private GitHub source"
    return "Public GitHub access"


def access_source_summary(
    *,
    session,
    owner_scope: str,
    access_source_type: str,
    access_source_ref: str | None,
) -> dict[str, str | None]:
    if access_source_type != "github_token":
        return {
            "access_source_label": access_source_label(
                access_source_type=access_source_type,
                access_source_ref=access_source_ref,
            ),
            "access_source_status": None,
            "access_source_status_detail": None,
        }

    record = None
    if access_source_ref:
        record = GitHubTokenAccessSourceRepository(session).get_by_owner_scope_and_source_ref(
            owner_scope=owner_scope,
            source_ref=access_source_ref,
        )
    display_label = record.display_label if record is not None else None
    return {
        "access_source_label": access_source_label(
            access_source_type=access_source_type,
            access_source_ref=access_source_ref,
            display_label=display_label,
        ),
        "access_source_status": record.authorization_status if record is not None else "missing",
        "access_source_status_detail": record.last_error if record is not None else "Private access source is not configured.",
    }
