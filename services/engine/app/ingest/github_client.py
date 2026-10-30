from __future__ import annotations

import base64
from datetime import datetime, timezone
from time import sleep
from typing import Any
from urllib.parse import unquote, urlsplit

import httpx

from app.ingest.github_types import GitHubArtifactPayload, GitHubRepositoryFile


class GitHubNetworkError(Exception):
    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.__cause__ = cause


class GitHubClient:
    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str = "https://api.github.com",
        max_pages: int = 5,
        transport_retry_attempts: int = 2,
        transport_retry_backoff_seconds: float = 0.5,
        client: httpx.Client | None = None,
    ) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "DecisionAtlas"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        self.base_url = base_url.rstrip("/")
        self.max_pages = max_pages
        self.transport_retry_attempts = max(0, transport_retry_attempts)
        self.transport_retry_backoff_seconds = max(0.0, transport_retry_backoff_seconds)
        self.client = client or httpx.Client(base_url=self.base_url, headers=headers, timeout=30.0)

    def fetch_issues(self, repo: str, *, since: datetime | None = None) -> list[GitHubArtifactPayload]:
        normalized_since = self._normalize_since(since)
        params: dict[str, Any] = {"state": "all"}
        if normalized_since is not None:
            params["since"] = normalized_since.isoformat()
        items = self._paginate(f"/repos/{repo}/issues", params=params)
        issues: list[GitHubArtifactPayload] = []
        for item in items:
            if "pull_request" in item:
                continue
            issues.append(
                GitHubArtifactPayload(
                    artifact_type="issue",
                    source_id=str(item["id"]),
                    repo=repo,
                    title=item.get("title"),
                    content=item.get("body") or "",
                    author=(item.get("user") or {}).get("login"),
                    url=item.get("html_url"),
                    timestamp=self._parse_datetime(item.get("created_at")),
                    metadata_json={
                        "source_metadata_origin": "github_api",
                        "number": item.get("number"),
                        "state": item.get("state"),
                        "updated_at": item.get("updated_at"),
                        "closed_at": item.get("closed_at"),
                    },
                )
            )
        return issues

    def fetch_pull_requests(self, repo: str, *, since: datetime | None = None) -> list[GitHubArtifactPayload]:
        normalized_since = self._normalize_since(since)
        items = self._paginate(
            f"/repos/{repo}/pulls",
            params={"state": "all", "sort": "updated", "direction": "desc"},
        )
        pulls: list[GitHubArtifactPayload] = []
        for item in items:
            updated_at = self._parse_datetime(item.get("updated_at") or item.get("created_at"))
            if normalized_since is not None and updated_at is not None and updated_at <= normalized_since:
                continue
            content = "\n\n".join(part for part in [item.get("title"), item.get("body") or ""] if part)
            pulls.append(
                GitHubArtifactPayload(
                    artifact_type="pr",
                    source_id=str(item["id"]),
                    repo=repo,
                    title=item.get("title"),
                    content=content,
                    author=(item.get("user") or {}).get("login"),
                    url=item.get("html_url"),
                    timestamp=self._parse_datetime(item.get("created_at")),
                    metadata_json={
                        "source_metadata_origin": "github_api",
                        "number": item.get("number"),
                        "state": item.get("state"),
                        "updated_at": item.get("updated_at"),
                        "merged_at": item.get("merged_at"),
                        "merge_state_observed": "github_api" if "merged_at" in item else "unknown",
                        "merged": (item.get("merged_at") is not None) if "merged_at" in item else None,
                        "merge_commit_sha": item.get("merge_commit_sha"),
                        "head_sha": (item.get("head") or {}).get("sha"),
                        "base_ref": (item.get("base") or {}).get("ref"),
                    },
                )
            )
        return pulls

    def fetch_commits(self, repo: str, *, since: datetime | None = None) -> list[GitHubArtifactPayload]:
        normalized_since = self._normalize_since(since)
        params: dict[str, Any] = {}
        if normalized_since is not None:
            params["since"] = normalized_since.isoformat()
        items = self._paginate(f"/repos/{repo}/commits", params=params or None)
        commits: list[GitHubArtifactPayload] = []
        for item in items:
            commit = item.get("commit") or {}
            author = (item.get("author") or {}).get("login") or ((commit.get("author") or {}).get("name"))
            commits.append(
                GitHubArtifactPayload(
                    artifact_type="commit",
                    source_id=item.get("sha"),
                    repo=repo,
                    title=(commit.get("message") or "").splitlines()[0] if commit.get("message") else None,
                    content=commit.get("message") or "",
                    author=author,
                    url=item.get("html_url"),
                    timestamp=self._parse_datetime((commit.get("author") or {}).get("date")),
                    metadata_json={
                        "source_metadata_origin": "github_api",
                        "commit_sha": item.get("sha"),
                        "committer_date": self._parse_datetime((commit.get("committer") or {}).get("date")).isoformat()
                        if self._parse_datetime((commit.get("committer") or {}).get("date")) else None,
                    },
                )
            )
        return commits

    def get_default_branch(self, repo: str) -> str:
        response = self._get(f"/repos/{repo}")
        response.raise_for_status()
        payload = response.json()
        return payload.get("default_branch") or "main"

    def get_repository_metadata(self, repo: str) -> dict[str, Any]:
        response = self._get(f"/repos/{repo}")
        response.raise_for_status()
        payload = response.json()
        return {
            "full_name": payload.get("full_name") or repo,
            "private": bool(payload.get("private")),
            "default_branch": payload.get("default_branch") or "main",
        }

    def list_repository_files(self, repo: str, *, ref: str | None = None) -> list[GitHubRepositoryFile]:
        branch = ref or self.get_default_branch(repo)
        response = self._get(f"/repos/{repo}/git/trees/{branch}", params={"recursive": "1"})
        response.raise_for_status()
        payload = response.json()
        tree = payload.get("tree") or []
        return [
            GitHubRepositoryFile(
                path=item["path"],
                sha=item.get("sha"),
                size=item.get("size"),
            )
            for item in tree
            if item.get("type") == "blob" and item.get("path")
        ]

    def fetch_markdown_document(self, repo: str, *, path: str, ref: str) -> str:
        response = self._get(f"/repos/{repo}/contents/{path}", params={"ref": ref})
        response.raise_for_status()
        payload = response.json()
        encoded = payload.get("content")
        encoding = payload.get("encoding")
        if encoded and encoding == "base64":
            return base64.b64decode(encoded).decode("utf-8")

        # Prefer the authenticated Contents API raw media type. Unlike a
        # cross-origin download URL, this also works for private repositories
        # without sending their token to another host.
        raw_response = self._get(
            f"/repos/{repo}/contents/{path}",
            params={"ref": ref},
            headers={"Accept": "application/vnd.github.raw+json"},
        )
        if raw_response.is_redirect:
            raise ValueError("GitHub raw content API redirected unexpectedly")
        raw_response.raise_for_status()
        if "json" not in raw_response.headers.get("content-type", "").lower():
            return raw_response.text

        # Some API proxies/fixtures ignore Accept and send the same object.
        # Fall back to the explicitly validated, unauthenticated public URL
        # only if the raw media response is still a Contents metadata object.
        try:
            raw_payload = raw_response.json()
        except ValueError as exc:
            raise ValueError(
                f"GitHub raw content API returned malformed JSON for {path}"
            ) from exc
        if not isinstance(raw_payload, dict) or "encoding" not in raw_payload:
            # Some API gateways return a 200 OK with an error JSON object.
            # Never index this response as source Markdown.
            raise ValueError(
                f"GitHub raw content API returned unexpected JSON for {path}"
            )
        if raw_payload.get("encoding") == "base64" and raw_payload.get("content"):
            return base64.b64decode(raw_payload["content"]).decode("utf-8")

        download_url = payload.get("download_url")
        if isinstance(download_url, str) and download_url:
            return self._fetch_public_markdown_download(download_url, repo=repo, path=path)

        raise ValueError(f"Unsupported GitHub content encoding for {path}")

    def _fetch_public_markdown_download(self, download_url: str, *, repo: str, path: str) -> str:
        """Fetch public raw content without forwarding GitHub API credentials.

        Content-API download_url is upstream-controlled. A cross-origin GET
        through the authenticated API client must never inherit its token.
        """
        try:
            parsed = urlsplit(download_url)
            # Verify the *requested file*, not only the repo prefix. URL
            # percent-encoding otherwise hides "..", "/" and nested escapes
            # from a check against raw path segments. Do not resolve
            # ambiguous paths: failing closed is safer than misattributing
            # arbitrary upstream content to the requested Artifact.
            segments = [unquote(part) for part in parsed.path.split("/")[1:]]
            repo_segments = repo.split("/")
            file_segments = path.split("/")
            trustworthy_segments = (
                len(segments) > len(repo_segments) + len(file_segments)
                and segments[:len(repo_segments)] == repo_segments
                and segments[-len(file_segments):] == file_segments
                and all(
                    part not in {"", ".", ".."}
                    and "/" not in part
                    and "\\" not in part
                    and "%" not in part
                    for part in segments
                )
            )
            trusted = (
                parsed.scheme == "https"
                and parsed.hostname == "raw.githubusercontent.com"
                and parsed.username is None
                and parsed.password is None
                and parsed.port in (None, 443)
                and not parsed.netloc.endswith(":")
                and not parsed.query
                and not parsed.fragment
                and trustworthy_segments
            )
        except ValueError:
            trusted = False
        if not trusted:
            raise ValueError("GitHub raw content download URL is not trusted")

        # build_request merges client defaults, so explicitly strip credentials
        # and override client-level auth before sending. Redirects must not be
        # followed to another host.
        request = self.client.build_request("GET", download_url)
        request.headers.pop("Authorization", None)
        request.headers.pop("Cookie", None)
        response = self.client.send(request, auth=httpx.Auth(), follow_redirects=False)
        if response.is_redirect:
            raise ValueError("GitHub raw content download redirected unexpectedly")
        response.raise_for_status()
        return response.text

    def _paginate(self, path: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        page = 1
        results: list[dict[str, Any]] = []
        while True:
            if page > self.max_pages:
                break
            request_params = {"per_page": 100, "page": page}
            if params:
                request_params.update(params)
            response = self._get(path, params=request_params)
            if response.status_code == 422 and page > 1:
                break
            response.raise_for_status()
            payload = response.json()
            if not payload:
                break
            results.extend(payload)
            if "next" not in response.links:
                break
            page += 1
        return results

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @staticmethod
    def _normalize_since(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _get(
        self, path: str, *, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None
    ) -> httpx.Response:
        attempts = self.transport_retry_attempts + 1
        for attempt in range(1, attempts + 1):
            try:
                return self.client.get(path, params=params, headers=headers, follow_redirects=False)
            except (httpx.ConnectError, httpx.ReadError, httpx.ReadTimeout, httpx.RemoteProtocolError) as exc:
                if attempt >= attempts:
                    raise GitHubNetworkError(
                        f"GitHub request failed after {attempts} transport attempts",
                        cause=exc,
                    ) from exc
                if self.transport_retry_backoff_seconds > 0:
                    sleep(self.transport_retry_backoff_seconds * attempt)
        raise AssertionError("unreachable")
