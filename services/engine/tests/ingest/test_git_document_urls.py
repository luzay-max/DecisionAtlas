from app.ingest.github_importer import _repo_doc_url


def test_provider_native_document_source_urls() -> None:
    assert _repo_doc_url(
        "https://gitlab.com/group/team/repo",
        repo="group/team/repo", ref="main", path="docs/ADR 1.md", provider="gitlab",
    ) == "https://gitlab.com/group/team/repo/-/blob/main/docs/ADR%201.md"
    assert _repo_doc_url(
        "https://gitee.com/org/repo",
        repo="org/repo", ref="master", path="README.md", provider="gitee",
    ) == "https://gitee.com/org/repo/blob/master/README.md"
    assert _repo_doc_url(
        "https://github.com/org/repo",
        repo="org/repo", ref="main", path="README.md",
    ) == "https://github.com/org/repo/blob/main/README.md"
