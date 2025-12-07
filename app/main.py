# app/main.py

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI

from app.core.config import Settings, get_settings
from app.core.logging_config import configure_logging
from app.db.base import Base
from app.db.session import get_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    configure_logging()
    settings = get_settings()
    engine = get_engine(settings)
    Base.metadata.create_all(bind=engine)

    yield  # <-- the application runs here

    # Shutdown actions (none yet)
    # e.g. close DB connections or cleanup later if needed


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    def health(settings: Settings = Depends(get_settings)) -> dict:
        return {
            "status": "ok",
            "app": settings.app_name,
        }

    return app


app = create_app()
