from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


def get_engine():
    settings = get_settings()
    return create_engine(settings.database_url, future=True)


def get_session_factory():
    return sessionmaker(bind=get_engine(), class_=Session, expire_on_commit=False)


def get_db_session() -> Session:
    return get_session_factory()()
