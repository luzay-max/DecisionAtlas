from __future__ import annotations


def rewrite_query(query: str) -> str:
    return " ".join(query.strip().lower().split())
