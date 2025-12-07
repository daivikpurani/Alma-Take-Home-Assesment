# app/core/config.py

import logging
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def _find_env_file() -> str | None:
    """
    Find .env file relative to this config file (most reliable).
    This file is at: app/core/config.py
    Project root is: app/core/config.py -> app/core -> app -> project_root
    """
    config_file = Path(__file__)
    project_root = config_file.parent.parent.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        logger.info(f"[CONFIG] Found .env file at: {env_file}")
        return str(env_file)
    
    # Fallback: try current working directory
    try:
        cwd_env = Path.cwd() / ".env"
        if cwd_env.exists():
            logger.info(f"[CONFIG] Found .env file at: {cwd_env}")
            return str(cwd_env)
    except Exception:
        pass
    
    logger.warning("[CONFIG] No .env file found - using default values")
    return None


# Find .env file at module load time
_env_file_path = _find_env_file()


class Settings(BaseSettings):
    # Application
    app_name: str = "Leads Service"
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql://leads_user:leads_pass@localhost:5432/leads_db"

    # Auth
    internal_api_token: str = "OpWAp0HHe5BbtLWJM8PFq4xNJ44OnOuZrIjpl_9_MeE"

    # Storage
    upload_root: str = "uploads"

    # Email
    sendgrid_api_key: str = ""  # Loaded from SENDGRID_API_KEY in .env file
    company_notification_email: str = "daiiviikpurani2@gmail.com"
    attorney_email: str = "shuo@tryalma.ai"  # Loaded from ATTORNEY_EMAIL in .env file
    company_name: str | None = "Alma"

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("database_url cannot be empty")
        return v

    @field_validator("sendgrid_api_key")
    @classmethod
    def validate_sendgrid_api_key(cls, v: str) -> str:
        """Validate and strip whitespace from SendGrid API key."""
        return v.strip() if v else ""

    model_config = SettingsConfigDict(
        # Load .env file - this is the primary source for all configuration
        # Reviewer just needs to paste API keys into .env file
        env_file=_env_file_path,
        env_file_encoding="utf-8",
        # Don't ignore empty values from .env file
        env_ignore_empty=False,
        # Field names are case-sensitive, env vars are automatically converted
        # sendgrid_api_key maps to SENDGRID_API_KEY automatically
        case_sensitive=True,
        # Ignore extra fields not defined in the model
        extra="ignore",
        # Note: pydantic_settings will read from .env file automatically
        # Environment variables are NOT used - only .env file
    )

    @model_validator(mode='after')
    def validate_configuration(self):
        """Validate and log configuration after initialization."""
        # Log SendGrid API key status
        if not self.sendgrid_api_key or not self.sendgrid_api_key.strip():
            logger.warning(
                "[CONFIG] SENDGRID_API_KEY is not set in .env file. "
                "Email functionality will be disabled. "
                "Please add SENDGRID_API_KEY=your-key-here to your .env file."
            )
        else:
            masked_key = f"{self.sendgrid_api_key[:8]}..." if len(self.sendgrid_api_key) > 8 else "***"
            logger.info(f"[CONFIG] ✓ SendGrid API key loaded from .env file: {masked_key}")
        
        return self


def _load_env_file_into_dict(env_file_path: str) -> dict[str, str]:
    """Load .env file and return as dict (only from file, not OS env)."""
    env_vars = {}
    if not env_file_path:
        return env_vars
    
    try:
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    if key:
                        env_vars[key] = value
    except Exception as e:
        logger.warning(f"[CONFIG] Error reading .env file: {e}")
    
    return env_vars


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance, so we only read env once.
    Use this via FastAPI dependencies or direct calls.
    
    Settings are loaded ONLY from:
    1. .env file (primary source - reviewer just needs to paste keys here)
    2. Default values (fallback)
    
    Note: OS environment variables are NOT used - only .env file.
    """
    if _env_file_path:
        logger.info(f"[CONFIG] Loading settings from .env file: {_env_file_path}")
        
        # Load .env file manually to ensure we get the values
        env_vars = _load_env_file_into_dict(_env_file_path)
        
        # Create Settings with values from .env file
        # pydantic_settings will also try to load, but we ensure .env values are used
        settings = Settings()
        
        # If pydantic_settings didn't load from .env, manually set values
        if not settings.sendgrid_api_key and 'SENDGRID_API_KEY' in env_vars:
            logger.info("[CONFIG] Manually loading SENDGRID_API_KEY from .env file")
            settings_dict = settings.model_dump()
            settings_dict['sendgrid_api_key'] = env_vars['SENDGRID_API_KEY'].strip()
            settings = Settings.model_validate(settings_dict)
            logger.info(f"[CONFIG] ✓ Loaded SENDGRID_API_KEY from .env file: {env_vars['SENDGRID_API_KEY'][:8]}...")
    else:
        logger.warning("[CONFIG] No .env file found - using default values")
        settings = Settings()
    
    return settings
