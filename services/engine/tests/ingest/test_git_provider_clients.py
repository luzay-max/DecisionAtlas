"""Offline read-only API contract tests for public GitLab and Gitee sources."""
from __future__ import annotations

import base64
from datetime import datetime, timezone

import httpx
import pytest

from app.ingest.git_provider_clients import GiteeClient, GitLabClient, GitProviderError


def _client(base_url: str, handler):
    return httpx.Client(base_url=base_url, transport=httpx.MockTransport(handler))


def test_gitlab_issue_merge_request_and_commit_normalization() -> None:
    seen = []

    def respond(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        path = request.url.path
        if path.endswith("/issues"):
            return httpx.Response(200, json=[{
                "id": 3, "iid": 2, "title": "Compatibility", "description": "Reason and tradeoff",
                "author": {"username": "maintainer"}, "state": "closed",
                "web_url": "https://gitlab.com/acme/docs/-/issues/2",
                "created_at": "2026-01-01T11:00:00Z", "updated_at": "2026-01-02T11:00:00Z",
            }])
        if path.endswith("/merge_requests"):
            return httpx.Response(200, json=[{
                "id": 6, "iid": 4, "title": "Choose cache", "description": "Latency",
                "state": "merged", "merged_at": "2026-01-03T12:00:00Z",
                "web_url": "https://gitlab.com/acme/docs/-/merge_requests/4",
                "created_at": "2026-01-01T11:00:00Z", "updated_at": "2026-01-03T12:00:00Z",
            }])
        if path.endswith("/repository/commits"):
            return httpx.Response(200, json=[{
                "id": "abcdef", "message": "Document cache rationale\n\nMore detail",
                "web_url": "https://gitlab.com/acme/docs/-/commit/abcdef",
                "author_name": "Example", "authored_date": "2026-01-03T13:00:00Z",
            }])
        return httpx.Response(404)

    client = GitLabClient(client=_client("https://gitlab.com/api/v4", respond))
    issues = client.fetch_issues("acme/docs")
    prs = client.fetch_pull_requests("acme/docs")
    commits = client.fetch_commits("acme/docs")
    assert issues[0].artifact_type == "issue"
    assert issues[0].source_id == "gitlab:issue:3"
    assert issues[0].metadata_json["number"] == 2
    assert issues[0].timestamp.tzinfo is not None
    assert prs[0].artifact_type == "pr"
    assert prs[0].metadata_json["source_kind"] == "merge_request"
    assert prs[0].metadata_json["state"] == "merged"
    assert prs[0].metadata_json["merged_at"]
    assert commits[0].source_id == "gitlab:commit:abcdef"
    assert commits[0].title == "Document cache rationale"
    assert all("projects" in url for url in seen)


def test_gitlab_nested_project_and_document_tree() -> None:
    requested = []

    def respond(request: httpx.Request) -> httpx.Response:
        requested.append(str(request.url))
        path = request.url.path
        if path.endswith("/repository/tree"):
            return httpx.Response(200, json=[
                {"type": "blob", "path": "docs/ADR-001.md", "id": "f1"},
                {"type": "tree", "path": "docs", "id": "d1"},
            ])
        if path.endswith("/raw"):
            assert request.url.params["ref"] == "main"
            return httpx.Response(200, text="# Architecture\nUse explicit reviewers.")
        if path.endswith("platform"):
            return httpx.Response(200, json={"default_branch": "main"})
        return httpx.Response(404)

    client = GitLabClient(client=_client("https://gitlab.com/api/v4", respond))
    docs = client.list_repository_files("org/team/platform")
    assert [(x.path, x.sha) for x in docs] == [("docs/ADR-001.md", "f1")]
    assert client.fetch_markdown_document("org/team/platform", path="docs/ADR-001.md", ref="main").startswith("# Architecture")
    assert any("org%2Fteam%2Fplatform" in url for url in requested)


def test_gitee_issue_pr_commit_tree_and_document() -> None:
    body = base64.b64encode("## Why\nThe decision has evidence".encode()).decode()

    def respond(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/issues"):
            return httpx.Response(200, json=[{"id": "I100", "number": "I100", "title": "Bug",
                 "body": "Impacts design", "html_url": "https://gitee.com/acme/design/issues/I100",
                 "created_at": "2026-02-01T10:00:00+08:00", "updated_at": "2026-02-02T10:00:00+08:00",
                 "user": {"login": "a"}, "state": "closed"}])
        if path.endswith("/pulls"):
            return httpx.Response(200, json=[{"id": 21, "number": 5, "title": "Improve docs",
                 "body": "Document reasoning", "html_url": "https://gitee.com/acme/design/pulls/5",
                 "created_at": "2026-02-01T10:00:00+08:00", "updated_at": "2026-02-02T10:00:00+08:00",
                 "state": "closed", "merged": True, "merged_at": "2026-02-02T10:00:00+08:00"}])
        if path.endswith("/commits"):
            return httpx.Response(200, json=[{"sha": "abc", "html_url": "https://gitee.com/acme/design/commit/abc",
                "commit": {"message": "Add ADR", "author": {"date": "2026-02-02T10:00:00+08:00", "name": "John"}}}])
        if "/git/trees/" in path:
            return httpx.Response(200, json={"truncated": False, "tree": [
                 {"type": "blob", "path": "docs/decision.md", "sha": "fff", "size": 30}]})
        if "/contents/" in path:
            return httpx.Response(200, json={"encoding": "base64", "content": body})
        if path.endswith("/acme/design"):
            return httpx.Response(200, json={"default_branch": "master"})
        return httpx.Response(404)

    client = GiteeClient(client=_client("https://gitee.com/api/v5", respond))
    assert client.get_default_branch("acme/design") == "master"
    issue = client.fetch_issues("acme/design")[0]
    assert issue.metadata_json["provider"] == "gitee"
    assert issue.source_id == "gitee:issue:I100"
    pr = client.fetch_pull_requests("acme/design")[0]
    assert pr.metadata_json["merged"] is True
    assert pr.metadata_json["state"] == "closed"
    assert client.fetch_commits("acme/design")[0].source_id == "gitee:commit:abc"
    assert client.list_repository_files("acme/design", ref="master")[0].path == "docs/decision.md"
    assert "evidence" in client.fetch_markdown_document("acme/design", path="docs/decision.md", ref="master")


@pytest.mark.parametrize("bad", ["", "foo", "../secret", "org/../repo", "a/b?token=secret", "a//b", "a/b/c"])
def test_gitee_rejects_invalid_repository_before_network(bad: str) -> None:
    client = GiteeClient(client=_client("https://gitee.com/api/v5", lambda r: pytest.fail("network used")))
    with pytest.raises(GitProviderError):
        client.get_repository_metadata(bad)


@pytest.mark.parametrize("bad", ["../secret.md", "docs/../../.env", "/etc/passwd", "docs//adr.md"])
def test_paths_reject_traversal_before_network(bad: str) -> None:
    a = GitLabClient(client=_client("https://gitlab.com/api/v4", lambda r: pytest.fail("network used")))
    b = GiteeClient(client=_client("https://gitee.com/api/v5", lambda r: pytest.fail("network used")))
    with pytest.raises(GitProviderError):
        a.fetch_markdown_document("team/repo", path=bad, ref="main")
    with pytest.raises(GitProviderError):
        b.fetch_markdown_document("team/repo", path=bad, ref="main")


def test_gitlab_pagination_limit_is_explicit_not_silent() -> None:
    def respond(request):
        return httpx.Response(200, json=[{"id": i, "title": str(i)} for i in range(100)])

    c = GitLabClient(max_pages=1, client=_client("https://gitlab.com/api/v4", respond))
    with pytest.raises(GitProviderError, match="pagination limit"):
        c.fetch_issues("group/repo")


def test_gitee_incremental_date_filter_and_safe_auth_errors() -> None:
    def respond(request):
        if "issues" in request.url.path:
            return httpx.Response(200, json=[
              {"id": "A", "updated_at": "2026-01-01T00:00:00Z"},
              {"id": "B", "updated_at": "2026-02-01T00:00:00Z"},
            ])
        return httpx.Response(401, text="secret-body")

    c = GiteeClient(client=_client("https://gitee.com/api/v5", respond))
    out = c.fetch_issues("a/b", since=datetime(2026, 1, 15, tzinfo=timezone.utc))
    assert [item.source_id for item in out] == ["gitee:issue:B"]
    with pytest.raises(GitProviderError, match="access denied") as error:
        c.get_repository_metadata("a/b")
    assert "secret-body" not in str(error.value)


def test_gitee_rejects_truncated_tree_and_invalid_doc_encoding() -> None:
    def respond(request):
        if "/git/trees/" in request.url.path:
            return httpx.Response(200, json={"truncated": True, "tree": []})
        return httpx.Response(200, json={"encoding": "none", "content": "not trusted"})

    c = GiteeClient(client=_client("https://gitee.com/api/v5", respond))
    with pytest.raises(GitProviderError, match="truncated"):
        c.list_repository_files("a/b", ref="main")
    with pytest.raises(GitProviderError, match="encoding"):
        c.fetch_markdown_document("a/b", path="README.md", ref="main")
