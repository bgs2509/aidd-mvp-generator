# Структурированное логирование

> **Назначение**: Настройка structlog для JSON логов.

---

## Установка

```bash
pip install structlog
```

---

## Базовая настройка

```python
"""Настройка structlog."""

import logging
import structlog
from structlog.types import Processor


def setup_logging(
    log_level: str = "INFO",
    json_logs: bool = True,
) -> None:
    """
    Настроить структурированное логирование.

    Args:
        log_level: Уровень логирования.
        json_logs: Использовать JSON формат.
    """
    # Общие процессоры
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_logs:
        # Production: JSON
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: Console
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Получение логгера
logger = structlog.get_logger()
```

---

## Использование

```python
"""Примеры использования structlog."""

import structlog

logger = structlog.get_logger()


# Простое сообщение
logger.info("User created")

# С контекстом
logger.info("User created", user_id="123", email="test@example.com")

# Различные уровни
logger.debug("Debug message", data={"key": "value"})
logger.info("Info message")
logger.warning("Warning message", reason="something")
logger.error("Error message", error_code=500)

# Исключения
try:
    raise ValueError("Something went wrong")
except Exception:
    logger.exception("Failed to process", user_id="123")
```

---

## Контекстные переменные

```python
"""Контекстные переменные для логирования."""

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

logger = structlog.get_logger()


async def process_request(request_id: str, user_id: str):
    """Обработка запроса с контекстом."""
    # Привязка контекста
    bind_contextvars(
        request_id=request_id,
        user_id=user_id,
    )

    try:
        # Все логи будут содержать request_id и user_id
        logger.info("Processing started")

        await do_something()

        logger.info("Processing completed")
    finally:
        # Очистка контекста
        clear_contextvars()


async def do_something():
    """Вложенная функция."""
    # Контекст сохраняется
    logger.info("Doing something")  # Будет содержать request_id и user_id
```

---

## Middleware FastAPI

```python
"""Middleware для логирования запросов."""

import time
import uuid
from fastapi import FastAPI, Request
from structlog.contextvars import bind_contextvars, clear_contextvars
import structlog

logger = structlog.get_logger()


def setup_logging_middleware(app: FastAPI) -> None:
    """Настроить middleware логирования."""

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        """Middleware для логирования HTTP запросов."""
        # Генерация request_id
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        # Привязка контекста
        bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        start_time = time.perf_counter()

        try:
            logger.info("Request started")

            response = await call_next(request)

            process_time = time.perf_counter() - start_time
            logger.info(
                "Request completed",
                status_code=response.status_code,
                duration_ms=round(process_time * 1000, 2),
            )

            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            logger.exception("Request failed", error=str(e))
            raise

        finally:
            clear_contextvars()
```

---

## Интеграция с uvicorn

```python
"""Интеграция с uvicorn."""

import logging
import structlog


def setup_uvicorn_logging():
    """Настроить логирование uvicorn."""
    # Отключение стандартных логов uvicorn
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.error").handlers = []

    # Перенаправление в structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
```

---

## Формат логов

```json
// Production JSON формат
{
  "timestamp": "2024-01-15T12:00:00.000000Z",
  "level": "info",
  "event": "User created",
  "request_id": "abc-123",
  "user_id": "456",
  "email": "test@example.com"
}

// При ошибке
{
  "timestamp": "2024-01-15T12:00:00.000000Z",
  "level": "error",
  "event": "Failed to process",
  "request_id": "abc-123",
  "exception": "Traceback (most recent call last):\n..."
}
```

---

## Конфигурация

```python
"""Конфигурация логирования."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    log_level: str = "INFO"
    json_logs: bool = True  # False для dev

    class Config:
        env_file = ".env"


settings = Settings()

# В main.py
setup_logging(
    log_level=settings.log_level,
    json_logs=settings.json_logs,
)
```

---

## Чек-лист

- [ ] structlog установлен
- [ ] JSON формат для production
- [ ] Console для development
- [ ] Контекстные переменные используются
- [ ] request_id добавляется
- [ ] Middleware настроен
