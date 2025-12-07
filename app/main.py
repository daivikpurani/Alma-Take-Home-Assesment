# app/main.py

import traceback
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from app.core.config import Settings, get_settings
from app.core.logging_config import configure_logging
from app.db.base import Base
from app.db.session import get_engine

from app.api.public.leads import router as public_leads_router
from app.api.internal.leads import router as internal_leads_router

logger = logging.getLogger(__name__)


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

    # Global exception handler for unhandled exceptions
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        Catch-all exception handler that logs full stack traces
        and returns appropriate error responses.
        """
        logger.error(
            f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
            exc_info=True,  # This includes full stack trace
            extra={
                "path": request.url.path,
                "method": request.method,
            }
        )
        
        # In production, you might want to hide internal error details
        # For now, we'll include the error type for debugging
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An internal server error occurred",
                "error_type": type(exc).__name__,
                # Only include traceback in development/debug mode
                "traceback": traceback.format_exc() if settings.log_level == "DEBUG" else None
            }
        )

    # Handler for validation errors (Pydantic)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle request validation errors with proper logging.
        """
        logger.warning(
            f"Validation error: {exc.errors()}",
            extra={
                "path": request.url.path,
                "method": request.method,
            }
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()}
        )

    @app.get("/health", status_code=status.HTTP_200_OK)
    def health(settings: Settings = Depends(get_settings)) -> dict:
        return {
            "status": "ok",
            "app": settings.app_name,
        }
        
    app.include_router(public_leads_router, prefix="/public")
    app.include_router(internal_leads_router, prefix="/api/internal")

    return app

app = create_app()
