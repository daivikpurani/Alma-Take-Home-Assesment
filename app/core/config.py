# app/core/config.py

import os
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> str | None:
    """Find .env file in current directory or parent directory."""
    # Try current directory first
    current_dir = Path.cwd() / ".env"
    if current_dir.exists():
        print(f"[CONFIG] Found .env file at: {current_dir}")
        return str(current_dir)
    
    # Try parent directory
    parent_dir = current_dir.parent / ".env"
    if parent_dir.exists():
        print(f"[CONFIG] Found .env file at: {parent_dir}")
        return str(parent_dir)
    
    # Try relative to this file
    file_dir = Path(__file__).parent.parent.parent / ".env"
    if file_dir.exists():
        print(f"[CONFIG] Found .env file at: {file_dir}")
        return str(file_dir)
    
    # Try parent of file directory
    parent_file_dir = file_dir.parent / ".env"
    if parent_file_dir.exists():
        print(f"[CONFIG] Found .env file at: {parent_file_dir}")
        return str(parent_file_dir)
    
    print(f"[CONFIG] No .env file found, using default: .env")
    return ".env"  # Default fallback


class Settings(BaseSettings):
    # Application
    app_name: str = "Leads Service"
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql://leads_user:leads_pass@localhost:5432/leads_db"

    # Auth
    internal_api_token: str = "abc123"

    # Storage
    upload_root: str = "uploads"

    # Email
    sendgrid_api_key: str = ""
    company_notification_email: str = "daiiviikpurani2@gmail.com"
    company_name: str | None = "Alma"

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("database_url cannot be empty")
        return v

    model_config = SettingsConfigDict(
        # Try .env in current directory, then parent directory
        env_file=_find_env_file(),
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