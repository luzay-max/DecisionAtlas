from __future__ import annotations

import httpx

from app.ingest.github_client import GitHubClient


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
