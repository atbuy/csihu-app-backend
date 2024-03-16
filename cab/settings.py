from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class AnnouncementSettings(BaseModel):
    base_url: str
    feed_url: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CAB_", env_nested_delimiter="__")

    ann: AnnouncementSettings


@lru_cache()
def get_settings() -> Settings:
    """Used to return the Settings as a Singleton."""

    return Settings()
