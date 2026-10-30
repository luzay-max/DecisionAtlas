from __future__ import annotations

from datetime import datetime
import httpx
import pytest

from app.ingest.github_client import GitHubClient, GitHubIncompleteCoverageError, GitHubNetworkError


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
    assert issues[0].metadata_json["source_metadata_origin"] == "github_api"
    assert issues[0].metadata_json["number"] == 10
    assert issues[0].metadata_json["state"] == "open"


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
    assert pulls[0].metadata_json["merge_state_observed"] == "unknown"
    assert pulls[0].metadata_json["merged"] is None



def test_fetch_pull_requests_preserves_observed_merge_metadata() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/pulls"):
            return httpx.Response(
                200,
                json=[
                    {
                        "id": 4,
                        "number": 100,
                        "title": "Merged feature",
                        "body": "Decision rationale",
                        "user": {"login": "reviewer"},
                        "html_url": "https://github.com/org/repo/pull/100",
                        "state": "closed",
                        "created_at": "2026-03-18T00:00:00Z",
                        "updated_at": "2026-03-19T00:00:00Z",
                        "merged_at": "2026-03-19T00:00:00Z",
                        "merge_commit_sha": "a" * 40,
                        "head": {"sha": "b" * 40},
                        "base": {"ref": "main"},
                    }
                ],
            )
        return httpx.Response(200, json=[])

    client = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"))
    pull = client.fetch_pull_requests("org/repo")[0]

    assert pull.metadata_json["source_metadata_origin"] == "github_api"
    assert pull.metadata_json["number"] == 100
    assert pull.metadata_json["state"] == "closed"
    assert pull.metadata_json["merge_state_observed"] == "github_api"
    assert pull.metadata_json["merged"] is True
    assert pull.metadata_json["merged_at"] == "2026-03-19T00:00:00Z"
    assert pull.metadata_json["merge_commit_sha"] == "a" * 40
    assert pull.metadata_json["head_sha"] == "b" * 40
    assert pull.metadata_json["base_ref"] == "main"


def test_fetch_pull_requests_preserves_explicit_unmerged_state() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/pulls"):
            return httpx.Response(
                200,
                json=[
                    {
                        "id": 5,
                        "number": 101,
                        "title": "Unmerged proposal",
                        "body": "Not adopted",
                        "user": {"login": "reviewer"},
                        "html_url": "https://github.com/org/repo/pull/101",
                        "state": "closed",
                        "created_at": "2026-03-18T00:00:00Z",
                        "updated_at": "2026-03-19T00:00:00Z",
                        "merged_at": None,
                        "merge_commit_sha": None,
                        "head": {"sha": "d" * 40},
                        "base": {"ref": "main"},
                    }
                ],
            )
        return httpx.Response(200, json=[])

    client = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"))
    pull = client.fetch_pull_requests("org/repo")[0]

    assert pull.metadata_json["merge_state_observed"] == "github_api"
    assert pull.metadata_json["merged"] is False
    assert pull.metadata_json["merged_at"] is None
    assert pull.metadata_json["merge_commit_sha"] is None


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


def test_paginate_rejects_422_after_next_link_instead_of_claiming_complete() -> None:
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

    with pytest.raises(GitHubIncompleteCoverageError, match="pagination_rejected") as exc:
        client.fetch_issues("org/repo")

    assert exc.value.scope == "/repos/org/repo/issues"
    assert request_pages == ["1", "2"]


def test_paginate_fails_closed_at_max_pages_with_next_link() -> None:
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

    with pytest.raises(GitHubIncompleteCoverageError, match="page_limit") as exc:
        client.fetch_issues("org/repo")

    assert exc.value.scope == "/repos/org/repo/issues"
    assert request_pages == ["1", "2", "3"]




def test_tree_truncation_fails_before_document_selection() -> None:
    request_paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        request_paths.append(request.url.path)
        return httpx.Response(
            200,
            json={
                "sha": "abc",
                "truncated": True,
                "tree": [{"path": "docs/architecture.md", "type": "blob", "sha": "123"}],
            },
        )

    client = GitHubClient(client=httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    ))
    with pytest.raises(GitHubIncompleteCoverageError, match="tree_truncated") as exc:
        client.list_repository_files("org/repo", ref="main")

    assert exc.value.scope == "org/repo@main"
    assert request_paths == ["/repos/org/repo/git/trees/main"]


def test_complete_tree_and_last_page_without_next_link_remain_accepted() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/issues"):
            return httpx.Response(200, json=[{
                "id": 1,
                "number": 1,
                "title": "One issue",
                "body": "Content",
                "user": {"login": "maintainer"},
                "state": "open",
                "created_at": "2026-03-18T00:00:00Z",
            }])
        return httpx.Response(200, json={
            "truncated": False,
            "tree": [{"path": "docs/architecture.md", "type": "blob", "sha": "a" * 40, "size": 4}],
        })

    client = GitHubClient(max_pages=1, client=httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    ))
    assert len(client.fetch_issues("org/repo")) == 1
    assert [x.path for x in client.list_repository_files("org/repo", ref="main")] == [
        "docs/architecture.md"
    ]

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


def test_raw_markdown_fallback_never_forwards_client_auth_or_cookies() -> None:
    observed = {}

    def handler(request: httpx.Request) -> httpx.Response:
        observed[str(request.url.host)] = {
            "authorization": request.headers.get("Authorization"),
            "cookie": request.headers.get("Cookie"),
        }
        if request.url.host == "api.github.com":
            return httpx.Response(
                200,
                json={
                    "encoding": "none",
                    "content": "",
                    "download_url": "https://raw.githubusercontent.com/org/repo/main/CHANGELOG.md",
                },
            )
        if request.url.host == "raw.githubusercontent.com":
            return httpx.Response(200, text="# Safe raw content")
        raise AssertionError("Unexpected outbound request")

    transport = httpx.MockTransport(handler)
    client = GitHubClient(
        client=httpx.Client(
            transport=transport,
            base_url="https://api.github.com",
            auth=httpx.BasicAuth("private-user", "private-pass"),
            headers={"Cookie": "session=private-cookie"},
        )
    )
    assert client.fetch_markdown_document("org/repo", path="CHANGELOG.md", ref="main") == "# Safe raw content"
    assert observed["api.github.com"]["authorization"] is not None
    assert observed["api.github.com"]["cookie"] == "session=private-cookie"
    assert observed["raw.githubusercontent.com"] == {"authorization": None, "cookie": None}


def test_raw_markdown_fallback_rejects_untrusted_host_before_request() -> None:
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        return httpx.Response(
            200,
            json={"encoding": "none", "download_url": "https://example.invalid/org/repo/main/README.md"},
        )

    client = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"))
    try:
        client.fetch_markdown_document("org/repo", path="README.md", ref="main")
    except ValueError as exc:
        assert "not trusted" in str(exc)
    else:
        raise AssertionError("Expected unsafe raw download to be blocked")
    assert len(requests) == 2


def test_raw_markdown_fallback_refuses_redirects() -> None:
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        if request.url.host == "api.github.com":
            return httpx.Response(
                200,
                json={"encoding": "none", "download_url": "https://raw.githubusercontent.com/org/repo/main/README.md"},
            )
        return httpx.Response(302, headers={"Location": "https://example.invalid/steal"})

    client = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"))
    try:
        client.fetch_markdown_document("org/repo", path="README.md", ref="main")
    except ValueError as exc:
        assert "redirected unexpectedly" in str(exc)
    else:
        raise AssertionError("Expected redirect to be blocked")
    assert len(requests) == 3


def test_raw_media_rejects_success_status_with_unexpected_json() -> None:
    observed: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(str(request.url))
        if len(observed) == 1:
            return httpx.Response(200, json={
                "encoding": "none",
                "content": "",
                "download_url": "https://raw.githubusercontent.com/org/repo/main/README.md",
            })
        if len(observed) == 2:
            # An API gateway/error proxy may return 200 with an error object.
            # It is not valid Markdown and must not become decision evidence.
            return httpx.Response(200, json={"message": "GitHub source unavailable"})
        raise AssertionError("Unexpected request after invalid source response")

    client = GitHubClient(client=httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    ))
    try:
        client.fetch_markdown_document("org/repo", path="README.md", ref="main")
    except ValueError as exc:
        assert "unexpected JSON" in str(exc)
    else:
        raise AssertionError("Expected unexpected raw JSON response to fail closed")
    assert len(observed) == 2
    assert all(url.startswith("https://api.github.com/") for url in observed)


def test_raw_media_rejects_malformed_json_response() -> None:
    requests: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        if len(requests) == 1:
            return httpx.Response(200, json={
                "encoding": "none",
                "download_url": "https://raw.githubusercontent.com/org/repo/main/README.md",
            })
        return httpx.Response(
            200, content=b"not-a-json-object",
            headers={"content-type": "application/json"},
        )

    client = GitHubClient(client=httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    ))
    try:
        client.fetch_markdown_document("org/repo", path="README.md", ref="main")
    except ValueError as exc:
        assert "malformed JSON" in str(exc)
    else:
        raise AssertionError("Expected malformed raw JSON response to fail closed")
    assert len(requests) == 2


def test_raw_media_fallback_keeps_private_token_on_github_api_only() -> None:
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append({
            "host": request.url.host,
            "accept": request.headers.get("Accept"),
            "authorization": request.headers.get("Authorization"),
        })
        if request.url.host != "api.github.com":
            raise AssertionError("No cross-origin request is needed for a private repository")
        if request.headers.get("Accept") == "application/vnd.github.raw+json":
            return httpx.Response(200, text="# Large private Markdown")
        return httpx.Response(
            200,
            json={
                "encoding": "none",
                "content": "",
                "download_url": "https://raw.githubusercontent.com/org/repo/main/private.md",
            },
        )

    client = GitHubClient(
        client=httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="https://api.github.com",
            auth=httpx.BasicAuth("private-user", "private-pass"),
        )
    )
    result = client.fetch_markdown_document("org/repo", path="private.md", ref="main")
    assert result == "# Large private Markdown"
    assert [row["host"] for row in seen] == ["api.github.com", "api.github.com"]
    assert seen[1]["accept"] == "application/vnd.github.raw+json"
    assert all(row["authorization"] is not None for row in seen)


def test_raw_media_fallback_does_not_follow_authenticated_redirects() -> None:
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.host)
        if request.headers.get("Accept") == "application/vnd.github.raw+json":
            return httpx.Response(302, headers={"Location": "https://example.invalid/steal"})
        return httpx.Response(200, json={"encoding": "none", "content": ""})

    client = GitHubClient(client=httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
        headers={"Authorization": "Bearer private-token"},
        follow_redirects=True,
    ))
    try:
        client.fetch_markdown_document("org/repo", path="README.md", ref="main")
    except ValueError as exc:
        assert "raw content API redirected" in str(exc)
    else:
        raise AssertionError("Expected authenticated cross-host redirect to be blocked")
    assert seen == ["api.github.com", "api.github.com"]


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


def test_get_repository_metadata_maps_private_flag() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "full_name": "org/private-repo",
                "private": True,
                "default_branch": "main",
            },
        )

    client = GitHubClient(client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com"))

    metadata = client.get_repository_metadata("org/private-repo")

    assert metadata == {
        "full_name": "org/private-repo",
        "private": True,
        "default_branch": "main",
    }


def test_streamed_public_raw_refuses_large_unknown_length_without_forwarding_auth() -> None:
    seen = []
    chunks_read = []

    def raw_chunks():
        for i in range(50):
            chunks_read.append(i)
            yield b"a" * 4096

    class RawStream(httpx.SyncByteStream):
        def __iter__(self):
            yield from raw_chunks()

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append((request.url.host, request.headers.get("authorization"), request.headers.get("cookie")))
        if request.url.host == "api.github.com":
            return httpx.Response(200, json={
                "encoding": "none",
                "content": "",
                "download_url": "https://raw.githubusercontent.com/org/repo/main/README.md",
            })
        return httpx.Response(200, stream=RawStream())

    client = GitHubClient(
        max_markdown_bytes=16 * 1024,
        client=httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="https://api.github.com",
            auth=httpx.BasicAuth("private-user", "private-password"),
            headers={"Cookie": "session=secret"},
        ),
    )
    with pytest.raises(GitHubIncompleteCoverageError, match="document_size_budget"):
        client.fetch_markdown_document("org/repo", path="README.md", ref="main")
    assert seen[-1] == ("raw.githubusercontent.com", None, None)
    assert len(chunks_read) < 50  # Stream aborted before the complete body arrived.


def test_streamed_private_raw_refuses_oversize_without_following_redirects() -> None:
    observed = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append((request.url.host, request.headers.get("accept"), request.headers.get("authorization")))
        if len(observed) == 1:
            return httpx.Response(200, json={
                "encoding": "none",
                "content": "",
                "download_url": "https://raw.githubusercontent.com/org/repo/main/private.md",
            })
        return httpx.Response(
            200, content=b"x" * 4096, headers={"content-type": "text/plain"}
        )

    client = GitHubClient(
        max_markdown_bytes=1024,
        client=httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="https://api.github.com",
            auth=httpx.BasicAuth("private-user", "private-password"),
        ),
    )
    with pytest.raises(GitHubIncompleteCoverageError, match="document_size_budget"):
        client.fetch_markdown_document("org/repo", path="private.md", ref="main")
    assert [host for host, _, _ in observed] == ["api.github.com", "api.github.com"]
    assert all(auth is not None for _, _, auth in observed)


def test_streamed_contents_base64_enforces_decoded_document_size() -> None:
    import base64 as base64_library

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "encoding": "base64",
            "content": base64_library.b64encode(b"123456789").decode("ascii"),
        })

    client = GitHubClient(
        max_markdown_bytes=8,
        client=httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="https://api.github.com",
        ),
    )
    with pytest.raises(GitHubIncompleteCoverageError, match="document_size_budget"):
        client.fetch_markdown_document("org/repo", path="README.md", ref="main")


def test_streamed_raw_accepts_valid_small_gzip_response() -> None:
    import gzip

    expected = "# Valid UTF-8 Markdown\n"
    encoded = gzip.compress(expected.encode("utf-8"))

    def handler(request: httpx.Request) -> httpx.Response:
        if request.headers.get("accept") == "application/vnd.github.raw+json":
            return httpx.Response(
                200, content=encoded, headers={
                    "content-type": "text/plain",
                    "content-encoding": "gzip",
                },
            )
        return httpx.Response(200, json={"encoding": "none"})

    client = GitHubClient(
        max_markdown_bytes=4096,
        client=httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="https://api.github.com",
        ),
    )
    assert client.fetch_markdown_document("org/repo", path="README.md", ref="main") == expected


def test_streamed_raw_rejects_large_decompressed_gzip_response() -> None:
    import gzip

    compressed = gzip.compress(b"a" * 256 * 1024)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.headers.get("accept") == "application/vnd.github.raw+json":
            return httpx.Response(
                200, content=compressed, headers={
                    "content-type": "text/plain",
                    "content-encoding": "gzip",
                },
            )
        return httpx.Response(200, json={"encoding": "none"})

    client = GitHubClient(
        max_markdown_bytes=32 * 1024,
        client=httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="https://api.github.com",
        ),
    )
    with pytest.raises(GitHubIncompleteCoverageError, match="document_size_budget"):
        client.fetch_markdown_document("org/repo", path="README.md", ref="main")


@pytest.mark.parametrize(
    "tree_payload",
    [
        {"truncated": False},
        {"truncated": False, "tree": None},
        {"truncated": False, "tree": {"path": "README.md"}},
        {"truncated": False, "tree": ["README.md"]},
    ],
)
def test_malformed_git_tree_fails_closed_instead_of_claiming_empty_repository(
    tree_payload: dict,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=tree_payload)

    client = GitHubClient(client=httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    ))
    with pytest.raises(GitHubIncompleteCoverageError, match="malformed_tree") as exc:
        client.list_repository_files("org/repo", ref="main")
    assert exc.value.scope == "org/repo@main"


def test_valid_empty_git_tree_still_succeeds() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"truncated": False, "tree": []})

    client = GitHubClient(client=httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    ))
    assert client.list_repository_files("org/repo", ref="main") == []


def test_empty_paginated_page_with_next_link_fails_closed() -> None:
    pages: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        pages.append(request.url.params.get("page"))
        if pages[-1] == "1":
            return httpx.Response(
                200,
                headers={"Link": '<https://api.github.com/repos/org/repo/issues?per_page=100&page=2>; rel="next"'},
                json=[{
                    "id": 1, "number": 1, "title": "Issue",
                    "body": "Some evidence", "state": "open",
                    "created_at": "2026-10-30T00:00:00Z",
                }],
            )
        return httpx.Response(
            200,
            headers={"Link": '<https://api.github.com/repos/org/repo/issues?per_page=100&page=3>; rel="next"'},
            json=[],
        )

    client = GitHubClient(client=httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    ))
    with pytest.raises(GitHubIncompleteCoverageError, match="empty_page_with_next") as exc:
        client.fetch_issues("org/repo")
    assert exc.value.scope == "/repos/org/repo/issues"
    assert pages == ["1", "2"]


@pytest.mark.parametrize(
    "page", [{"message": "Internal error"}, ["unexpected-item"], None]
)
def test_malformed_pagination_result_fails_with_coverage_error(page) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        # json=None would produce an empty body in HTTPX, not JSON null.
        return httpx.Response(200, content=b"null" if page is None else None, json=page if page is not None else None)

    client = GitHubClient(client=httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    ))
    with pytest.raises(GitHubIncompleteCoverageError, match="malformed_pagination"):
        client.fetch_issues("org/repo")



@pytest.mark.parametrize("body", [b"", b"{not-json", b"null", b"[]"])
def test_malformed_tree_http_200_does_not_escape_typed_coverage_error(body: bytes) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=body)

    client = GitHubClient(client=httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com",
    ))
    with pytest.raises(GitHubIncompleteCoverageError, match="malformed_tree"):
        client.list_repository_files("org/repo", ref="main")


@pytest.mark.parametrize("body", [b"", b"{not-json", b"null"])
def test_malformed_paginated_http_200_reports_coverage_error(body: bytes) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=body)

    client = GitHubClient(client=httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com",
    ))
    with pytest.raises(GitHubIncompleteCoverageError, match="malformed_pagination"):
        client.fetch_issues("org/repo")

