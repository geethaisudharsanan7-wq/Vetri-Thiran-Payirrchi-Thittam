import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Local-only FitBuddy configuration."""

    app_name: str = os.getenv(
        "APP_NAME",
        "FitBuddy - Local Fitness Plan Generator",
    )

    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./fitbuddy.db",
    )

    # Local-only build: no Gemini/OpenAI/API key is required.
    ai_mode: str = "local"

    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "change-me")


settings = Settings()