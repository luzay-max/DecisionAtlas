from __future__ import annotations

import base64
from datetime import datetime
from typing import Any

import httpx

from app.ingest.github_types import GitHubArtifactPayload, GitHubRepositoryFile


class GitHubClient:
    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str = "https://api.github.com",
        max_pages: int = 5,
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
        self.client = client or httpx.Client(base_url=self.base_url, headers=headers, timeout=30.0)

    def fetch_issues(self, repo: str, *, since: datetime | None = None) -> list[GitHubArtifactPayload]:
        params: dict[str, Any] = {"state": "all"}
        if since is not None:
            params["since"] = since.isoformat()
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
                    metadata_json={"number": item.get("number"), "state": item.get("state")},
                )
            )
        return issues

    def fetch_pull_requests(self, repo: str, *, since: datetime | None = None) -> list[GitHubArtifactPayload]:
        items = self._paginate(
            f"/repos/{repo}/pulls",
            params={"state": "all", "sort": "updated", "direction": "desc"},
        )
        pulls: list[GitHubArtifactPayload] = []
        for item in items:
            updated_at = self._parse_datetime(item.get("updated_at") or item.get("created_at"))
            if since is not None and updated_at is not None and updated_at <= since:
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
                    metadata_json={"number": item.get("number"), "state": item.get("state")},
                )
            )
        return pulls

    def fetch_commits(self, repo: str, *, since: datetime | None = None) -> list[GitHubArtifactPayload]:
        params: dict[str, Any] = {}
        if since is not None:
            params["since"] = since.isoformat()
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
                    metadata_json={},
                )
            )
        return commits

    def get_default_branch(self, repo: str) -> str:
        response = self.client.get(f"/repos/{repo}")
        response.raise_for_status()
        payload = response.json()
        return payload.get("default_branch") or "main"

    def list_repository_files(self, repo: str, *, ref: str | None = None) -> list[GitHubRepositoryFile]:
        branch = ref or self.get_default_branch(repo)
        response = self.client.get(f"/repos/{repo}/git/trees/{branch}", params={"recursive": "1"})
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
        response = self.client.get(f"/repos/{repo}/contents/{path}", params={"ref": ref})
        response.raise_for_status()
        payload = response.json()
        encoded = payload.get("content")
        encoding = payload.get("encoding")
        if not encoded or encoding != "base64":
            raise ValueError(f"Unsupported GitHub content encoding for {path}")
        return base64.b64decode(encoded).decode("utf-8")

    def _paginate(self, path: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        page = 1
        results: list[dict[str, Any]] = []
        while True:
            if page > self.max_pages:
                break
            request_params = {"per_page": 100, "page": page}
            if params:
                request_params.update(params)
            response = self.client.get(path, params=request_params)
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
