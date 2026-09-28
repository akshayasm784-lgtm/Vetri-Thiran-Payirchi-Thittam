from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "FitBuddy – AI Fitness Plan Generator"

    environment: str = "development"

    debug: bool = True

    database_url: str = (
        f"sqlite:///{(BASE_DIR / 'data' / 'fitbuddy.db').as_posix()}"
    )

    gemini_api_key: str | None = None

    # Keep these configurable because Gemini model availability can change.
    gemini_workout_model: str = "gemini-3.5-flash-lite"

    gemini_tip_model: str = "gemini-3.5-flash-lite"

    # Set MOCK_AI=true if you want to run the application
    # without making Gemini API calls.
    mock_ai: bool = False

    # Reserved for future authentication.
    admin_token: str | None = None

    max_feedback_length: int = 1200

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()