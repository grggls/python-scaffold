"""Application configuration via environment variables."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Immutable application settings loaded from environment variables."""

    app_name: str = "myproject"
    debug: bool = False
    log_level: str = "INFO"


def get_settings() -> Settings:
    """Create a Settings instance from environment variables.

    Environment variables:
        APP_NAME: Application name (default: "myproject")
        DEBUG: Enable debug mode (default: "false")
        LOG_LEVEL: Logging level (default: "INFO")
    """
    return Settings(
        app_name=os.environ.get("APP_NAME", "myproject"),
        debug=os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes"),
        log_level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    )
