from __future__ import annotations

import pytest

from app.repository_identity import canonical_github_repository


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Acme/DecisionAtlas", "acme/decisionatlas"),
        ("ACME/DECISIONATLAS", "acme/decisionatlas"),
        ("acme/DecisionAtlas.git", "acme/decisionatlas"),
        (
            "https://github.com/Acme/DecisionAtlas",
            "acme/decisionatlas",
        ),
        (
            "HTTPS://GITHUB.COM/Acme/DecisionAtlas.git",
            "acme/decisionatlas",
        ),
        (" owner/repo ", "owner/repo"),
        ("a/b", "a/b"),
    ],
)
def test_canonical_github_repository_accepts_only_supported_aliases(
    value: str, expected: str
) -> None:
    assert canonical_github_repository(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "   ",
        "/owner/repo",
        "owner/repo/",
        "owner//repo",
        "owner/repo/extra",
        "owner",
        "owner/.",
        "owner/..",
        "owner/.git",
        "owner/repo?query=1",
        "owner/repo#fragment",
        "https://github.com/owner/repo?",
        "https://github.com/owner/repo#",
        "http://github.com/owner/repo",
        "https://www.github.com/owner/repo",
        "https://gitlab.com/owner/repo",
        "https://github.com/owner/repo/extra",
        "https://github.com/owner/repo/",
        "https://github.com/owner%2Frepo",
        "https://github.com/owner/repo%2Fextra",
        "https://user@github.com/owner/repo",
        "https://github.com:443/owner/repo",
        "https://[invalid/owner/repo",
        "bad_owner/repo",
        "bad..owner/repo",
        "owner/repo with spaces",
        "owner/" + ("r" * 101),
        ("o" * 40) + "/repo",
    ],
)
def test_canonical_github_repository_rejects_ambiguous_or_malformed_values(
    value: str | None,
) -> None:
    assert canonical_github_repository(value) is None
