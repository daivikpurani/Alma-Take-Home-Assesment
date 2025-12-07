# app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends
from app.core.config import get_settings, Settings
from app.db.base import Base, load_models


# We create one global engine for the entire app, not per request
_engine = None


def get_engine(settings: Settings):
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.database_url,
            future=True,
            pool_pre_ping=True,
        )
    return _engine


def get_session_local(engine):
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    )


# Dependency used in routes
def get_db(settings: Settings = Depends(get_settings)):
    engine = get_engine(settings)
    SessionLocal = get_session_local(engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Called one time at app startup
def init_db():
    load_models()  # <-- fixes circular import issues
    settings = get_settings()
    engine = get_engine(settings)
    Base.metadata.create_all(bind=engine)
