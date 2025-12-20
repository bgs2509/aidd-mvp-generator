# Фабрика приложений FastAPI

> **Назначение**: Паттерн создания FastAPI приложения.

---

## Базовый паттерн

```python
"""Фабрика приложения FastAPI."""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from {context}_api.api.v1.router import api_router
from {context}_api.core.config import settings
from {context}_api.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    setup_logging()
    yield
    # Shutdown


def create_app() -> FastAPI:
    """
    Создать экземпляр FastAPI приложения.

    Returns:
        Настроенное FastAPI приложение.
    """
    app = FastAPI(
        title=settings.service_name,
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Подключение роутеров
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
```

---

## С HTTP клиентом

```python
"""Фабрика с управлением HTTP клиентом."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx

from {context}_api.api.v1.router import api_router
from {context}_api.core.config import settings
from {context}_api.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом."""
    setup_logging()

    # Создание HTTP клиента
    app.state.http_client = httpx.AsyncClient(
        base_url=settings.data_api_url,
        timeout=httpx.Timeout(30.0),
    )

    yield

    # Закрытие HTTP клиента
    await app.state.http_client.aclose()


def create_app() -> FastAPI:
    """Создать приложение."""
    app = FastAPI(
        title=settings.service_name,
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
```

---

## Middleware

```python
"""Добавление middleware."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid


def create_app() -> FastAPI:
    """Создать приложение с middleware."""
    app = FastAPI(
        title=settings.service_name,
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID middleware
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """Добавить request_id к запросу."""
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response

    # Timing middleware
    @app.middleware("http")
    async def add_timing(request: Request, call_next):
        """Измерить время обработки запроса."""
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        return response

    app.include_router(api_router, prefix="/api/v1")

    return app
```

---

## Health Check

```python
"""Health check эндпоинт."""

from fastapi import APIRouter, Response

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """
    Проверка состояния сервиса.

    Returns:
        Статус сервиса.
    """
    return {"status": "healthy"}


@router.get("/ready")
async def readiness_check() -> dict:
    """
    Проверка готовности сервиса.

    Returns:
        Статус готовности.
    """
    # Здесь можно добавить проверку зависимостей
    return {"status": "ready"}
```

---

## Структура main.py

```
main.py
├── Импорты
├── lifespan() — управление жизненным циклом
├── create_app() — фабрика приложения
│   ├── Создание FastAPI
│   ├── Добавление middleware
│   └── Подключение роутеров
└── app = create_app()
```

---

## Чек-лист

- [ ] Используется lifespan для startup/shutdown
- [ ] HTTP клиент создаётся в lifespan
- [ ] Docs отключены в production
- [ ] Request ID middleware добавлен
- [ ] Health check эндпоинт есть
