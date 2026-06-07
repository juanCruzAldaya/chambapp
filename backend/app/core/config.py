from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la app, cargada desde variables de entorno / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "LaburApp API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "local"

    # Base de datos
    DATABASE_URL: str = (
        "postgresql+psycopg2://laburapp:laburapp@localhost:5432/laburappdb"
    )

    # Seguridad
    SECRET_KEY: str = "changeme"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 día

    # CORS. NoDecode evita que pydantic-settings intente parsear el valor del
    # env var como JSON (vendría como CSV); lo separa nuestro validador de abajo.
    BACKEND_CORS_ORIGINS: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
