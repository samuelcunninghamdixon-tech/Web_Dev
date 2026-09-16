from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "Agency Agent Service"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://agency:agency@localhost:5432/agency"
    ollama_base_url: str = "http://localhost:11434"
    shared_screenshots_dir: Path = Path("/shared/screenshots")
    shared_assets_dir: Path = Path("/shared/assets")
    shared_exports_dir: Path = Path("/shared/exports")
    shared_generated_sites_dir: Path = Path("/shared/generated-sites")
    review_platform: str = "discord"
    discord_bot_token: str = ""
    discord_application_id: str = ""
    discord_public_key: str = ""
    discord_review_channel_id: str = ""
    discord_review_guild_id: str = ""
    discord_interaction_url: str = ""
    slack_signing_secret: str = ""
    slack_review_channel: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator(
        "discord_bot_token",
        "discord_application_id",
        "discord_public_key",
        "discord_review_channel_id",
        "discord_review_guild_id",
        "discord_interaction_url",
        "slack_signing_secret",
        mode="before",
    )
    @classmethod
    def ignore_placeholders(cls, value: str) -> str:
        if isinstance(value, str) and value.lower() in {"replace-me", "change-me", ""}:
            return ""
        return value

    def public_metadata(self) -> dict[str, str]:
        return {
            "service": self.service_name,
            "environment": self.environment,
        }