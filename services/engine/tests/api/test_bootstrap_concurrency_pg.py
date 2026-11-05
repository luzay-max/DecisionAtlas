"""Issue #48: PostgreSQL advisory lock concurrency integration, CI only.

Uses isolated ephemeral PostgreSQL 17, no real users/private content. Does not
run for normal SQLite/Windows tests without an explicit CI-only URL.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import os
from threading import Barrier

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, func, inspect, select, text
from sqlalchemy.orm import Session

from app.auth import SESSION_HEADER
from app.db.models import Actor, AuthSession, OwnerScope, OwnerScopeMembership
from app.main import create_app


def test_pg17_bootstrap_advisory_lock_avoids_identity_duplicate_under_parallel_requests(
    monkeypatch,
) -> None:
    url = os.getenv("DECISIONATLAS_BOOTSTRAP_PG_CI_URL")
    if not url or not url.startswith("postgresql+psycopg://"):
        pytest.skip("Issue #48 real PostgreSQL concurrency test needs isolated CI URL")

    engine = create_engine(url)
    with engine.connect() as conn:
        assert int(conn.scalar(text("SHOW server_version_num"))) >= 170000
        assert not inspect(conn).has_table("alembic_version"), (
            "Refuse to run destructive test against an existing database"
        )

    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("AUTH_AUTO_BOOTSTRAP_LOCAL", "true")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")

    request_count = 8
    gate = Barrier(request_count, timeout=20)

    def invoke(_index: int) -> tuple[int, dict]:
        with TestClient(create_app()) as client:
            gate.wait()
            response = client.post("/auth/bootstrap")
            return response.status_code, response.json()

    with ThreadPoolExecutor(max_workers=request_count) as pool:
        results = list(pool.map(invoke, range(request_count)))

    assert all(status == 200 for status, _ in results)
    assert len({body["actor"]["id"] for _, body in results}) == 1
    assert len({body["session_token"] for _, body in results}) == request_count
    assert all(body["role"] == "admin" for _, body in results)

    # Every request created a distinct valid persistent session for the same
    # authorized local bootstrap identity, never a duplicate membership.
    engine.dispose()
    engine = create_engine(url)
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(Actor)) == 1
        assert session.scalar(select(func.count()).select_from(OwnerScope)) == 1
        assert session.scalar(select(func.count()).select_from(OwnerScopeMembership)) == 1
        assert session.scalar(select(func.count()).select_from(AuthSession)) == request_count
        assert session.scalar(select(Actor.is_bootstrap)) is True
        assert session.scalar(select(OwnerScopeMembership.role)) == "admin"
    with TestClient(create_app()) as client:
        for _, body in results:
            verified = client.get(
                "/auth/session", headers={SESSION_HEADER: body["session_token"]}
            )
            assert verified.status_code == 200
            assert verified.json()["current_owner_scope"] == "local-default"
    engine.dispose()
