from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Decision, Workspace
from app.indexing.embedder import Embedder, FakeEmbedder
from app.llm.base import ProviderTimeoutError
from app.retrieval.answering import answer_why_question
from app.retrieval.full_text import full_text_search
from app.retrieval.hybrid import hybrid_search_with_mode
from app.retrieval.query_rewrite import rewrite_query, significant_query_terms


class FakeMustNotEmbed(FakeEmbedder):
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise AssertionError("FakeEmbedder must never score lexical-only retrieval")


class UnavailableEmbedder(Embedder):
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise ProviderTimeoutError("synthetic embedding provider unavailable")


class WorkingEmbedder(Embedder):
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0] for _ in texts]


def _seed(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "b02-retrieval.sqlite3"
    url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(cfg, "head")
    engine = create_engine(url)
    with Session(engine) as session:
        workspace = Workspace(slug="b02-public", name="B02 Public", owner_scope="local-default")
        other_workspace = Workspace(slug="b02-other", name="Other Workspace", owner_scope="local-default")
        session.add_all([workspace, other_workspace])
        session.flush()
        records = [
            (workspace.id, "使用 PostgreSQL 主库", "保证业务数据一致性", "保持 PostgreSQL 为主数据库", "迁移成本"),
            (workspace.id, "SQLite 本地轻量存储", "离线桌面部署", "使用文件型 SQLite", "并发写入有限"),
            (workspace.id, "RabbitMQ 消息去重", "处理 XXL-JOB 重复回调", "建立幂等消费机制", "额外存储"),
            (other_workspace.id, "火星电梯", "火星探索", "建造太空电梯", "暂不可行"),
        ]
        for ws, title, problem, choice, tradeoffs in records:
            session.add(Decision(
                workspace_id=ws, title=title, problem=problem,
                chosen_option=choice, tradeoffs=tradeoffs,
                review_state="accepted", status="active",
            ))
        session.add(Decision(
            workspace_id=workspace.id, title="火星电梯", problem="未审核",
            chosen_option="忽略", tradeoffs="未批准",
            review_state="candidate", status="active",
        ))
        session.commit()
    return engine


def test_chinese_query_rewrite_retains_han_bigrams_and_latin_technical_tokens() -> None:
    rewritten = rewrite_query("为什么使用PostgreSQL主库保证一致性？")
    terms = significant_query_terms(rewritten)
    assert {"使用", "主库", "保证", "一致", "postgresql"}.issubset(set(terms))
    assert "为什么" not in rewritten
    assert "postgresql" in rewrite_query("PostgreSQL 和 Redis")
    assert "xxl-job" in rewrite_query("检查 XXL-JOB 回调")


def test_pure_chinese_and_mixed_retrieval_are_workspace_scoped(tmp_path: Path, monkeypatch) -> None:
    engine = _seed(tmp_path, monkeypatch)
    with Session(engine) as session:
        pure = full_text_search(
            session=session, workspace_slug="b02-public",
            query=rewrite_query("为什么保证业务数据一致性？"),
        )
        mixed = full_text_search(
            session=session, workspace_slug="b02-public",
            query=rewrite_query("为什么使用PostgreSQL主库？"),
        )
        tech = full_text_search(
            session=session, workspace_slug="b02-public",
            query=rewrite_query("RabbitMQ XXL-JOB 消息去重"),
        )
        negative = full_text_search(
            session=session, workspace_slug="b02-public",
            query=rewrite_query("火星电梯"),
        )
    assert pure and pure[0].title == "使用 PostgreSQL 主库"
    assert mixed and mixed[0].title == "使用 PostgreSQL 主库"
    assert tech and tech[0].title == "RabbitMQ 消息去重"
    assert negative == []  # Candidate + other workspace never leak.
    engine.dispose()


def test_fake_embedding_returns_honest_lexical_only_mode(tmp_path: Path, monkeypatch) -> None:
    engine = _seed(tmp_path, monkeypatch)
    with Session(engine) as session:
        hits, mode = hybrid_search_with_mode(
            session=session, workspace_slug="b02-public",
            query=rewrite_query("为什么使用 PostgreSQL 主库"),
            embedder=FakeMustNotEmbed(),
        )
        no_hits, negative_mode = hybrid_search_with_mode(
            session=session, workspace_slug="b02-public",
            query=rewrite_query("火星电梯"),
            embedder=FakeMustNotEmbed(),
        )
    assert mode == negative_mode == "lexical_only"
    assert hits and hits[0].title == "使用 PostgreSQL 主库"
    assert not no_hits
    engine.dispose()


def test_embedding_timeout_degrades_to_lexical_without_fake_semantic_hits(
    tmp_path: Path, monkeypatch
) -> None:
    engine = _seed(tmp_path, monkeypatch)
    with Session(engine) as session:
        hits, mode = hybrid_search_with_mode(
            session=session, workspace_slug="b02-public",
            query=rewrite_query("PostgreSQL 主库"),
            embedder=UnavailableEmbedder(),
        )
        absent, absent_mode = hybrid_search_with_mode(
            session=session, workspace_slug="b02-public",
            query=rewrite_query("火星电梯"),
            embedder=UnavailableEmbedder(),
        )
        hybrid_hits, hybrid_mode = hybrid_search_with_mode(
            session=session, workspace_slug="b02-public",
            query=rewrite_query("PostgreSQL 主库"),
            embedder=WorkingEmbedder(),
        )
    assert mode == absent_mode == "lexical_fallback"
    assert hits and hits[0].title == "使用 PostgreSQL 主库"
    assert absent == []
    assert hybrid_mode == "hybrid" and hybrid_hits
    engine.dispose()


def test_why_payload_reports_retrieval_mode_without_claiming_semantic_success(
    tmp_path: Path, monkeypatch
) -> None:
    engine = _seed(tmp_path, monkeypatch)
    with Session(engine) as session:
        lexical = answer_why_question(
            session=session, workspace_slug="b02-public",
            question="为什么使用 PostgreSQL 主库", embedder=FakeMustNotEmbed(),
        )
        degraded = answer_why_question(
            session=session, workspace_slug="b02-public",
            question="为什么使用 PostgreSQL 主库", embedder=UnavailableEmbedder(),
        )
    assert lexical["retrieval_mode"] == lexical["answer_context"]["retrieval_mode"] == "lexical_only"
    assert degraded["retrieval_mode"] == degraded["answer_context"]["retrieval_mode"] == "lexical_fallback"
    engine.dispose()
