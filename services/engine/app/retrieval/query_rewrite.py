from __future__ import annotations

import re
import unicodedata


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "by",
    "did",
    "do",
    "does",
    "for",
    "how",
    "in",
    "is",
    "it",
    "its",
    "need",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "use",
    "was",
    "we",
    "what",
    "why",
}

TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?")
SEPARATOR_PATTERN = re.compile(r"[\(\)\[\]\{\},.:;!?/\\]+")
PHRASE_REWRITES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bpre[\s-]?release\b"), "prerelease"),
    (re.compile(r"\brelease[\s-]?candidate\b"), "release candidate"),
    (re.compile(r"\bduplicate[\s-]?key\b"), "duplicate key"),
    (re.compile(r"\blong[\s-]?running\b"), "long running"),
    (re.compile(r"\bcache[\s-]?only\b"), "cache only"),
    (re.compile(r"\bbackground[\s-]?jobs?\b"), "background jobs"),
    (re.compile(r"\bsource[\s-]+of[\s-]+truth\b"), "source of truth"),
    (re.compile(r"\bweb[\s-]?socket\b"), "websocket"),
    (re.compile(r"\bkeep[\s_-]?alive\b"), "keep alive"),
    (re.compile(r"\bgithub[\s-]?app\b"), "github app"),
    (re.compile(r"\bhttp[\s-]?based\b"), "http"),
    (re.compile(r"\bactive[\s_-]?downloads\b"), "active downloads"),
    (re.compile(r"\bfailed[\s_-]?downloads\b"), "failed downloads"),
    (re.compile(r"\bremote[\s-]?browser\b"), "remote browser"),
    (re.compile(r"\baddwebhooks\(\)"), "addwebhooks"),
)
TOKEN_ALIASES: dict[str, tuple[str, ...]] = {
    "rc": ("release", "candidate"),
    "prerelease": ("pre", "release"),
    "pre-release": ("pre", "release"),
    "app": ("app", "application", "identity", "token"),
    "identity": ("identity", "token", "app"),
    "token": ("token", "identity", "credential"),
    "credential": ("credential", "token", "identity"),
    "http": ("http", "download", "downloads"),
    "download": ("download", "downloads", "http"),
    "downloads": ("download", "downloads", "http"),
    "agent": ("agent", "active", "downloads"),
    "active": ("active", "status", "downloads"),
    "status": ("status", "state", "tracking"),
    "tracking": ("tracking", "status", "state"),
    "browser": ("browser", "remote"),
    "remote": ("remote", "browser"),
    "queue": ("queue", "background", "jobs"),
    "queues": ("queue", "background", "jobs"),
    "job": ("job", "jobs", "queue"),
    "jobs": ("jobs", "queue", "background"),
    "rollout": ("rollout", "migration"),
    "migration": ("migration", "rollout"),
    "migrate": ("migrate", "migration"),
    "websocket": ("websocket", "web", "socket"),
    "db": ("database",),
    "postgres": ("postgresql",),
    "postgresql": ("postgres", "postgresql"),
}
BROAD_QUERY_TERMS = {
    "architecture",
    "migration",
    "policy",
    "process",
    "release",
    "strategy",
    "system",
    "workflow",
}
COMPARATIVE_QUERY_TERMS = {
    "compare",
    "comparison",
    "difference",
    "together",
    "versus",
    "vs",
}


def _normalize_query_text(query: str) -> str:
    normalized = unicodedata.normalize("NFKC", query).strip().lower()
    normalized = SEPARATOR_PATTERN.sub(" ", normalized)
    normalized = normalized.replace("_", " ")
    for pattern, replacement in PHRASE_REWRITES:
        normalized = pattern.sub(replacement, normalized)
    return " ".join(normalized.split())


def expand_query_terms(query: str) -> list[str]:
    normalized = _normalize_query_text(query)
    terms = TOKEN_PATTERN.findall(normalized)
    expanded: list[str] = []
    for term in terms:
        aliases = TOKEN_ALIASES.get(term)
        if aliases:
            expanded.extend(aliases)
        else:
            expanded.append(term)
    return expanded


def significant_query_terms(query: str) -> list[str]:
    terms = [term for term in expand_query_terms(query) if term not in STOP_WORDS]
    return terms or expand_query_terms(query)


def is_broad_why_query(query: str) -> bool:
    terms = set(significant_query_terms(query))
    return bool(terms.intersection(BROAD_QUERY_TERMS | COMPARATIVE_QUERY_TERMS))


def rewrite_query(query: str) -> str:
    return " ".join(expand_query_terms(query))
