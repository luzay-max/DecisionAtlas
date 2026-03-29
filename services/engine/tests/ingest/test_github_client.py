from __future__ import annotations

from datetime import datetime
import httpx

from app.ingest.github_client import GitHubClient, GitHubNetworkError


def test_fetch_issues_skips_pull_requests() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/issues"):
            return httpx.Response(
                200,
                json=[
                    {
                        "id": 1,
                        "number": 10,
                        "title": "Issue title",
                        "body": "Issue body",
                        "user": {"login": "alice"},
                        "html_url": "https://github.com/org/repo/issues/10",
                        "state": "open",
                        "created_at": "2026-03-18T00:00:00Z",
                    },
                    {
                        "id": 2,
                        "title": "Should be skipped",
                        "pull_request": {},
                    },
                ],
            )
        return httpx.Response(200, json=[])

    client = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"))

    issues = client.fetch_issues("org/repo")

    assert len(issues) == 1
    assert issues[0].artifact_type == "issue"
    assert issues[0].author == "alice"


def test_fetch_pull_requests_maps_content() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/pulls"):
            return httpx.Response(
                200,
                json=[
                    {
                        "id": 3,
                        "number": 99,
                        "title": "Add API route",
                        "body": "Implements the importer route",
                        "user": {"login": "bob"},
                        "html_url": "https://github.com/org/repo/pull/99",
                        "state": "open",
                        "created_at": "2026-03-18T00:00:00Z",
                    }
                ],
            )
        return httpx.Response(200, json=[])

    client = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"))

    pulls = client.fetch_pull_requests("org/repo")

    assert len(pulls) == 1
    assert pulls[0].artifact_type == "pr"
    assert "Add API route" in pulls[0].content


def test_fetch_commits_maps_commit_message() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/commits"):
            return httpx.Response(
                200,
                json=[
                    {
                        "sha": "abc123",
                        "html_url": "https://github.com/org/repo/commit/abc123",
                        "author": {"login": "carol"},
                        "commit": {
                            "message": "Add importer\n\nDetailed body",
                            "author": {"date": "2026-03-18T00:00:00Z", "name": "Carol"},
                        },
                    }
                ],
            )
        return httpx.Response(200, json=[])

    client = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"))

    commits = client.fetch_commits("org/repo")

    assert len(commits) == 1
    assert commits[0].artifact_type == "commit"
    assert commits[0].title == "Add importer"
    assert commits[0].author == "carol"


def test_client_works_without_token_for_public_repo() -> None:
    captured_auth_headers: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_auth_headers.append(request.headers.get("Authorization"))
        return httpx.Response(200, json=[])

    client = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"))

    client.fetch_issues("org/repo")

    assert captured_auth_headers == [None]


def test_fetch_commits_forwards_since_parameter() -> None:
    captured_since: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_since.append(request.url.params.get("since"))
        return httpx.Response(200, json=[])

    client = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"))

    client.fetch_commits("org/repo", since=GitHubClient._parse_datetime("2026-03-18T00:00:00Z"))

    assert captured_since == ["2026-03-18T00:00:00+00:00"]


def test_paginate_stops_without_next_link_even_when_page_is_full() -> None:
    request_pages: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        request_pages.append(request.url.params.get("page"))
        return httpx.Response(
            200,
            json=[{"id": index} for index in range(100)],
        )

    client = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"))

    client.fetch_issues("org/repo")

    assert request_pages == ["1"]


def test_paginate_tolerates_out_of_range_422_on_late_page() -> None:
    request_pages: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        page = request.url.params.get("page")
        request_pages.append(page)
        if page == "1":
            return httpx.Response(
                200,
                headers={"Link": '<https://api.github.com/repos/org/repo/issues?per_page=100&page=2>; rel="next"'},
                json=[
                    {
                        "id": 1,
                        "number": 10,
                        "title": "Issue title",
                        "body": "Issue body",
                        "user": {"login": "alice"},
                        "html_url": "https://github.com/org/repo/issues/10",
                        "state": "open",
                        "created_at": "2026-03-18T00:00:00Z",
                    }
                ],
            )
        return httpx.Response(422, json={"message": "Validation Failed"})

    client = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"))

    issues = client.fetch_issues("org/repo")

    assert len(issues) == 1
    assert request_pages == ["1", "2"]


def test_paginate_respects_max_pages_limit() -> None:
    request_pages: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        request_pages.append(request.url.params.get("page"))
        page = int(request.url.params.get("page", "1"))
        next_page = page + 1
        return httpx.Response(
            200,
            headers={"Link": f'<https://api.github.com/repos/org/repo/issues?per_page=100&page={next_page}>; rel="next"'},
            json=[
                {
                    "id": page,
                    "number": page,
                    "title": f"Issue {page}",
                    "body": "Issue body",
                    "user": {"login": "alice"},
                    "html_url": f"https://github.com/org/repo/issues/{page}",
                    "state": "open",
                    "created_at": "2026-03-18T00:00:00Z",
                }
            ],
        )

    client = GitHubClient(
        max_pages=3,
        client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"),
    )

    issues = client.fetch_issues("org/repo")

    assert len(issues) == 3
    assert request_pages == ["1", "2", "3"]


def test_fetch_markdown_document_falls_back_to_download_url_for_non_base64_content() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "api.github.com":
            return httpx.Response(
                200,
                json={
                    "name": "CHANGELOG.md",
                    "path": "CHANGELOG.md",
                    "encoding": "none",
                    "content": "",
                    "download_url": "https://raw.githubusercontent.com/org/repo/main/CHANGELOG.md",
                },
            )
        if request.url.host == "raw.githubusercontent.com":
            return httpx.Response(200, text="# Changelog\n\nLarge markdown body")
        raise AssertionError(f"Unexpected request: {request.url}")

    client = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"))

    content = client.fetch_markdown_document("org/repo", path="CHANGELOG.md", ref="main")

    assert content == "# Changelog\n\nLarge markdown body"


def test_fetch_pull_requests_accepts_naive_since_datetime() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/pulls"):
            return httpx.Response(
                200,
                json=[
                    {
                        "id": 1,
                        "number": 10,
                        "title": "Old change",
                        "body": "already synced",
                        "user": {"login": "alice"},
                        "html_url": "https://github.com/org/repo/pull/10",
                        "state": "closed",
                        "created_at": "2026-03-18T00:00:00Z",
                        "updated_at": "2026-03-18T00:00:00Z",
                    },
                    {
                        "id": 2,
                        "number": 11,
                        "title": "New change",
                        "body": "needs sync",
                        "user": {"login": "bob"},
                        "html_url": "https://github.com/org/repo/pull/11",
                        "state": "open",
                        "created_at": "2026-03-19T00:00:00Z",
                        "updated_at": "2026-03-19T00:00:00Z",
                    },
                ],
            )
        return httpx.Response(200, json=[])

    client = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"))

    pulls = client.fetch_pull_requests("org/repo", since=datetime(2026, 3, 18, 12, 0, 0))

    assert len(pulls) == 1
    assert pulls[0].title == "New change"


def test_transport_failure_retries_and_recovers() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise httpx.ConnectError("temporary network failure", request=request)
        return httpx.Response(200, json=[])

    client = GitHubClient(
        transport_retry_attempts=2,
        transport_retry_backoff_seconds=0,
        client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"),
    )

    issues = client.fetch_issues("org/repo")

    assert issues == []
    assert attempts == 2


def test_transport_failure_exhaustion_raises_network_error() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ReadTimeout("request timed out", request=request)

    client = GitHubClient(
        transport_retry_attempts=2,
        transport_retry_backoff_seconds=0,
        client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"),
    )

    try:
        client.fetch_issues("org/repo")
    except GitHubNetworkError as exc:
        assert "transport attempts" in str(exc)
    else:
        raise AssertionError("expected GitHubNetworkError")

    assert attempts == 3


def test_repository_access_error_is_not_retried() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(404, json={"message": "Not Found"})

    client = GitHubClient(
        transport_retry_attempts=2,
        transport_retry_backoff_seconds=0,
        client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"),
    )

    try:
        client.fetch_issues("org/repo")
    except httpx.HTTPStatusError as exc:
        assert exc.response.status_code == 404
    else:
        raise AssertionError("expected HTTPStatusError")

    assert attempts == 1
