"""
Точка входа {context}_data.

Создание и настройка FastAPI приложения.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI

from src.core.config import settings
from src.core.logging import setup_logging
from src.core.database import engine
from src.api.v1.router import api_router


logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Управление жизненным циклом приложения.

    Инициализация и закрытие ресурсов.
    """
    # === Startup ===
    logger.info(
        "Запуск приложения",
        app_name=settings.app_name,
        environment=settings.app_env,
    )

    yield

    # === Shutdown ===
    logger.info("Остановка приложения")

    # Закрытие подключения к БД
    await engine.dispose()
    logger.info("Подключение к БД закрыто")


def create_app() -> FastAPI:
    """
    Создать экземпляр FastAPI приложения.

    Returns:
        Настроенное FastAPI приложение.
    """
    # Настройка логирования
    setup_logging(
        log_level=settings.log_level,
        json_logs=settings.app_env != "development",
    )

    # Создание приложения
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="PostgreSQL Data API сервис",
        root_path=settings.root_path,  # Reverse proxy support
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Подключение роутеров
    app.include_router(api_router, prefix="/api/v1")

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict:
        """Проверка состояния сервиса."""
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": "1.0.0",
        }

    return app


# Создание приложения
app = create_app()
