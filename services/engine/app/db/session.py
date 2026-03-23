from __future__ import annotations

from threading import RLock

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

_engine_lock = RLock()
_engines: dict[str, Engine] = {}
_session_factories: dict[str, sessionmaker] = {}


def get_engine():
    settings = get_settings()
    database_url = settings.database_url
    with _engine_lock:
        engine = _engines.get(database_url)
        if engine is None:
            create_args: dict[str, object] = {"future": True}
            if database_url.startswith("sqlite"):
                create_args["connect_args"] = {
                    "timeout": 30,
                    "check_same_thread": False,
                }
            engine = create_engine(database_url, **create_args)
            if database_url.startswith("sqlite"):
                with engine.connect() as connection:
                    connection.exec_driver_sql("PRAGMA busy_timeout = 30000")
            _engines[database_url] = engine
        return engine


def get_session_factory():
    settings = get_settings()
    database_url = settings.database_url
    with _engine_lock:
        session_factory = _session_factories.get(database_url)
        if session_factory is None:
            session_factory = sessionmaker(bind=get_engine(), class_=Session, expire_on_commit=False)
            _session_factories[database_url] = session_factory
        return session_factory


def get_db_session() -> Session:
    return get_session_factory()()
