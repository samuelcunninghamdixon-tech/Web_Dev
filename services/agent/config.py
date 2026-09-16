from pathlib import Path

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
    slack_signing_secret: str = ""
    slack_review_channel: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def public_metadata(self) -> dict[str, str]:
        return {
            "service": self.service_name,
            "environment": self.environment,
        }