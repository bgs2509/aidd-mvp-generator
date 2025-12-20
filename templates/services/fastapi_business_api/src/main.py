"""
Точка входа {context}_api.

Создание и настройка FastAPI приложения.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.logging import setup_logging
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

    # Создание HTTP клиента для Data API
    app.state.http_client = httpx.AsyncClient(
        base_url=settings.data_api_url,
        timeout=httpx.Timeout(settings.data_api_timeout),
    )
    logger.info("HTTP клиент создан", base_url=settings.data_api_url)

    yield

    # === Shutdown ===
    logger.info("Остановка приложения")

    # Закрытие HTTP клиента
    await app.state.http_client.aclose()
    logger.info("HTTP клиент закрыт")


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
        description="Business API сервис",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
