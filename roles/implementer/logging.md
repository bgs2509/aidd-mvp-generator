# Функция: Логирование (Level ≥ 2)

> **Назначение**: Настройка структурированного логирования.

---

## Цель

Настроить структурированное логирование с использованием structlog
для всех сервисов проекта.

---

## Требования к логированию (Level 2)

```
ОБЯЗАТЕЛЬНО:
✓ Структурированные логи (JSON)
✓ Уровни логирования (DEBUG, INFO, WARNING, ERROR)
✓ Request ID для трассировки
✓ Контекстная информация

НЕ ТРЕБУЕТСЯ (Level 3+):
✗ Centralized logging (ELK)
✗ Log aggregation
✗ Alerting
```

---

## Компоненты

### 1. Настройка structlog (core/logging.py)

```python
"""Настройка структурированного логирования."""

import logging
import sys
from typing import Any

import structlog

from {context}_{service}.core.config import settings


def setup_logging() -> None:
    """Настроить логирование для сервиса."""

    # Уровень логирования
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Процессоры structlog
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.debug:
        # Красивый вывод для разработки
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # JSON для продакшена
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

    # Настройка structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Настройка стандартного logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Уровень для сторонних библиотек
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Получить логгер с заданным именем."""
    return structlog.get_logger(name)
```

### 2. Request ID Middleware (middlewares/request_id.py)

```python
"""Middleware для генерации и отслеживания Request ID."""

import uuid
from typing import Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления Request ID к каждому запросу."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Обработать запрос с Request ID."""
        # Получить или сгенерировать Request ID
        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4()),
        )

        # Добавить в контекст structlog
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
        )

        # Сохранить в state для использования в handlers
        request.state.request_id = request_id

        # Выполнить запрос
        response = await call_next(request)

        # Добавить Request ID в заголовки ответа
        response.headers["X-Request-ID"] = request_id

        return response
```

### 3. Logging Middleware (middlewares/logging.py)

```python
"""Middleware для логирования HTTP запросов."""

import time
from typing import Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов и ответов."""

    def __init__(self, app, logger_name: str = "http"):
        """Инициализация middleware."""
        super().__init__(app)
        self.logger = structlog.get_logger(logger_name)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Логировать запрос и ответ."""
        start_time = time.perf_counter()

        # Логируем входящий запрос
        self.logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query=str(request.query_params),
            client_ip=request.client.host if request.client else None,
        )

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Логируем успешный ответ
            self.logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Логируем ошибку
            self.logger.exception(
                "request_failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=round(duration_ms, 2),
            )
            raise
```

### 4. Подключение middleware (main.py)

```python
"""Точка входа с настроенным логированием."""

from fastapi import FastAPI

from {context}_{service}.core.logging import setup_logging
from {context}_{service}.middlewares.request_id import RequestIDMiddleware
from {context}_{service}.middlewares.logging import LoggingMiddleware


def create_app() -> FastAPI:
    """Фабрика приложения."""
    setup_logging()

    app = FastAPI(
        title="{Service Name}",
        version="1.0.0",
    )

    # Middleware (порядок важен!)
    # Request ID должен быть первым
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)

    # ... роутеры ...

    return app
```

### 5. Использование в коде

```python
"""Пример использования логирования."""

import structlog

logger = structlog.get_logger(__name__)


class {Entity}Service:
    """Сервис с логированием."""

    async def create_{entity}(self, data: dict) -> dict:
        """Создать {entity} с логированием."""
        logger.info(
            "{entity}_creation_started",
            name=data.get("name"),
        )

        try:
            result = await self._do_create(data)

            logger.info(
                "{entity}_created",
                {entity}_id=str(result["id"]),
                name=result["name"],
            )

            return result

        except ValueError as e:
            logger.warning(
                "{entity}_creation_validation_error",
                error=str(e),
                data=data,
            )
            raise

        except Exception as e:
            logger.exception(
                "{entity}_creation_failed",
                error=str(e),
            )
            raise

    async def get_{entity}(self, {entity}_id: str) -> dict | None:
        """Получить {entity}."""
        logger.debug(
            "{entity}_fetch_started",
            {entity}_id={entity}_id,
        )

        result = await self._do_get({entity}_id)

        if result is None:
            logger.warning(
                "{entity}_not_found",
                {entity}_id={entity}_id,
            )
        else:
            logger.debug(
                "{entity}_fetched",
                {entity}_id={entity}_id,
            )

        return result
```

---

## Формат логов

### Development (консоль)

```
2024-01-15T10:30:45.123456+00:00 [info     ] request_started            method=GET path=/api/v1/entities request_id=abc-123
2024-01-15T10:30:45.125000+00:00 [info     ] entity_fetched             entity_id=xyz-789 request_id=abc-123
2024-01-15T10:30:45.130000+00:00 [info     ] request_completed          duration_ms=6.54 method=GET path=/api/v1/entities request_id=abc-123 status_code=200
```

### Production (JSON)

```json
{"timestamp": "2024-01-15T10:30:45.123456+00:00", "level": "info", "event": "request_started", "method": "GET", "path": "/api/v1/entities", "request_id": "abc-123"}
{"timestamp": "2024-01-15T10:30:45.125000+00:00", "level": "info", "event": "entity_fetched", "entity_id": "xyz-789", "request_id": "abc-123"}
{"timestamp": "2024-01-15T10:30:45.130000+00:00", "level": "info", "event": "request_completed", "duration_ms": 6.54, "method": "GET", "path": "/api/v1/entities", "request_id": "abc-123", "status_code": 200}
```

---

## Уровни логирования

| Уровень | Когда использовать |
|---------|-------------------|
| DEBUG | Детальная отладочная информация |
| INFO | Нормальное выполнение операций |
| WARNING | Потенциальные проблемы (не критичные) |
| ERROR | Ошибки, требующие внимания |
| CRITICAL | Критические ошибки (сервис не работает) |

---

## Что логировать

### ОБЯЗАТЕЛЬНО логировать

```python
# Входящие запросы
logger.info("request_started", method="GET", path="/api/v1/users")

# Исходящие вызовы
logger.info("external_call_started", service="data_api", endpoint="/users")

# Важные бизнес-события
logger.info("order_created", order_id="123", user_id="456")

# Ошибки
logger.error("payment_failed", order_id="123", error="Insufficient funds")

# Метрики производительности
logger.info("database_query", query="SELECT", duration_ms=5.2)
```

### НЕ логировать

```python
# Секретные данные
logger.info("user_login", password="secret")  # ПЛОХО!

# PII без необходимости
logger.info("user_data", email="user@example.com", phone="+1234567890")  # ПЛОХО!

# Большие объёмы данных
logger.info("response", body=large_json_object)  # ПЛОХО!
```

---

## Качественные ворота

### LOGGING_READY

- [ ] structlog настроен
- [ ] Request ID middleware подключён
- [ ] Logging middleware подключён
- [ ] JSON формат в production
- [ ] Все сервисы логируют запросы
- [ ] Ошибки логируются с traceback
- [ ] Нет логирования секретных данных

---

## Источники

| Документ | Описание |
|----------|----------|
| `knowledge/quality/logging/structured.md` | Структурированное логирование |
| `knowledge/quality/logging/correlation.md` | Корреляция логов |
