# app/core/config.py

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "Leads Service"
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql://leads_user:leads_pass@localhost:5432/leads_db"

    # Auth
    internal_api_token: str = "secret-token"

    # Storage
    upload_root: str = "uploads"

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("database_url cannot be empty")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",          # optional: load from .env if present
        env_file_encoding="utf-8",
        extra="ignore",           # ignore unexpected env vars
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance, so we only read env once.
    Use this via FastAPI dependencies or direct calls.
    """
    return Settings()