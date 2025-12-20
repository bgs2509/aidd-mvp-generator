"""
Конфигурация {context}_worker.

Загрузка настроек из переменных окружения.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки воркера."""

    # === Воркер ===
    worker_name: str = "{context}_worker"

    # === Business API ===
    business_api_url: str = "http://business-api:8000"
    business_api_timeout: float = 30.0

    # === Задачи ===
    task_interval_seconds: int = 60

    # === Логирование ===
    log_level: str = "INFO"

    class Config:
        """Конфигурация Pydantic."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Синглтон настроек
settings = Settings()
