from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class WebdriverSettings(BaseModel):
    host: str
    port: str


class AnnouncementSettings(BaseModel):
    base_url: str
    feed_url: str
    base_announcement_url: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CAB_", env_nested_delimiter="__")

    allowed_origins: list[str]
    ann: AnnouncementSettings
    web_driver: WebdriverSettings


@lru_cache()
def get_settings() -> Settings:
    """Used to return the Settings as a Singleton."""

    return Settings()
