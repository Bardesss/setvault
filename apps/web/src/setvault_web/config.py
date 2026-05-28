from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = Field(default="dev-only-do-not-use-in-prod", min_length=16)
    database_url: str = "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault"
    redis_url: str = "redis://localhost:6379/0"
    base_url: str = "http://localhost:1970"
    tusd_hook_secret: str = "dev-tusd-secret"  # noqa: S105
    allow_1001tl_scrape: bool = Field(default=False, alias="SETVAULT_ALLOW_1001TL_SCRAPE")


@lru_cache
def get_settings() -> Settings:
    return Settings()
