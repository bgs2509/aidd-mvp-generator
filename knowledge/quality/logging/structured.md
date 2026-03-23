# Structured Logging

> **Purpose**: Setting up structlog for JSON logs.

---

## Installation

```bash
pip install structlog
```

---

## Basic Setup

```python
"""structlog setup."""

import logging
import structlog
from structlog.types import Processor


def setup_logging(
    log_level: str = "INFO",
    json_logs: bool = True,
) -> None:
    """
    Set up structured logging.

    Args:
        log_level: Log level.
        json_logs: Use JSON format.
    """
    # Shared processors
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


# Getting a logger
logger = structlog.get_logger()
```

---

## Usage

```python
"""structlog usage examples."""

import structlog

logger = structlog.get_logger()


# Simple message
logger.info("User created")

# With context
logger.info("User created", user_id="123", email="test@example.com")

# Different levels
logger.debug("Debug message", data={"key": "value"})
logger.info("Info message")
logger.warning("Warning message", reason="something")
logger.error("Error message", error_code=500)

# Exceptions
try:
    raise ValueError("Something went wrong")
except Exception:
    logger.exception("Failed to process", user_id="123")
```

---

## Context Variables

```python
"""Context variables for logging."""

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

logger = structlog.get_logger()


async def process_request(request_id: str, user_id: str):
    """Request processing with context."""
    # Bind context
    bind_contextvars(
        request_id=request_id,
        user_id=user_id,
    )

    try:
        # All logs will contain request_id and user_id
        logger.info("Processing started")

        await do_something()

        logger.info("Processing completed")
    finally:
        # Clear context
        clear_contextvars()


async def do_something():
    """Nested function."""
    # Context is preserved
    logger.info("Doing something")  # Will contain request_id and user_id
```

---

## FastAPI Middleware

```python
"""Request logging middleware."""

import time
import uuid
from fastapi import FastAPI, Request
from structlog.contextvars import bind_contextvars, clear_contextvars
import structlog

logger = structlog.get_logger()


def setup_logging_middleware(app: FastAPI) -> None:
    """Set up logging middleware."""

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        """HTTP request logging middleware."""
        # Generate request_id
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        # Bind context
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

## Integration with uvicorn

```python
"""Integration with uvicorn."""

import logging
import structlog


def setup_uvicorn_logging():
    """Set up uvicorn logging."""
    # Disable standard uvicorn logs
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.error").handlers = []

    # Redirect to structlog
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

## Log Format

```json
// Production JSON format
{
  "timestamp": "2024-01-15T12:00:00.000000Z",
  "level": "info",
  "event": "User created",
  "request_id": "abc-123",
  "user_id": "456",
  "email": "test@example.com"
}

// On error
{
  "timestamp": "2024-01-15T12:00:00.000000Z",
  "level": "error",
  "event": "Failed to process",
  "request_id": "abc-123",
  "exception": "Traceback (most recent call last):\n..."
}
```

---

## Configuration

```python
"""Logging configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    log_level: str = "INFO"
    json_logs: bool = True  # False for dev

    class Config:
        env_file = ".env"


settings = Settings()

# In main.py
setup_logging(
    log_level=settings.log_level,
    json_logs=settings.json_logs,
)
```

---

## Checklist

- [ ] structlog installed
- [ ] JSON format for production
- [ ] Console for development
- [ ] Context variables used
- [ ] request_id added
- [ ] Middleware configured
