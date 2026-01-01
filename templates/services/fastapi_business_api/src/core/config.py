"""
Конфигурация {context}_api.

Загрузка настроек из переменных окружения.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    # === Приложение ===
    app_name: str = "{context}_api"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # === Reverse Proxy ===
    root_path: str = ""  # Путевой префикс (например, "/my-service")

    # === Data API ===
    data_api_url: str = "http://data-api:8001"
    data_api_timeout: float = 30.0

    # === Redis (опционально) ===
    redis_url: str = "redis://redis:6379/0"

    # === CORS ===
    cors_origins: list[str] = ["*"]

    class Config:
        """Конфигурация Pydantic."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Синглтон настроек
settings = Settings()
