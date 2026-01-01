"""
Конфигурация {context}_data.

Загрузка настроек из переменных окружения.
"""

from pydantic import Field
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

    # === База данных ===
    # SECURITY: Нет default значения с credentials!
    # Обязательно установить через DATABASE_URL в .env
    database_url: str = Field(
        default="postgresql+asyncpg://localhost:5432/{context}_db",
        description="Database URL. ОБЯЗАТЕЛЬНО установите credentials через переменную окружения DATABASE_URL",
    )

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
