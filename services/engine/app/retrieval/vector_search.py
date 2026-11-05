from __future__ import annotations

from collections import OrderedDict
from hashlib import sha256
from json import dumps
from math import isfinite
from threading import RLock

from sqlalchemy.orm import Session

from app.indexing.embedder import Embedder
from app.llm.base import ProviderResponseError
from app.repositories.decisions import DecisionRepository
from app.repositories.workspaces import WorkspaceRepository
from app.retrieval.full_text import RetrievalHit

# B01: bounded, process-local optimization. No 0013 Alembic migration, no
# persistent/private source snapshots, and no caching FakeEmbedder or arbitrary
# embedders unless they explicitly advertise a stable namespace.
_MAX_CACHE_ENTRIES = 256
_MAX_VECTOR_DIMENSIONS = 8192
_cache_lock = RLock()
_cache: OrderedDict[tuple, tuple[float, ...]] = OrderedDict()


def _validated_embedding(value: object, *, dimension: int | None = None) -> tuple[float, ...]:
    if not isinstance(value, (list, tuple)) or not 1 <= len(value) <= _MAX_VECTOR_DIMENSIONS:
        raise ProviderResponseError("Embedding provider returned an invalid vector size")
    if dimension is not None and len(value) != dimension:
        raise ProviderResponseError("Embedding provider returned a mismatched vector dimension")
    validated: list[float] = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ProviderResponseError("Embedding provider returned a non-numeric vector value")
        number = float(item)
        if not isfinite(number):
            raise ProviderResponseError("Embedding provider returned a non-finite vector value")
        validated.append(number)
    return tuple(validated)


def _embed_batch(embedder: Embedder, texts: list[str], *, dimension: int | None = None) -> list[tuple[float, ...]]:
    raw = embedder.embed(texts)
    if not isinstance(raw, list) or len(raw) != len(texts):
        raise ProviderResponseError("Embedding provider returned an invalid batch size")
    # Validate the entire batch before caching any result; never silently
    # truncate a mismatched vector using zip().
    return [_validated_embedding(embedding, dimension=dimension) for embedding in raw]


def _cache_namespace(embedder: Embedder) -> tuple[str, ...] | None:
    namespace = getattr(embedder, "embedding_cache_namespace", None)
    if (
        isinstance(namespace, tuple)
        and 2 <= len(namespace) <= 6
        and all(isinstance(item, str) and 0 < len(item) <= 512 for item in namespace)
    ):
        return namespace
    return None


def _cache_read(key: tuple) -> tuple[float, ...] | None:
    with _cache_lock:
        value = _cache.get(key)
        if value is not None:
            _cache.move_to_end(key)
        return value


def _cache_write(key: tuple, value: tuple[float, ...]) -> None:
    with _cache_lock:
        _cache[key] = value
        _cache.move_to_end(key)
        while len(_cache) > _MAX_CACHE_ENTRIES:
            _cache.popitem(last=False)


def _similarity(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    # Finite inputs can still overflow during multiplication/summation.
    result = sum(a * b for a, b in zip(left, right))
    if not isfinite(result):
        raise ProviderResponseError("Embedding similarity produced a non-finite score")
    return result


def vector_search(
    *,
    session: Session,
    workspace_slug: str,
    query: str,
    embedder: Embedder,
    review_state: str = "accepted",
) -> list[RetrievalHit]:
    workspace = WorkspaceRepository(session).get_by_slug(workspace_slug)
    if workspace is None:
        raise ValueError(f"Workspace not found: {workspace_slug}")

    decisions = DecisionRepository(session).list_by_review_state(workspace.id, review_state)
    if not decisions:
        return []

    # Query is always embedded exactly once per call; only stable decision
    # content may be cached. FakeEmbedder has no namespace and stays uncached.
    query_vector = _embed_batch(embedder, [query])[0]
    dimension = len(query_vector)
    # Private/credential-backed sources remain outside this process cache
    # until the separate F06b P privacy/retention gate is accepted.
    namespace = _cache_namespace(embedder) if workspace.access_source_type == "public" else None

    def decision_text(decision) -> str:
        return " ".join([decision.title, decision.problem, decision.chosen_option, decision.tradeoffs])

    # Include context/constraints in the *version key* even though the
    # existing vector input uses four fields, to invalidate on all content edits.
    def decision_hash(decision) -> str:
        # Length-unambiguous JSON avoids collisions from delimiter characters
        # present in user-controlled decision fields.
        version_content = dumps([
            decision.title, decision.problem, decision.chosen_option,
            decision.tradeoffs, decision.context or "", decision.constraints or "",
        ], ensure_ascii=False, separators=(",", ":"))
        return sha256(version_content.encode("utf-8")).hexdigest()

    embeddings: dict[int, tuple[float, ...]] = {}
    missing_decisions = []
    missing_texts = []
    missing_keys: list[tuple | None] = []
    for decision in decisions:
        key = (
            workspace.owner_scope, workspace.slug, workspace.id, decision.id,
            namespace, decision_hash(decision), dimension,
        ) if namespace is not None else None
        cached = _cache_read(key) if key is not None else None
        if cached is not None:
            embeddings[decision.id] = cached
        else:
            missing_decisions.append(decision)
            missing_texts.append(decision_text(decision))
            missing_keys.append(key)

    if missing_texts:
        generated = _embed_batch(embedder, missing_texts, dimension=dimension)
        for decision, value, key in zip(missing_decisions, generated, missing_keys):
            embeddings[decision.id] = value
            if key is not None:
                _cache_write(key, value)

    hits = []
    for decision in decisions:
        score = _similarity(query_vector, embeddings[decision.id])
        hits.append(
            RetrievalHit(
                decision_id=decision.id,
                title=decision.title,
                problem=decision.problem,
                chosen_option=decision.chosen_option,
                tradeoffs=decision.tradeoffs,
                score=score,
            )
        )
    return sorted(hits, key=lambda item: item.score, reverse=True)
