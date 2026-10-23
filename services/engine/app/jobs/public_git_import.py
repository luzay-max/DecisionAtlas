"""Explicit, public-only GitLab/Gitee import job setup.

Never grants credentials, trusts user-supplied API hosts, or silently binds an
existing workspace to a different repository / tenant. Uses the existing
ImportJob and Workspace tables; actual indexing/extraction remains in the
existing run_github_import worker with a provider parameter.
"""
from __future__ import annotations

import hashlib
import re
from urllib.parse import urlparse
from uuid import uuid4

from app.db.session import get_db_session
from app.ingest.git_provider_clients import GitProviderError, _validate_repo
from app.jobs.import_jobs import ActiveImportConflict, serialize_import_job
from app.repositories.import_jobs import ImportJobRepository
from app.repositories.workspaces import WorkspaceRepository

PUBLIC_HOSTS = {"gitlab": "gitlab.com", "gitee": "gitee.com"}
_SLUG = re.compile(r"^[A-Za-z0-9_-]{1,120}$")


def normalize_public_repo(*, provider: str, repo: str) -> tuple[str, str]:
    """Accept only a repository name or a clean HTTPS URL on the official host."""
    if provider not in PUBLIC_HOSTS:
        raise GitProviderError("Only public gitlab and gitee imports are supported")
    if not repo or repo != repo.strip():
        raise GitProviderError("Invalid repository address")
    value = repo
    if "://" in value:
        parsed = urlparse(value)
        if (parsed.scheme != "https" or parsed.hostname != PUBLIC_HOSTS[provider]
                or parsed.username or parsed.password or parsed.port
                or parsed.query or parsed.fragment or parsed.params):
            raise GitProviderError("Repository URL must use the approved public HTTPS host")
        value = parsed.path.strip("/")
        if not value or "//" in parsed.path:
            raise GitProviderError("Invalid repository address")
    if value.endswith(".git"):
        value = value[:-4]
    normalized = _validate_repo(value, nested=(provider == "gitlab"))
    return normalized, f"https://{PUBLIC_HOSTS[provider]}/{normalized}"


def _default_slug(*, provider: str, repo: str, owner_scope: str) -> str:
    digest = hashlib.sha256(f"{owner_scope}\0{provider}\0{repo}".encode("utf-8")).hexdigest()[:12]
    safe = re.sub(r"[^a-z0-9]+", "-", repo.lower()).strip("-")
    return f"{provider}-{safe[:90].strip('-')}-{digest}"


def queue_public_git_import(
    *, provider: str, repo: str, mode: str, owner_scope: str,
    workspace_slug: str | None = None,
) -> dict:
    if mode not in {"full", "since_last_sync"}:
        raise GitProviderError("Unsupported import mode")
    normalized, repo_url = normalize_public_repo(provider=provider, repo=repo)
    if not owner_scope or not owner_scope.strip():
        raise GitProviderError("Authenticated owner scope is required")
    if workspace_slug is not None and not _SLUG.fullmatch(workspace_slug):
        raise GitProviderError("Invalid workspace identifier")
    identity = f"{provider}:{normalized}"
    session = get_db_session()
    try:
        workspaces = WorkspaceRepository(session)
        existing = workspaces.get_by_repo_identity(owner_scope=owner_scope, repo_identity=identity)
        if workspace_slug:
            requested = workspaces.get_by_slug(workspace_slug)
            if requested is not None and (
                requested.owner_scope != owner_scope
                or requested.repo_identity != identity
                or requested.repo_url != repo_url
            ):
                raise GitProviderError("Workspace is not available for this repository")
            if existing is not None and existing.slug != workspace_slug:
                raise GitProviderError("Repository is already bound to a different workspace")
            workspace = requested or existing
            slug = workspace_slug
        else:
            workspace = existing
            slug = existing.slug if existing is not None else _default_slug(
                provider=provider, repo=normalized, owner_scope=owner_scope,
            )
            if workspace is None and workspaces.get_by_slug(slug) is not None:
                raise GitProviderError("Workspace identifier collision")
        if workspace is None:
            workspace = workspaces.create(
                slug=slug, name=normalized, repo_url=repo_url,
                owner_scope=owner_scope, repo_identity=identity,
                access_source_type=f"{provider}_public",
            )
        elif workspace.access_source_type != f"{provider}_public":
            raise GitProviderError("Repository uses a different access source")
        jobs = ImportJobRepository(session)
        active = jobs.latest_active_for_workspace(workspace.id)
        if active is not None:
            raise ActiveImportConflict(active_job=serialize_import_job(session=session, job=active))
        job = jobs.create(
            job_id=str(uuid4()), workspace_id=workspace.id, repo=normalized,
            mode=mode, sync_origin=f"{provider}_public_manual_{'incremental' if mode == 'since_last_sync' else 'full'}",
        )
        session.commit()
        return serialize_import_job(session=session, job=job)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
