# Production Requirements для MVP

> **Назначение**: Чек-лист требований для production-ready MVP.
> Объединяет все критерии готовности к деплою в один документ.

---

## Обзор

Production-ready MVP должен соответствовать **Level 2** качества:
- Стабильная работа под нагрузкой
- Корректная обработка ошибок
- Возможность мониторинга и отладки
- Безопасность на базовом уровне

---

## 1. Health Checks

### Требования

- [ ] Endpoint `/health` возвращает HTTP 200
- [ ] Проверка подключения к БД
- [ ] Проверка подключения к Redis (если используется)
- [ ] Проверка внешних зависимостей

### Пример реализации

```python
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> JSONResponse:
    """Проверка здоровья сервиса."""
    checks = {
        "status": "healthy",
        "checks": {}
    }

    # Проверка БД
    try:
        await db.execute(text("SELECT 1"))
        checks["checks"]["database"] = "ok"
    except Exception as e:
        checks["checks"]["database"] = f"error: {str(e)}"
        checks["status"] = "unhealthy"

    # Проверка Redis
    try:
        await redis.ping()
        checks["checks"]["redis"] = "ok"
    except Exception as e:
        checks["checks"]["redis"] = f"error: {str(e)}"
        checks["status"] = "unhealthy"

    status_code = (
        status.HTTP_200_OK
        if checks["status"] == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(content=checks, status_code=status_code)
```

### Kubernetes Probes

```yaml
# В Deployment
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

---

## 2. Graceful Shutdown

### Требования

- [ ] Обработка сигналов SIGTERM и SIGINT
- [ ] Завершение текущих HTTP-запросов
- [ ] Закрытие соединений с БД
- [ ] Закрытие соединений с Redis
- [ ] Таймаут на завершение (default: 30s)

### Пример для FastAPI

```python
import signal
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    await init_database()
    await init_redis()

    yield

    # Shutdown
    await close_database()
    await close_redis()


app = FastAPI(lifespan=lifespan)
```

### Пример для AsyncIO Worker

```python
import signal
import asyncio


class GracefulShutdown:
    """Обработчик graceful shutdown."""

    def __init__(self):
        self.shutdown_event = asyncio.Event()

    def setup(self):
        """Настройка обработчиков сигналов."""
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(self._shutdown(sig))
            )

    async def _shutdown(self, sig: signal.Signals):
        """Обработка сигнала завершения."""
        print(f"Получен сигнал {sig.name}, завершаем...")
        self.shutdown_event.set()

    async def wait(self):
        """Ожидание сигнала завершения."""
        await self.shutdown_event.wait()
```

### Docker Stop Timeout

```yaml
# docker-compose.yml
services:
  api:
    stop_grace_period: 30s
```

---

## 3. Structured Logging

### Требования

- [ ] JSON формат логов
- [ ] Request ID для трейсинга
- [ ] Уровни логирования: DEBUG, INFO, WARNING, ERROR
- [ ] Контекстная информация (user_id, endpoint, etc.)
- [ ] Не логировать sensitive данные (пароли, токены)

### Пример с structlog

```python
import structlog
from uuid import uuid4


def setup_logging(json_logs: bool = True):
    """Настройка структурированного логирования."""
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Middleware для request_id
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Добавление request_id к каждому запросу."""
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    structlog.contextvars.bind_contextvars(request_id=request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response
```

### Что НЕ логировать

```python
SENSITIVE_FIELDS = {
    "password",
    "token",
    "secret",
    "api_key",
    "authorization",
    "credit_card",
}


def sanitize_log_data(data: dict) -> dict:
    """Удаление sensitive данных из логов."""
    return {
        k: "***REDACTED***" if k.lower() in SENSITIVE_FIELDS else v
        for k, v in data.items()
    }
```

---

## 4. Error Handling

### Требования

- [ ] Централизованная обработка исключений
- [ ] Разные ответы для dev и prod (stack trace только в dev)
- [ ] Логирование всех необработанных исключений
- [ ] Стандартизированный формат ошибок

### Пример Exception Handler

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Стандартный формат ошибки."""

    error: str
    message: str
    request_id: str | None = None
    details: dict | None = None


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Глобальный обработчик исключений."""
    logger = structlog.get_logger()

    # Логируем ошибку
    logger.error(
        "Unhandled exception",
        exc_type=type(exc).__name__,
        exc_message=str(exc),
        path=request.url.path,
    )

    # Формируем ответ
    error_response = ErrorResponse(
        error="internal_server_error",
        message="Внутренняя ошибка сервера",
        request_id=request.headers.get("X-Request-ID"),
    )

    # В dev-режиме добавляем детали
    if settings.DEBUG:
        error_response.details = {
            "exception": type(exc).__name__,
            "message": str(exc),
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )
```

### Кастомные исключения

```python
class AppException(Exception):
    """Базовое исключение приложения."""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 400,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    """Ресурс не найден."""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} с ID {resource_id} не найден",
            error_code="not_found",
            status_code=404,
        )
```

---

## 5. Configuration Management

### Требования

- [ ] Все секреты через environment variables
- [ ] Валидация конфига при старте приложения
- [ ] Значения по умолчанию для опциональных параметров
- [ ] Разделение конфигов: dev / staging / prod
- [ ] Никаких секретов в коде или git

### Пример с Pydantic Settings

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Обязательные
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str = Field(..., min_length=32)

    # Опциональные с defaults
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_PREFIX: str = "/api/v1"

    # Валидация
    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL должен быть PostgreSQL")
        return v


# Singleton
settings = Settings()
```

### .env.example

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-at-least-32-characters

# Optional
DEBUG=false
LOG_LEVEL=INFO
```

---

## 6. Security

### Требования

- [ ] HTTPS only в production
- [ ] CORS настроен (не `*` в production)
- [ ] Rate limiting для публичных endpoints
- [ ] Input validation через Pydantic
- [ ] SQL injection защита (параметризованные запросы)
- [ ] XSS защита (экранирование вывода)

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

# Production
ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]

# Development
if settings.DEBUG:
    ALLOWED_ORIGINS.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.get("/api/public")
@limiter.limit("10/minute")
async def public_endpoint(request: Request):
    """Публичный endpoint с rate limiting."""
    return {"message": "ok"}
```

### Input Validation

```python
from pydantic import BaseModel, Field, validator
import re


class UserCreate(BaseModel):
    """Схема создания пользователя."""

    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)

    @validator("email")
    def validate_email(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, v):
            raise ValueError("Некорректный email")
        return v.lower()

    @validator("password")
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль должен содержать заглавную букву")
        if not re.search(r"[0-9]", v):
            raise ValueError("Пароль должен содержать цифру")
        return v
```

---

## 7. Monitoring & Metrics

### Требования

- [ ] Метрики запросов (count, latency, errors)
- [ ] Метрики бизнес-логики (orders, users, etc.)
- [ ] Алерты на критические ошибки
- [ ] Dashboard для визуализации

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

# Метрики
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Сбор метрик для каждого запроса."""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
    ).inc()
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path,
    ).observe(duration)

    return response


@app.get("/metrics")
async def metrics():
    """Endpoint для Prometheus."""
    return Response(
        content=generate_latest(),
        media_type="text/plain",
    )
```

---

## 8. Чек-лист перед деплоем

### Инфраструктура

- [ ] Docker images собираются без ошибок
- [ ] docker-compose up запускает все сервисы
- [ ] Health checks проходят для всех сервисов
- [ ] Volumes для персистентных данных настроены

### Код

- [ ] Все тесты проходят (`pytest`)
- [ ] Coverage ≥75%
- [ ] Линтер проходит (`ruff check`)
- [ ] Type checker проходит (`mypy`)
- [ ] Нет TODO/FIXME в критичном коде

### Безопасность

- [ ] Секреты не в коде и не в git
- [ ] .env.example актуален
- [ ] CORS настроен для production
- [ ] Rate limiting включён

### Логирование

- [ ] JSON формат логов
- [ ] Уровень логирования INFO или выше
- [ ] Sensitive данные не логируются

### Мониторинг

- [ ] /health endpoint работает
- [ ] /metrics endpoint работает (если нужен)
- [ ] Алерты настроены

---

## Связанные документы

| Документ | Описание |
|----------|----------|
| `knowledge/quality/logging/structured.md` | Настройка structlog |
| `knowledge/services/asyncio-workers/signal-handling.md` | Graceful shutdown |
| `knowledge/services/fastapi/application-factory.md` | Паттерн Application Factory |
| `knowledge/infrastructure/docker-compose.md` | Docker Compose конфигурация |
| `knowledge/infrastructure/ci-cd.md` | CI/CD pipeline |

---

**Версия документа**: 1.0
**Создан**: 2025-12-20
