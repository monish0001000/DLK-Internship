"""
SentinelX EDR - Application Configuration
==========================================
Centralized configuration management using Pydantic BaseSettings.
All settings can be overridden via environment variables or a .env file.

Sections:
    - Application settings (name, debug, CORS)
    - Database (SQLite default, PostgreSQL ready)
    - AI providers (Gemini primary, OpenRouter fallback)
    - Threat Intelligence feeds (all optional)
    - Detection engine (plugin dir, collection interval)
    - Security (API key, JWT)
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    
    Priority: env vars > .env file > defaults
    
    To switch to PostgreSQL, set:
        DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/sentinelx
    """

    # ── Application ─────────────────────────────────────────────
    APP_NAME: str = "SentinelX EDR"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    LOG_LEVEL: str = "INFO"
    DEMO_MODE: bool = False  # Seeds sample data on startup
    API_V1_STR: str = "/api/v1"

    # ── Database ────────────────────────────────────────────────
    # SQLite for development (zero-config), swap to PostgreSQL for production
    DATABASE_URL: str = "sqlite:///./sentinelx.db"

    # ── AI Providers ────────────────────────────────────────────
    # Gemini (primary) - get free key at https://aistudio.google.com/apikey
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # OpenRouter (fallback) - get free key at https://openrouter.ai/keys
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "google/gemini-2.0-flash-exp:free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # ── Threat Intelligence Feeds (all optional) ────────────────
    ABUSEIPDB_API_KEY: Optional[str] = None
    OTX_API_KEY: Optional[str] = None
    # MalwareBazaar is keyless (public API)
    TI_SYNC_INTERVAL_HOURS: int = 4  # How often to sync feeds

    # ── Detection Engine ────────────────────────────────────────
    PLUGIN_DIR: str = "./app/plugins/examples"
    SIGMA_RULES_DIR: str = "./app/data/sigma_rules"
    COLLECTION_INTERVAL_SECONDS: int = 60
    MAX_EVENTS_PER_WINDOW: int = 100  # Behavioral detector window size

    # ── Security ────────────────────────────────────────────────
    API_KEY: Optional[str] = None  # If set, endpoints require this key
    JWT_SECRET: str = "sentinelx-change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 15  # 15 minutes for access token
    JWT_REFRESH_EXPIRATION_DAYS: int = 7 # 7 days for refresh token
    SECRET_KEY: str = "sentinelx-secret-change-me-in-production" # Used in auth.py
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    # ── Agent ───────────────────────────────────────────────────
    AGENT_HEARTBEAT_TIMEOUT_SECONDS: int = 300  # 5 min = offline

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings singleton.
    Call get_settings() anywhere to access configuration.
    The lru_cache ensures only one Settings instance is created.
    """
    return Settings()
