# conventions.md — Соглашения о коде и стиле

> **Назначение**: Единые стандарты кода для всех генерируемых проектов.
> AI-агент ОБЯЗАН следовать этим соглашениям при генерации кода.
>
> **Язык документации**: Русский

---

## 1. Именование

### 1.1 Python код

| Элемент | Стиль | Пример |
|---------|-------|--------|
| Модули | `snake_case` | `user_service.py` |
| Классы | `PascalCase` | `UserService` |
| Функции | `snake_case` | `get_user_by_id()` |
| Переменные | `snake_case` | `user_name` |
| Константы | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| Приватные | `_prefix` | `_internal_method()` |
| Protected | `_prefix` | `_calculate_total()` |

### 1.2 Файлы и директории

| Элемент | Стиль | Пример |
|---------|-------|--------|
| Python файлы | `snake_case.py` | `user_repository.py` |
| Markdown | `kebab-case.md` | `api-contracts.md` |
| Конфиги | `kebab-case` | `docker-compose.yml` |
| Директории | `snake_case` | `data_services/` |

### 1.3 Именование сервисов

```
{контекст}_{домен}_{тип}

Где:
- контекст: бизнес-область (finance, booking, ecommerce)
- домен: подсистема (lending, payments, orders)
- тип: api, bot, worker, data
```

**Примеры**:
```
booking_restaurant_api       # Business API
booking_restaurant_bot       # Telegram Bot
booking_restaurant_worker    # Background Worker
booking_restaurant_data      # Data API PostgreSQL
```

---

## 2. Docstrings (Google-стиль, на русском)

### 2.1 Функции

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

### 2.2 Классы

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

### 2.3 Модули

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

### 3.1 Обязательность

Type hints **ОБЯЗАТЕЛЬНЫ** для:
- Всех параметров функций
- Возвращаемых значений функций
- Атрибутов классов
- Переменных модульного уровня

```python
# ✅ Правильно
def process_order(order_id: int, items: list[OrderItem]) -> ProcessedOrder:
    pass

# ❌ Неправильно
def process_order(order_id, items):
    pass
```

### 3.2 Стандартные паттерны

```python
from typing import Optional, Any
from collections.abc import Sequence, Mapping

# Optional (может быть None)
def get_user(user_id: int) -> User | None:
    pass

# Коллекции
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

### 3.3 Pydantic модели

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

## 4. Импорты

### 4.1 Группировка

```python
# 1. Стандартная библиотека
import asyncio
import logging
from datetime import datetime
from typing import Any

# 2. Сторонние библиотеки
import httpx
from fastapi import FastAPI, Depends
from pydantic import BaseModel

# 3. Локальные модули (absolute imports)
from src.core.config import settings
from src.application.services import UserService
from src.domain.entities import User
```

### 4.2 Правила

- **Только absolute imports** (никаких relative imports)
- Группы разделяются пустой строкой
- Внутри группы — алфавитный порядок
- `from x import y` предпочтительнее `import x`

```python
# ✅ Правильно
from src.domain.entities import User

# ❌ Неправильно
from ..domain.entities import User
```

---

## 5. Структура сервиса (DDD/Hexagonal)

### 5.1 Слои

```
src/
├── api/                # Входящие адаптеры (HTTP)
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
├── domain/             # Чистая бизнес-логика
│   ├── entities/
│   │   └── user.py
│   ├── value_objects/
│   │   └── email.py
│   └── services/
│       └── user_domain_service.py
│
├── infrastructure/     # Исходящие адаптеры
│   ├── http/
│   │   └── data_api_client.py
│   └── cache/
│       └── redis_client.py
│
├── schemas/            # Pydantic схемы API
│   ├── __init__.py
│   ├── base.py
│   └── user_schemas.py
│
├── core/               # Конфигурация и утилиты
│   ├── config.py
│   ├── logging.py
│   └── exceptions.py
│
└── main.py             # Точка входа
```

### 5.2 Зависимости между слоями

```
api → application → domain
                 ↘
                   infrastructure
```

**Правила**:
- `domain` НЕ зависит ни от чего
- `application` зависит только от `domain`
- `api` и `infrastructure` зависят от `application` и `domain`

---

## 6. Обработка ошибок

### 6.1 Кастомные исключения

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

### 6.2 Обработчики ошибок FastAPI

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

## 7. Логирование

### 7.1 Структурированное логирование (structlog)

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

### 7.2 Уровни логирования

| Уровень | Использование |
|---------|---------------|
| `DEBUG` | Детали для отладки |
| `INFO` | Нормальный ход выполнения |
| `WARNING` | Потенциальные проблемы |
| `ERROR` | Ошибки, требующие внимания |
| `CRITICAL` | Критические сбои |

---

## 8. Тестирование

### 8.1 Структура тестов

```
tests/
├── unit/                   # Изолированные тесты
│   ├── domain/
│   │   └── test_user_entity.py
│   └── application/
│       └── test_user_service.py
│
├── integration/            # Тесты интеграции
│   └── test_user_api.py
│
├── conftest.py             # Общие фикстуры
└── factories.py            # Фабрики тестовых данных
```

### 8.2 Именование тестов

```python
# Формат: test_{что_тестируем}_{сценарий}_{ожидаемый_результат}

def test_create_user_with_valid_data_returns_user():
    """Тест создания пользователя с валидными данными."""
    pass

def test_create_user_with_invalid_email_raises_validation_error():
    """Тест создания пользователя с невалидным email."""
    pass
```

### 8.3 Фикстуры pytest

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

### 8.4 Покрытие тестами

**Минимальное покрытие для MVP: ≥75%**

```bash
# Запуск с покрытием
pytest --cov=src --cov-report=html --cov-fail-under=75
```

---

## 9. Конфигурация

### 9.1 Pydantic Settings

```python
# src/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Настройки приложения."""

    # Приложение
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

### 9.2 Переменные окружения

```bash
# .env.example

# Приложение
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

При работе за nginx с путевым префиксом (multi-service deployment):

```python
# src/core/config.py

class Settings(BaseSettings):
    # ... другие настройки
    root_path: str = ""  # Путевой префикс (например, "/my-service")

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

**Правила:**
- nginx НЕ делает rewrite — передаёт полный путь
- FastAPI использует root_path из env
- Routes объявляются БЕЗ префикса (`@app.get("/health")`, не `/my-service/health`)
- StaticFiles mounts работают автоматически

**Подробнее:** `knowledge/infrastructure/nginx.md` (секция "Работа с путевыми префиксами")

---

## 10. Чек-лист для код-ревью

### Соответствие соглашениям

- [ ] Именование соответствует стандартам
- [ ] Type hints для всех функций
- [ ] Docstrings на русском в Google-стиле
- [ ] Absolute imports
- [ ] Структура DDD/Hexagonal соблюдена

### Качество кода

- [ ] Нет дублирования (DRY)
- [ ] Простые решения (KISS)
- [ ] Нет избыточного функционала (YAGNI)
- [ ] Обработка ошибок через кастомные исключения
- [ ] Структурированное логирование

### Тестирование

- [ ] Unit-тесты для бизнес-логики
- [ ] Integration-тесты для API
- [ ] Покрытие ≥75%

---

**Версия документа**: 1.0
**Создан**: 2025-12-19
**Назначение**: Соглашения о коде для AIDD-MVP Generator
