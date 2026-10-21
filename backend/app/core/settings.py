from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Values come from environment variables, or from a local .env file.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # These are not used until later stages. The key values are never printed.
    llm_provider: str = "replace_me"
    llm_model: str = "replace_me"
    llm_api_key: SecretStr = SecretStr("")
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: SecretStr = SecretStr("")
    database_url: str = ""

    # The one browser origin allowed to call the API once CORS is added.
    frontend_origin: str = "http://localhost:3000"

    @field_validator("log_level", mode="before")
    @classmethod
    def log_level_upper(cls, value):
        if isinstance(value, str):
            return value.upper()
        return value

    @field_validator("frontend_origin", "qdrant_url")
    @classmethod
    def check_url(cls, value):
        value = value.strip().rstrip("/")
        if "*" in value:
            raise ValueError("wildcards are not allowed in a URL setting")
        if not value.startswith(("http://", "https://")):
            raise ValueError("must start with http:// or https://")
        return value

    @field_validator("database_url")
    @classmethod
    def check_database_url(cls, value):
        if value and not value.startswith("postgresql"):
            raise ValueError("must start with postgresql")
        return value

    @model_validator(mode="after")
    def check_production(self):
        if self.app_env == "production":
            if not self.frontend_origin.startswith("https://"):
                raise ValueError("FRONTEND_ORIGIN must use https in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
