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

    # === База данных ===
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/{context}_db"

    # === Пул соединений ===
    db_pool_size: int = 5
    db_max_overflow: int = 10

    class Config:
        """Конфигурация Pydantic."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Синглтон настроек
settings = Settings()
