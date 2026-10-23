"""Read-only GitLab.com and Gitee.com source clients.

Provider normalization matches the existing GitHubImporter input contract.
This layer deliberately does NOT bind credentials or schedule import jobs.
It only allows the official public API hosts until a separate, reviewed
private/self-hosted access-source design is available.
"""
from __future__ import annotations

import base64
import binascii
import re
from datetime import datetime, timezone
from urllib.parse import quote

import httpx

from app.ingest.github_types import GitHubArtifactPayload, GitHubRepositoryFile


class GitProviderError(ValueError):
    """A sanitized provider failure, safe to return to an operator."""


_REPO_PART = re.compile(r"^[A-Za-z0-9_.-]+$")


def _validate_repo(repo: str, *, nested: bool) -> str:
    if not repo or repo.strip() != repo:
        raise GitProviderError("Invalid repository identifier")
    parts = repo.split("/")
    if len(parts) < 2 or (not nested and len(parts) != 2):
        raise GitProviderError("Expected owner/repo or namespace/repo")
    if any(part in {".", ".."} or not _REPO_PART.fullmatch(part) for part in parts):
        raise GitProviderError("Invalid repository identifier")
    return repo


def _safe_file_path(path: str) -> str:
    if not path or path.startswith("/") or "\\" in path or "\0" in path:
        raise GitProviderError("Invalid repository file path")
    if any(part in {".", "..", ""} for part in path.split("/")):
        raise GitProviderError("Invalid repository file path")
    return path


def _time(value: str | None) -> datetime | None:
    if not value:
        return None
    timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return timestamp.replace(tzinfo=timezone.utc) if timestamp.tzinfo is None else timestamp


def _since_filter(value: str | None, since: datetime | None) -> bool:
    if since is None:
        return True
    date = _time(value)
    threshold = since.replace(tzinfo=timezone.utc) if since.tzinfo is None else since
    return date is None or date > threshold


class _PublicProviderClient:
    def __init__(
        self, *,
        base_url: str,
        max_pages: int = 5,
        client: httpx.Client | None = None,
    ) -> None:
        if max_pages < 1 or max_pages > 100:
            raise ValueError("max_pages must be between 1 and 100")
        self.max_pages = max_pages
        self.client = client or httpx.Client(
            base_url=base_url,
            headers={"Accept": "application/json", "User-Agent": "DecisionAtlas"},
            timeout=20.0,
            follow_redirects=False,
        )

    def _get(self, path: str, params: dict | None = None) -> httpx.Response:
        try:
            response = self.client.get(path, params=params)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            code = exc.response.status_code
            if code == 404:
                raise GitProviderError("Repository resource not found") from None
            if code in {401, 403}:
                raise GitProviderError("Provider authorization required or access denied") from None
            if code == 429:
                raise GitProviderError("Provider rate limit reached") from None
            raise GitProviderError(f"Provider request failed (HTTP {code})") from None
        except httpx.RequestError:
            raise GitProviderError("Provider network request failed") from None

    def _pages(self, path: str, params: dict | None = None) -> list[dict]:
        output: list[dict] = []
        for page in range(1, self.max_pages + 1):
            res = self._get(path, {**(params or {}), "page": page, "per_page": 100})
            items = res.json()
            if not isinstance(items, list):
                raise GitProviderError("Unexpected provider list response")
            output.extend(items)
            if len(items) < 100:
                return output
        raise GitProviderError("Provider pagination limit reached; increase max_pages explicitly")


class GitLabClient(_PublicProviderClient):
    """Public GitLab.com reader. Self-managed and private access require a separate gate."""

    def __init__(self, *, max_pages: int = 5, client: httpx.Client | None = None) -> None:
        super().__init__(base_url="https://gitlab.com/api/v4", max_pages=max_pages, client=client)

    @staticmethod
    def _project(repo: str) -> str:
        return quote(_validate_repo(repo, nested=True), safe="")

    def get_repository_metadata(self, repo: str) -> dict:
        return self._get(f"/projects/{self._project(repo)}").json()

    def get_default_branch(self, repo: str) -> str:
        branch = self.get_repository_metadata(repo).get("default_branch")
        if not isinstance(branch, str) or not branch:
            raise GitProviderError("Repository has no default branch")
        return branch

    def fetch_issues(self, repo: str, *, since: datetime | None = None) -> list[GitHubArtifactPayload]:
        output = []
        for item in self._pages(f"/projects/{self._project(repo)}/issues", {"scope": "all", "state": "all", "order_by": "updated_at", "sort": "desc"}):
            if not _since_filter(item.get("updated_at"), since):
                continue
            output.append(GitHubArtifactPayload(
                artifact_type="issue", source_id=f"gitlab:issue:{item['id']}", repo=repo,
                title=item.get("title"), content=item.get("description") or "",
                author=(item.get("author") or {}).get("username"),
                url=item.get("web_url"), timestamp=_time(item.get("created_at")),
                metadata_json={"provider": "gitlab", "number": item.get("iid"), "state": item.get("state")},
            ))
        return output

    def fetch_pull_requests(self, repo: str, *, since: datetime | None = None) -> list[GitHubArtifactPayload]:
        output = []
        for item in self._pages(f"/projects/{self._project(repo)}/merge_requests", {"scope": "all", "state": "all", "order_by": "updated_at", "sort": "desc"}):
            if not _since_filter(item.get("updated_at"), since):
                continue
            output.append(GitHubArtifactPayload(
                artifact_type="pr", source_id=f"gitlab:mr:{item['id']}", repo=repo,
                title=item.get("title"),
                content="\n\n".join(part for part in [item.get("title"), item.get("description")] if part),
                author=(item.get("author") or {}).get("username"),
                url=item.get("web_url"), timestamp=_time(item.get("created_at")),
                metadata_json={"provider": "gitlab", "number": item.get("iid"), "state": item.get("state"),
                               "merged_at": item.get("merged_at"), "source_kind": "merge_request"},
            ))
        return output

    def fetch_commits(self, repo: str, *, since: datetime | None = None) -> list[GitHubArtifactPayload]:
        params = {"since": since.isoformat()} if since is not None else None
        output = []
        for item in self._pages(f"/projects/{self._project(repo)}/repository/commits", params):
            message = item.get("message") or ""
            output.append(GitHubArtifactPayload(
                artifact_type="commit", source_id=f"gitlab:commit:{item['id']}", repo=repo,
                title=message.splitlines()[0] if message else None,
                content=message, author=item.get("author_name"), url=item.get("web_url"),
                timestamp=_time(item.get("authored_date")),
                metadata_json={"provider": "gitlab", "sha": item.get("id")},
            ))
        return output

    def list_repository_files(self, repo: str, *, ref: str | None = None) -> list[GitHubRepositoryFile]:
        chosen = ref or self.get_default_branch(repo)
        files = self._pages(f"/projects/{self._project(repo)}/repository/tree", {"recursive": "true", "ref": chosen})
        return [GitHubRepositoryFile(path=item["path"], sha=item.get("id"), size=None)
                for item in files if item.get("type") == "blob"]

    def fetch_markdown_document(self, repo: str, *, path: str, ref: str) -> str:
        safe_path = quote(_safe_file_path(path), safe="")
        return self._get(f"/projects/{self._project(repo)}/repository/files/{safe_path}/raw", {"ref": ref}).text


class GiteeClient(_PublicProviderClient):
    """Public Gitee.com reader, using the provider's official v5 API."""

    def __init__(self, *, max_pages: int = 5, client: httpx.Client | None = None) -> None:
        super().__init__(base_url="https://gitee.com/api/v5", max_pages=max_pages, client=client)

    @staticmethod
    def _repo(repo: str) -> str:
        return _validate_repo(repo, nested=False)

    def get_repository_metadata(self, repo: str) -> dict:
        return self._get(f"/repos/{self._repo(repo)}").json()

    def get_default_branch(self, repo: str) -> str:
        branch = self.get_repository_metadata(repo).get("default_branch")
        if not isinstance(branch, str) or not branch:
            raise GitProviderError("Repository has no default branch")
        return branch

    def fetch_issues(self, repo: str, *, since: datetime | None = None) -> list[GitHubArtifactPayload]:
        output = []
        for item in self._pages(f"/repos/{self._repo(repo)}/issues", {"state": "all", "sort": "updated", "direction": "desc"}):
            if not _since_filter(item.get("updated_at"), since):
                continue
            output.append(GitHubArtifactPayload(
                artifact_type="issue", source_id=f"gitee:issue:{item['id']}", repo=repo,
                title=item.get("title"), content=item.get("body") or "",
                author=(item.get("user") or {}).get("login"),
                url=item.get("html_url"), timestamp=_time(item.get("created_at")),
                metadata_json={"provider": "gitee", "number": item.get("number"), "state": item.get("state")},
            ))
        return output

    def fetch_pull_requests(self, repo: str, *, since: datetime | None = None) -> list[GitHubArtifactPayload]:
        output = []
        for item in self._pages(f"/repos/{self._repo(repo)}/pulls", {"state": "all", "sort": "updated", "direction": "desc"}):
            if not _since_filter(item.get("updated_at"), since):
                continue
            output.append(GitHubArtifactPayload(
                artifact_type="pr", source_id=f"gitee:pr:{item['id']}", repo=repo,
                title=item.get("title"),
                content="\n\n".join(part for part in [item.get("title"), item.get("body")] if part),
                author=(item.get("user") or {}).get("login"),
                url=item.get("html_url"), timestamp=_time(item.get("created_at")),
                metadata_json={"provider": "gitee", "number": item.get("number"), "state": item.get("state"),
                               "merged": item.get("merged"), "merged_at": item.get("merged_at")},
            ))
        return output

    def fetch_commits(self, repo: str, *, since: datetime | None = None) -> list[GitHubArtifactPayload]:
        output = []
        for item in self._pages(f"/repos/{self._repo(repo)}/commits"):
            commit = item.get("commit") or {}
            when = (commit.get("author") or {}).get("date")
            if not _since_filter(when, since):
                continue
            message = commit.get("message") or ""
            output.append(GitHubArtifactPayload(
                artifact_type="commit", source_id=f"gitee:commit:{item['sha']}", repo=repo,
                title=message.splitlines()[0] if message else None, content=message,
                author=(item.get("author") or {}).get("login") or (commit.get("author") or {}).get("name"),
                url=item.get("html_url"), timestamp=_time(when),
                metadata_json={"provider": "gitee", "sha": item.get("sha")},
            ))
        return output

    def list_repository_files(self, repo: str, *, ref: str | None = None) -> list[GitHubRepositoryFile]:
        chosen = ref or self.get_default_branch(repo)
        _validate_repo(repo, nested=False)
        result = self._get(f"/repos/{repo}/git/trees/{quote(chosen, safe='')}", {"recursive": 1}).json()
        if result.get("truncated"):
            raise GitProviderError("Provider repository tree is truncated")
        return [GitHubRepositoryFile(path=item["path"], sha=item.get("sha"), size=item.get("size"))
                for item in result.get("tree", []) if item.get("type") == "blob"]

    def fetch_markdown_document(self, repo: str, *, path: str, ref: str) -> str:
        _validate_repo(repo, nested=False)
        safe_path = quote(_safe_file_path(path), safe="/")
        item = self._get(f"/repos/{repo}/contents/{safe_path}", {"ref": ref}).json()
        if item.get("encoding") != "base64" or not isinstance(item.get("content"), str):
            raise GitProviderError("Unexpected repository content encoding")
        try:
            return base64.b64decode(item["content"], validate=False).decode("utf-8")
        except (binascii.Error, ValueError, UnicodeDecodeError) as exc:
            raise GitProviderError("Invalid repository document contents") from None
