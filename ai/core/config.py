"""Configuration management via Pydantic settings."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration loaded from .env file only (not environment variables)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_ignore_empty=True,  # Ignore empty env vars
        env_prefix="",  # No prefix
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,  # noqa: ARG003
        init_settings,  # noqa: ARG003
        env_settings,  # noqa: ARG003
        dotenv_settings,
        file_secret_settings,  # noqa: ARG003
    ):
        """Customize settings sources to ONLY use .env file, not environment variables."""
        # Return only dotenv_settings (the .env file)
        # This ignores environment variables completely
        return (dotenv_settings,)

    # LLM API Keys
    openrouter_api_key: str = Field(default="", description="OpenRouter API key")

    # Observability
    logfire_token: str = Field(
        default="", description="Logfire token for observability"
    )
    log_level: str = Field(default="INFO", description="Logging level")

    # Future: Data Source APIs
    limitless_api_key: str = Field(default="", description="Limitless AI API key")
    fireflies_api_key: str = Field(default="", description="Fireflies AI API key")
    notion_api_key: str = Field(default="", description="Notion API key")
    clickup_api_key: str = Field(default="", description="ClickUp API key")

    # Paths
    agents_dir: Path = Field(
        default=Path("ai/agents"), description="Agent definitions directory"
    )

    @property
    def demo_mode(self) -> bool:
        """Check if running in demo mode (no API keys configured)."""
        return not self.openrouter_api_key


# Global config instance
config = Config()
