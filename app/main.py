# app/main.py

from fastapi import Depends, FastAPI

from app.core.config import Settings, get_settings


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
    )

    @app.get("/health")
    def health(settings: Settings = Depends(get_settings)) -> dict:
        return {
            "status": "ok",
            "app": settings.app_name,
        }

    return app


app = create_app()
