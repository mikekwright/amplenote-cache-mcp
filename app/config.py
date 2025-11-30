"""
Configuration management for Amplenote MCP Server.

Uses pydantic-settings to load configuration from environment variables
with sensible defaults.
"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


_settings: "Settings | None" = None


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    Configuration values can be overridden by environment variables.
    For example, AMPLENOTE_DB_PATH environment variable will override db_path.
    """

    model_config = SettingsConfigDict(
        env_prefix="AMPLENOTE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database configuration
    db_path: Path = Field(
        default=Path.home() / ".config/ample-electron/amplenote.db",
        description="Path to the Amplenote SQLite database file"
    )

    # Query limits
    default_search_limit: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Default limit for search results"
    )

    default_list_limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Default limit for list operations"
    )

    max_query_limit: int = Field(
        default=1000,
        ge=1,
        description="Maximum allowed query limit"
    )


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
