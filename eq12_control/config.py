#!/usr/bin/env python3
"""
EQ12 Control Plane Configuration
===============================

SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2025 EQ12 Project Contributors

Settings loaded from environment variables with secure defaults.
"""

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # Database
    database_url: str = "sqlite:///./eq12_control.db"
    database_echo: bool = False

    # Security
    jwt_secret_key: str = "change-in-production-use-32-char-random"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    cors_allow_credentials: bool = True

    # Rate Limiting
    redis_url: str | None = None  # Use in-memory if not provided

    # Billing Providers
    paypal_client_id: str | None = None
    paypal_client_secret: str | None = None
    paypal_sandbox: bool = True

    cashapp_api_key: str | None = None
    venmo_api_key: str | None = None

    # Webhooks
    webhook_timeout: int = 5  # seconds
    webhook_replay_window: int = 300  # 5 minutes

    # Plans & Limits
    default_plan: str = "starter"

    # Server settings
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8001

    # Frontend
    frontend_url: str = "http://localhost:3000"

    # Admin
    admin_email: str = "admin@eq12.local"

    # Observability
    prometheus_enabled: bool = True
    log_level: str = "INFO"

    @field_validator("jwt_secret_key")
    @classmethod
    def jwt_key_must_be_secure(cls, v):
        if v == "change-in-production-use-32-char-random":
            import warnings

            warnings.warn(
                "Using default JWT secret! Set JWT_SECRET_KEY environment variable.",
                UserWarning,
                stacklevel=2,
            )
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_prefix = "EQ12_"
        case_sensitive = False


settings = Settings()
