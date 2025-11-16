"""
Configuration management for the Email Drafting Tool.
Loads settings from .env file and provides access throughout the application.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Project paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    CACHE_DIR: Path = BASE_DIR / "cache"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # Microsoft Graph API
    AZURE_CLIENT_ID: str = Field(..., description="Azure AD application client ID")
    AZURE_TENANT_ID: str = Field(default="common", description="Azure AD tenant ID")
    AZURE_REDIRECT_URI: str = Field(
        default="http://localhost:8000/callback",
        description="OAuth redirect URI"
    )
    AZURE_AUTHORITY: str = Field(default="", description="Azure AD authority URL")
    AZURE_SCOPES: list[str] = Field(
        default=[
            "User.Read",
            "Mail.Read",
            "Mail.ReadWrite",
            "Mail.Send"
        ],
        description="Microsoft Graph API scopes"
    )

    # AI Service
    ANTHROPIC_API_KEY: str = Field(..., description="Anthropic API key for Claude")
    ANTHROPIC_MODEL: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Claude model to use"
    )
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key (alternative)")
    OPENAI_MODEL: Optional[str] = Field(default="gpt-4", description="OpenAI model (alternative)")

    # Database
    DATABASE_PATH: str = Field(
        default="./data/emailv2.db",
        description="Path to SQLite database"
    )

    # Application settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: str = Field(default="./logs/app.log", description="Log file path")
    DEBUG_MODE: bool = Field(default=False, description="Enable debug mode")

    # Email fetching
    AUTO_FETCH_INTERVAL: int = Field(
        default=300,
        description="Auto-fetch interval in seconds"
    )
    MAX_EMAILS_PER_FETCH: int = Field(
        default=20,
        description="Maximum emails to fetch per request"
    )
    INITIAL_STYLE_LEARNING_EMAILS: int = Field(
        default=200,
        description="Number of sent emails to analyze for initial style learning"
    )

    # UI Settings
    THEME: str = Field(default="dark", description="UI theme (light/dark)")
    WINDOW_WIDTH: int = Field(default=1200, description="Main window width")
    WINDOW_HEIGHT: int = Field(default=800, description="Main window height")

    # Hotkeys
    DEFAULT_HOTKEY_SHOW: str = Field(default="ctrl+alt+e", description="Show window hotkey")
    DEFAULT_HOTKEY_DRAFT: str = Field(default="ctrl+alt+d", description="Generate draft hotkey")
    DEFAULT_HOTKEY_REFINE: str = Field(default="ctrl+alt+r", description="Refine draft hotkey")
    DEFAULT_HOTKEY_COPY: str = Field(default="ctrl+alt+c", description="Copy draft hotkey")

    # AI Draft settings
    DEFAULT_DRAFT_LENGTH: str = Field(default="medium", description="Default draft length")
    ENABLE_GRAMMAR_CHECK: bool = Field(default=True, description="Enable grammar checking")
    CORPORATE_BEST_PRACTICES: bool = Field(
        default=True,
        description="Apply corporate email best practices"
    )

    # Privacy settings
    ENABLE_STYLE_LEARNING: bool = Field(default=True, description="Enable style learning")
    EXCLUDE_SENDERS: str = Field(default="", description="Comma-separated list of senders to exclude")
    CLEAR_CACHE_ON_EXIT: bool = Field(default=False, description="Clear cache on application exit")

    # Development/Testing
    MOCK_GRAPH_API: bool = Field(default=False, description="Use mock Graph API (for testing)")
    MOCK_AI_API: bool = Field(default=False, description="Use mock AI API (for testing)")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Build Azure authority URL if not provided
        if not self.AZURE_AUTHORITY:
            self.AZURE_AUTHORITY = f"https://login.microsoftonline.com/{self.AZURE_TENANT_ID}"

        # Ensure directories exist
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    @property
    def database_url(self) -> str:
        """Get SQLAlchemy database URL."""
        db_path = Path(self.DATABASE_PATH).absolute()
        return f"sqlite:///{db_path}"

    def get_excluded_senders(self) -> list[str]:
        """Parse and return list of excluded senders."""
        if not self.EXCLUDE_SENDERS:
            return []
        return [email.strip() for email in self.EXCLUDE_SENDERS.split(",")]


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global settings
    if settings is None:
        settings = Settings()
    return settings


def reload_settings():
    """Reload settings from environment file."""
    global settings
    settings = Settings()
    return settings
