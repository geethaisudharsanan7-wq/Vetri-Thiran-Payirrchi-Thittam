import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    """Local-only FitBuddy configuration. No external API is required."""

    app_name: str = os.getenv(
        "APP_NAME",
        "FitBuddy - Local Fitness Plan Generator",
    )

    database_url: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(BASE_DIR / 'fitbuddy.db').as_posix()}",
    )

    # LOCAL MODE — no Gemini/OpenAI/API key
    ai_mode: str = "local"

    admin_username: str = os.getenv(
        "ADMIN_USERNAME",
        "admin",
    )

    admin_password: str = os.getenv(
        "ADMIN_PASSWORD",
        "change-me",
    )


settings = Settings()