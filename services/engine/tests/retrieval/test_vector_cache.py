from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.models import Decision, Workspace
from app.indexing.embedder import Embedder, FakeEmbedder
from app.llm.base import ProviderResponseError
from app.retrieval.vector_search import vector_search


class DeterministicCountingEmbedder(Embedder):
    def __init__(self, namespace: str, dimension: int = 2):
        # Only explicit stable namespaces opt in to B01 decision-vector caching.
        self.embedding_cache_namespace = ("synthetic-test-only", namespace)
        self.dimension = dimension
        self.calls: list[list[str]] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(list(texts))
        return [
            [float(sum(text.encode("utf-8")) % 97) + 1.0] + [1.0] * (self.dimension - 1)
            for text in texts
        ]


class InvalidEmbedder(Embedder):
    def __init__(self, invalid_for: str, value: list[float] | None = None):
        self.invalid_for = invalid_for
        self.value = value if value is not None else [float("nan"), 1.0]

    def embed(self, texts: list[str]) -> list[list[float]]:
        if len(texts) == 1 and texts[0] == "find evidence":
            return [self.value if self.invalid_for == "query" else [1.0, 1.0]]
        return [self.value if self.invalid_for == "decision" else [1.0, 1.0] for _ in texts]


def _db(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "cache.db"
    url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(cfg, "head")
    engine = create_engine(url)
    with Session(engine) as session:
        workspace = Workspace(slug="b01-workspace", name="B01 Test", owner_scope="b01-owner")
        session.add(workspace)
        session.flush()
        session.add_all([
            Decision(
                workspace_id=workspace.id, title="Use PostgreSQL", problem="Need consistency",
                chosen_option="Use transactions", tradeoffs="Operational overhead",
                context="Production data integrity", constraints="Limited writes",
                review_state="accepted", status="active",
            ),
            Decision(
                workspace_id=workspace.id, title="Keep SQLite local", problem="Need lightweight storage",
                chosen_option="Use file-backed database", tradeoffs="Single writer",
                review_state="accepted", status="active",
            ),
            Decision(
                workspace_id=workspace.id, title="Unreviewed draft", problem="Not verified",
                chosen_option="Do not publish", tradeoffs="Unknown",
                review_state="candidate", status="active",
            ),
        ])
        session.commit()
    return engine


def test_decision_vectors_are_cached_by_content_and_provider_but_queries_are_not(
    tmp_path: Path, monkeypatch
) -> None:
    engine = _db(tmp_path, monkeypatch)
    embedder = DeterministicCountingEmbedder(str(tmp_path), dimension=3)

    with Session(engine) as session:
        first = vector_search(
            session=session, workspace_slug="b01-workspace", query="find evidence", embedder=embedder,
        )
        second = vector_search(
            session=session, workspace_slug="b01-workspace", query="find evidence", embedder=embedder,
        )
    assert [len(call) for call in embedder.calls] == [1, 2, 1]
    assert [hit.decision_id for hit in first] == [hit.decision_id for hit in second]
    assert len(first) == 2  # Candidate never enters accepted-only cache/search.

    # Changing content invalidates only the affected decision, without a
    # persistent DB migration or relying on a manually updated timestamp.
    with Session(engine) as session:
        modified = session.scalar(select(Decision).where(Decision.title == "Use PostgreSQL"))
        assert modified is not None
        modified.tradeoffs = "Different operational risk"
        session.commit()
    with Session(engine) as session:
        vector_search(
            session=session, workspace_slug="b01-workspace", query="find evidence", embedder=embedder,
        )
    assert [len(call) for call in embedder.calls] == [1, 2, 1, 1, 1]

    # A different provider/model namespace never consumes the old vectors.
    other = DeterministicCountingEmbedder(str(tmp_path) + "-new-model", dimension=3)
    with Session(engine) as session:
        vector_search(
            session=session, workspace_slug="b01-workspace", query="find evidence", embedder=other,
        )
    assert [len(call) for call in other.calls] == [1, 2]
    engine.dispose()


def test_credential_backed_workspaces_do_not_use_process_embedding_cache(
    tmp_path: Path, monkeypatch
) -> None:
    engine = _db(tmp_path, monkeypatch)
    with Session(engine) as session:
        workspace = session.scalar(select(Workspace).where(Workspace.slug == "b01-workspace"))
        assert workspace is not None
        workspace.access_source_type = "github_token"
        session.commit()

    embedder = DeterministicCountingEmbedder(str(tmp_path) + "-private", dimension=2)
    with Session(engine) as session:
        vector_search(session=session, workspace_slug="b01-workspace", query="find evidence", embedder=embedder)
        vector_search(session=session, workspace_slug="b01-workspace", query="find evidence", embedder=embedder)
    # Safe default while F06b privacy operations P remain unapproved.
    assert [len(call) for call in embedder.calls] == [1, 2, 1, 2]
    engine.dispose()


def test_changed_embedding_dimensions_do_not_reuse_cached_old_dimension(
    tmp_path: Path, monkeypatch
) -> None:
    engine = _db(tmp_path, monkeypatch)
    namespace = str(tmp_path) + "-different-dimension"
    first_model = DeterministicCountingEmbedder(namespace, dimension=2)
    second_model = DeterministicCountingEmbedder(namespace, dimension=4)
    with Session(engine) as session:
        vector_search(session=session, workspace_slug="b01-workspace", query="find evidence", embedder=first_model)
        vector_search(session=session, workspace_slug="b01-workspace", query="find evidence", embedder=second_model)
    assert [len(call) for call in first_model.calls] == [1, 2]
    assert [len(call) for call in second_model.calls] == [1, 2]
    engine.dispose()


@pytest.mark.parametrize(
    "invalid_for,value",
    [
        ("query", [float("nan"), 1.0]),
        ("query", [float("inf"), 1.0]),
        ("decision", [float("nan"), 1.0]),
        ("decision", [1.0]),
        ("decision", []),
    ],
)
def test_invalid_or_mismatched_vectors_fail_closed(
    tmp_path: Path, monkeypatch, invalid_for: str, value: list[float]
) -> None:
    engine = _db(tmp_path, monkeypatch)
    with Session(engine) as session:
        with pytest.raises(ProviderResponseError):
            vector_search(
                session=session, workspace_slug="b01-workspace", query="find evidence",
                embedder=InvalidEmbedder(invalid_for, value),
            )
    engine.dispose()


def test_finite_embeddings_with_overflowing_dot_product_fail_closed(
    tmp_path: Path, monkeypatch
) -> None:
    engine = _db(tmp_path, monkeypatch)

    class HugeFiniteEmbedder(Embedder):
        def embed(self, texts: list[str]) -> list[list[float]]:
            return [[1e308, 1e308] for _ in texts]

    with Session(engine) as session:
        with pytest.raises(ProviderResponseError, match="non-finite score"):
            vector_search(
                session=session, workspace_slug="b01-workspace",
                query="find evidence", embedder=HugeFiniteEmbedder(),
            )
    engine.dispose()


def test_fake_embedder_never_claims_stable_decision_cache_identity() -> None:
    assert not hasattr(FakeEmbedder(), "embedding_cache_namespace")
