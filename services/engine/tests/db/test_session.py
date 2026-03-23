from __future__ import annotations

from app.db.session import get_engine


def test_get_engine_reuses_engine_per_database_url(monkeypatch, tmp_path) -> None:
    db_one = tmp_path / "one.db"
    db_two = tmp_path / "two.db"

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_one}")
    first = get_engine()
    second = get_engine()

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_two}")
    third = get_engine()

    assert first is second
    assert third is not first


def test_sqlite_engine_sets_busy_timeout(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "busy-timeout.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    engine = get_engine()
    with engine.connect() as connection:
        busy_timeout = connection.exec_driver_sql("PRAGMA busy_timeout").scalar_one()

    assert busy_timeout == 30000
