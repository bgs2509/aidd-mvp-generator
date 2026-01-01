"""
Конфигурация {context}_data.

Загрузка настроек из переменных окружения.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    # === Приложение ===
    app_name: str = "{context}_data"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # === Reverse Proxy ===
    root_path: str = ""  # Путевой префикс (например, "/my-service")

    # === MongoDB ===
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "{context}_db"

    class Config:
        """Конфигурация Pydantic."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Синглтон настроек
settings = Settings()
