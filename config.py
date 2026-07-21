"""Typed settings for the affiliate support bot, loaded from .env."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str

    knowledge_base_file: Path = Path("knowledge_base/affiliate_program_faq.pdf")
    vector_store_id: str | None = None
    vector_store_name: str = "affiliate-support-kb"

    assistant_name: str = "Affiliate Support Bot"
    assistant_model: str = "gpt-4.1-mini"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def get_settings() -> Settings:
    return Settings()
