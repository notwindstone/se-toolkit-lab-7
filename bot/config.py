"""
Configuration loader for the LMS Bot.

Loads secrets from environment variables (typically set via .env.bot.secret).
Uses pydantic-settings for validation and type coercion.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root is one level up from bot/
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env.bot.secret"


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    bot_token: str = ""

    # LMS API
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = ""

    # LLM API (for Task 3)
    llm_api_model: str = "coder-model"
    llm_api_key: str = ""
    llm_api_base_url: str = ""


# Global settings instance (loaded once at import time)
settings = BotSettings()
