"""
Точка входа {context}_api.

Создание и настройка FastAPI приложения.
"""

import hashlib
import sys
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.logging import setup_logging
from src.api.v1.router import api_router
from src.middlewares import RequestLoggingMiddleware
from shared.utils.log_helpers import log_service_started, log_service_stopped


logger = structlog.get_logger()


# Время запуска для расчёта uptime
_startup_time: float | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Управление жизненным циклом приложения.

    Инициализация и закрытие ресурсов.
    """
    global _startup_time
    _startup_time = time.time()

    # === Startup ===
    # Полное логирование контекста при старте (Log-Driven Design)
    log_service_started(
        logger,
        service_name=settings.app_name,
        service_version=getattr(settings, "app_version", "1.0.0"),
        environment=settings.app_env,
        python_version=sys.version.split()[0],
        feature_flags={
            "debug": settings.debug,
        },
        dependencies={
            "data_api": settings.data_api_url,
        },
        config_hash=hashlib.md5(
            settings.model_dump_json().encode()
        ).hexdigest()[:8],
    )

    # Создание HTTP клиента для Data API
    app.state.http_client = httpx.AsyncClient(
        base_url=settings.data_api_url,
        timeout=httpx.Timeout(settings.data_api_timeout),
    )
    logger.info("http_client_created", base_url=settings.data_api_url)

    yield

    # === Shutdown ===
    uptime = time.time() - _startup_time if _startup_time else None
    log_service_stopped(
        logger,
        service_name=settings.app_name,
        reason="shutdown",
        uptime_seconds=uptime,
    )

    # Закрытие HTTP клиента
    await app.state.http_client.aclose()
    logger.info("http_client_closed")


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
        root_path=settings.root_path,  # Reverse proxy support
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # === Middleware (порядок важен!) ===

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request Logging middleware (Log-Driven Design)
    # Должен быть после CORS, чтобы логировать только валидные запросы
    app.add_middleware(
        RequestLoggingMiddleware,
        skip_paths={"/health", "/metrics", "/ready"},
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
