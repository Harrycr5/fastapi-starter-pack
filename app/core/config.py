from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


# Raíz del proyecto: contiene el archivo .env
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Aplicación
    app_name: str = "FastAPI Starter"
    app_version: str = "0.1.0"
    environment: Literal["development", "testing", "production"] = "development"
    debug: bool = False

    # Base de datos
    database_url: PostgresDsn

    # Redis
    redis_url: RedisDsn = RedisDsn("redis://localhost:6379/0")

    # Autenticación
    jwt_secret_key: str = Field(min_length=32, repr=False)
    jwt_algorithm: Literal["HS256"] = "HS256"
    access_token_expire_minutes: int = Field(default=15, gt=0)
    refresh_token_expire_days: int = Field(default=7, gt=0)


@lru_cache
def get_settings() -> Settings:
    return Settings()

