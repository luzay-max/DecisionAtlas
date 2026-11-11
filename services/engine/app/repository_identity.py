from __future__ import annotations

import re
from urllib.parse import urlsplit


_OWNER = re.compile(r"^(?!.*--)[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
_REPOSITORY = re.compile(r"^[A-Za-z0-9._-]{1,100}$")


def canonical_github_repository(value: str | None) -> str | None:
    """Return a lowercase GitHub owner/repo key, or None for ambiguous input.

    Accepted inputs are GitHub HTTPS repository URLs and owner/repo shorthand,
    with an optional trailing lowercase .git suffix. This function deliberately
    does not resolve redirects, aliases, credentials, or non-GitHub hosts.
    """
    if value is None:
        return None
    candidate = value.strip()
    if (
        not candidate
        or "?" in candidate
        or "#" in candidate
        or any(ord(char) <= 0x20 or ord(char) == 0x7F for char in candidate)
    ):
        return None

    if "://" in candidate:
        try:
            parsed = urlsplit(candidate)
            port = parsed.port
        except ValueError:
            return None
        if (
            parsed.scheme.lower() != "https"
            or parsed.hostname is None
            or parsed.hostname.lower() != "github.com"
            or parsed.netloc.lower() != "github.com"
            or parsed.username is not None
            or parsed.password is not None
            or port is not None
        ):
            return None
        path = parsed.path
        if not path.startswith("/") or path.endswith("/"):
            return None
        path = path[1:]
    else:
        path = candidate
        if path.startswith("/") or path.endswith("/"):
            return None

    parts = path.split("/")
    if len(parts) != 2:
        return None
    owner, repository = parts
    if repository.endswith(".git"):
        repository = repository[:-4]
    if not _OWNER.fullmatch(owner) or not _REPOSITORY.fullmatch(repository):
        return None
    if repository in {".", ".."}:
        return None
    return f"{owner.lower()}/{repository.lower()}"
