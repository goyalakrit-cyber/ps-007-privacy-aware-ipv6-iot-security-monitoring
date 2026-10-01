from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Privacy-Aware IPv6 IoT Security Monitoring"
    APP_ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./data/ipv6_monitor.db"
    SECRET_KEY: str = "change-me-in-production"
    MAX_ALERTS: int = 500

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
