# conventions.md — Code Conventions

> **Purpose**: Unified code standards for all generated projects.
> AI agent MUST follow these conventions when generating code.
>
> **Documentation language**: Russian

---

## 1. Naming

### 1.1 Python Code

| Element | Style | Example |
|---------|-------|---------|
| Modules | `snake_case` | `user_service.py` |
| Classes | `PascalCase` | `UserService` |
| Functions | `snake_case` | `get_user_by_id()` |
| Variables | `snake_case` | `user_name` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| Private | `_prefix` | `_internal_method()` |
| Protected | `_prefix` | `_calculate_total()` |

### 1.2 Files and Directories

| Element | Style | Example |
|---------|-------|---------|
| Python files | `snake_case.py` | `user_repository.py` |
| Markdown | `kebab-case.md` | `api-contracts.md` |
| Configs | `kebab-case` | `docker-compose.yml` |
| Directories | `snake_case` | `data_services/` |

### 1.3 Service Naming

```
{context}_{domain}_{type}

Where:
- context: business area (finance, booking, ecommerce)
- domain: subsystem (lending, payments, orders)
- type: api, bot, worker, data
```

**Examples**:
```
booking_restaurant_api       # Business API
booking_restaurant_bot       # Telegram Bot
booking_restaurant_worker    # Background Worker
booking_restaurant_data      # Data API PostgreSQL
```

---

## 2. Docstrings (Google style, in Russian)

### 2.1 Functions

```python
def get_user_by_id(user_id: int, include_deleted: bool = False) -> User | None:
    """
    Получает пользователя по идентификатору.

    Выполняет поиск пользователя в базе данных по уникальному ID.
    Опционально может включать удалённых пользователей.

    Args:
        user_id: Уникальный идентификатор пользователя.
        include_deleted: Включать ли удалённых пользователей.
            По умолчанию False.

    Returns:
        Объект User если найден, None в противном случае.

    Raises:
        ValueError: Если user_id отрицательный.
        DatabaseError: При ошибке соединения с БД.

    Examples:
        >>> user = get_user_by_id(123)
        >>> user.name
        'Иван Петров'
    """
    pass
```

### 2.2 Classes

```python
class UserService:
    """
    Сервис для работы с пользователями.

    Предоставляет бизнес-логику управления пользователями:
    создание, обновление, деактивация и поиск.

    Attributes:
        data_client: HTTP клиент для обращения к Data API.
        cache: Redis клиент для кэширования.

    Examples:
        >>> service = UserService(data_client, cache)
        >>> user = await service.create_user(CreateUserDTO(...))
    """

    def __init__(self, data_client: DataClient, cache: RedisClient) -> None:
        """
        Инициализирует сервис пользователей.

        Args:
            data_client: HTTP клиент для Data API.
            cache: Redis клиент для кэширования.
        """
        self.data_client = data_client
        self.cache = cache
```

### 2.3 Modules

```python
"""
Модуль сервиса пользователей.

Содержит бизнес-логику для работы с пользователями:
- Создание и регистрация
- Аутентификация
- Управление профилем

Примечания:
    Модуль использует HTTP-only доступ к данным через Data API.
    Прямой доступ к базе данных запрещён.

Типичное использование:
    from application.services.user_service import UserService

    service = UserService(data_client)
    user = await service.get_user(user_id=123)
"""
```

---

## 3. Type Hints

### 3.1 Mandatory Usage

Type hints are **MANDATORY** for:
- All function parameters
- Function return values
- Class attributes
- Module-level variables

```python
# ✅ Correct
def process_order(order_id: int, items: list[OrderItem]) -> ProcessedOrder:
    pass

# ❌ Incorrect
def process_order(order_id, items):
    pass
```

### 3.2 Standard Patterns

```python
from typing import Optional, Any
from collections.abc import Sequence, Mapping

# Optional (can be None)
def get_user(user_id: int) -> User | None:
    pass

# Collections
def process_items(items: list[Item]) -> dict[str, Any]:
    pass

# Callable
def register_handler(callback: Callable[[Event], None]) -> None:
    pass

# Generic
T = TypeVar("T")
def first_or_default(items: Sequence[T], default: T) -> T:
    pass
```

### 3.3 Pydantic Models

```python
from pydantic import BaseModel, Field

class CreateUserRequest(BaseModel):
    """Запрос на создание пользователя."""

    name: str = Field(..., min_length=1, max_length=100, description="Имя пользователя")
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="Email")
    age: int | None = Field(default=None, ge=0, le=150, description="Возраст")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "Иван Петров", "email": "ivan@example.com", "age": 30}
            ]
        }
    }
```

---

## 4. Imports

### 4.1 Grouping

```python
# 1. Standard library
import asyncio
import logging
from datetime import datetime
from typing import Any

# 2. Third-party libraries
import httpx
from fastapi import FastAPI, Depends
from pydantic import BaseModel

# 3. Local modules (absolute imports)
from src.core.config import settings
from src.application.services import UserService
from src.domain.entities import User
```

### 4.2 Rules

- **Only absolute imports** (no relative imports)
- Groups separated by blank lines
- Within a group — alphabetical order
- `from x import y` is preferred over `import x`

```python
# ✅ Correct
from src.domain.entities import User

# ❌ Incorrect
from ..domain.entities import User
```

---

## 5. Service Structure (DDD/Hexagonal)

### 5.1 Layers

```
src/
├── api/                # Incoming adapters (HTTP)
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   └── users_router.py
│   └── dependencies.py
│
├── application/        # Use Cases / Application Services
│   ├── services/
│   │   └── user_service.py
│   └── dtos/
│       └── user_dto.py
│
├── domain/             # Pure business logic
│   ├── entities/
│   │   └── user.py
│   ├── value_objects/
│   │   └── email.py
│   └── services/
│       └── user_domain_service.py
│
├── infrastructure/     # Outgoing adapters
│   ├── http/
│   │   └── data_api_client.py
│   └── cache/
│       └── redis_client.py
│
├── schemas/            # Pydantic API schemas
│   ├── __init__.py
│   ├── base.py
│   └── user_schemas.py
│
├── core/               # Configuration and utilities
│   ├── config.py
│   ├── logging.py
│   └── exceptions.py
│
└── main.py             # Entry point
```

### 5.2 Dependencies Between Layers

```
api → application → domain
                 ↘
                   infrastructure
```

**Rules**:
- `domain` does NOT depend on anything
- `application` depends only on `domain`
- `api` and `infrastructure` depend on `application` and `domain`

---

## 6. Error Handling

### 6.1 Custom Exceptions

```python
# src/core/exceptions.py

class AppException(Exception):
    """Базовое исключение приложения."""

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(AppException):
    """Ресурс не найден."""

    def __init__(self, resource: str, identifier: Any) -> None:
        super().__init__(
            message=f"{resource} с идентификатором {identifier} не найден",
            code="NOT_FOUND"
        )


class ValidationError(AppException):
    """Ошибка валидации."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(
            message=f"Ошибка валидации поля '{field}': {message}",
            code="VALIDATION_ERROR"
        )
```

### 6.2 FastAPI Error Handlers

```python
# src/api/error_handlers.py

from fastapi import Request
from fastapi.responses import JSONResponse
from src.core.exceptions import AppException, NotFoundError

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Обработчик исключений приложения."""
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        }
    )
```

---

## 7. Logging

### 7.1 Structured Logging (structlog)

```python
import structlog

logger = structlog.get_logger(__name__)

async def process_order(order_id: int) -> Order:
    """Обрабатывает заказ."""
    logger.info(
        "Начало обработки заказа",
        order_id=order_id,
        action="process_order_start"
    )

    try:
        order = await fetch_order(order_id)
        logger.info(
            "Заказ успешно обработан",
            order_id=order_id,
            total=order.total,
            action="process_order_success"
        )
        return order
    except Exception as e:
        logger.error(
            "Ошибка обработки заказа",
            order_id=order_id,
            error=str(e),
            action="process_order_error"
        )
        raise
```

### 7.2 Logging Levels

| Level | Usage |
|-------|-------|
| `DEBUG` | Details for debugging |
| `INFO` | Normal execution flow |
| `WARNING` | Potential issues |
| `ERROR` | Errors requiring attention |
| `CRITICAL` | Critical failures |

---

## 8. Testing

### 8.1 Test Structure

```
tests/
├── unit/                   # Isolated tests
│   ├── domain/
│   │   └── test_user_entity.py
│   └── application/
│       └── test_user_service.py
│
├── integration/            # Integration tests
│   └── test_user_api.py
│
├── conftest.py             # Shared fixtures
└── factories.py            # Test data factories
```

### 8.2 Test Naming

```python
# Format: test_{what_we_test}_{scenario}_{expected_result}

def test_create_user_with_valid_data_returns_user():
    """Тест создания пользователя с валидными данными."""
    pass

def test_create_user_with_invalid_email_raises_validation_error():
    """Тест создания пользователя с невалидным email."""
    pass
```

### 8.3 Pytest Fixtures

```python
# tests/conftest.py

import pytest
from httpx import AsyncClient
from src.main import app

@pytest.fixture
async def client() -> AsyncClient:
    """Асинхронный HTTP клиент для тестов."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def sample_user() -> dict:
    """Пример данных пользователя."""
    return {
        "name": "Тестовый Пользователь",
        "email": "test@example.com",
        "age": 25
    }
```

### 8.4 Test Coverage

**Minimum coverage for MVP: ≥75%**

```bash
# Run with coverage
pytest --cov=src --cov-report=html --cov-fail-under=75
```

---

## 9. Configuration

### 9.1 Pydantic Settings

```python
# src/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Настройки приложения."""

    # Application
    app_name: str = "booking_restaurant_api"
    debug: bool = False
    log_level: str = "INFO"

    # Data API
    data_api_url: str = "http://localhost:8001"
    data_api_timeout: int = 30

    # Redis
    redis_url: str = "redis://localhost:6379"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

settings = Settings()
```

### 9.2 Environment Variables

```bash
# .env.example

# Application
APP_NAME=booking_restaurant_api
DEBUG=false
LOG_LEVEL=INFO

# Data API
DATA_API_URL=http://data-api:8001
DATA_API_TIMEOUT=30

# Redis
REDIS_URL=redis://redis:6379
```

### 9.3 Reverse Proxy (root_path)

When running behind nginx with a path prefix (multi-service deployment):

```python
# src/core/config.py

class Settings(BaseSettings):
    # ... other settings
    root_path: str = ""  # Path prefix (e.g., "/my-service")

# src/main.py

app = FastAPI(
    title=settings.app_name,
    root_path=settings.root_path,
)
```

```bash
# .env (production)
ROOT_PATH=/my-service
```

**Rules:**
- nginx does NOT rewrite — passes full path
- FastAPI uses root_path from env
- Routes are declared WITHOUT prefix (`@app.get("/health")`, not `/my-service/health`)
- StaticFiles mounts work automatically

**More details:** `knowledge/infrastructure/nginx.md` (section "Working with path prefixes")

---

## 10. Code Review Checklist

### Convention Compliance

- [ ] Naming follows standards
- [ ] Type hints for all functions
- [ ] Docstrings in Russian, Google style
- [ ] Absolute imports
- [ ] DDD/Hexagonal structure followed

### Code Quality

- [ ] No duplication (DRY)
- [ ] Simple solutions (KISS)
- [ ] No excessive functionality (YAGNI)
- [ ] Error handling via custom exceptions
- [ ] Structured logging

### Testing

- [ ] Unit tests for business logic
- [ ] Integration tests for API
- [ ] Coverage ≥75%

---

**Document version**: 1.0
**Created**: 2025-12-19
**Purpose**: Code Conventions for AIDD-MVP Generator
