# tests/conftest.py

import pytest
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import Mock, patch

from app.main import create_app
from app.db.base import Base, load_models
from app.core.config import Settings, get_settings
from app.services.email_service import EmailService
from app.storage.storage_service import StorageService


# Test database URL - SQLite in-memory
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db_session() -> Generator[Session, None, None]:
    """
    Create a fresh in-memory database for each test.
    """
    # Load models to ensure all tables are registered
    load_models()
    
    # Create engine and session
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def test_settings() -> Settings:
    """
    Create test settings with in-memory database and test API token.
    """
    return Settings(
        app_name="Leads Service Test",
        log_level="DEBUG",
        database_url=TEST_DATABASE_URL,
        internal_api_token="test_token_123",
        upload_root="test_uploads",
        sendgrid_api_key="",  # Empty to prevent actual email sends
        company_notification_email="test@example.com",
        company_name="Test Company",
    )


@pytest.fixture(scope="function")
def mock_email_service():
    """
    Mock EmailService to prevent actual email sends during tests.
    """
    with patch.object(EmailService, "send_email") as mock_send_email:
        yield mock_send_email


@pytest.fixture(scope="function")
def mock_storage_service():
    """
    Mock StorageService to avoid actual file system operations.
    """
    mock_storage = Mock(spec=StorageService)
    
    # Make save async
    async def async_save(file, filename=None):
        return "test_uploads/mock_resume.pdf"
    
    mock_storage.save = async_save
    return mock_storage


@pytest.fixture(scope="function")
def test_client(
    test_db_session: Session,
    mock_storage_service,
    test_settings: Settings,
) -> TestClient:
    """
    Create a test client with overridden dependencies.
    """
    # Clear the LRU cache to prevent cached production settings
    get_settings.cache_clear()
    
    # Patch get_settings before create_app() is called
    # This ensures lifespan and create_app() use test settings
    with patch('app.core.config.get_settings', return_value=test_settings):
        with patch('app.main.get_settings', return_value=test_settings):
            app = create_app()
    
    # Override dependencies for FastAPI dependency injection
    from app.api.deps import get_db, get_storage
    
    def _get_db_override():
        try:
            yield test_db_session
        finally:
            pass
    
    def _get_storage_override():
        return mock_storage_service
    
    def _get_settings_override():
        return test_settings
    
    app.dependency_overrides[get_settings] = _get_settings_override
    app.dependency_overrides[get_db] = _get_db_override
    app.dependency_overrides[get_storage] = _get_storage_override
    
    with TestClient(app) as client:
        yield client
    
    # Clean up overrides and cache
    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture(scope="function")
async def async_test_client(
    test_db_session: Session,
    mock_storage_service,
    test_settings: Settings,
) -> AsyncClient:
    """
    Create an async test client with overridden dependencies.
    """
    app = create_app()
    
    # Override dependencies
    from app.api.deps import get_db, get_storage
    
    def _get_db_override():
        try:
            yield test_db_session
        finally:
            pass
    
    def _get_storage_override():
        return mock_storage_service
    
    def _get_settings_override():
        return test_settings
    
    app.dependency_overrides[get_settings] = _get_settings_override
    app.dependency_overrides[get_db] = _get_db_override
    app.dependency_overrides[get_storage] = _get_storage_override
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up overrides
    app.dependency_overrides.clear()
