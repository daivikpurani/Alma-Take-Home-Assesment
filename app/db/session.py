# app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends
from app.core.config import get_settings, Settings


def get_engine(settings: Settings):
    return create_engine(settings.database_url, future=True)


def get_session_local(engine):
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    )


# Dependency to provide DB access per request
def get_db(
    settings: Settings = Depends(get_settings),
):
    engine = get_engine(settings)
    SessionLocal = get_session_local(engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
