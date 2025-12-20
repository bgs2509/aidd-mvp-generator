"""
Конфигурация {context}_bot.

Загрузка настроек из переменных окружения.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки бота."""

    # === Бот ===
    bot_name: str = "{context}_bot"
    telegram_bot_token: str

    # === Business API ===
    business_api_url: str = "http://business-api:8000"
    business_api_timeout: float = 30.0

    # === Redis ===
    redis_url: str = "redis://redis:6379/0"

    # === Логирование ===
    log_level: str = "INFO"

    class Config:
        """Конфигурация Pydantic."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Синглтон настроек
settings = Settings()
