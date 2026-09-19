from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    llm_provider: str = "gemini"
    gemini_model: str = Field(default="gemini-2.0-flash", validation_alias="GEMINI_MODEL")
    gemini_timeout_seconds: float = 30.0
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_file_size_bytes: int = 256_000
    max_repository_size_bytes: int = 5_000_000
    max_repository_files: int = 1_000
    max_context_characters: int = 24_000
    log_level: str = "INFO"
    auth_database_url: str = Field(default="sqlite:///./.forgeai_auth.db", validation_alias="AUTH_DATABASE_URL")
    auth_session_secret: str = Field(default="", validation_alias="AUTH_SESSION_SECRET")
    auth_cookie_name: str = Field(default="forgeai_session", validation_alias="AUTH_COOKIE_NAME")
    auth_cookie_secure: bool = Field(default=False, validation_alias="AUTH_COOKIE_SECURE")
    auth_session_max_age_seconds: int = Field(default=604_800, validation_alias="AUTH_SESSION_MAX_AGE_SECONDS")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
