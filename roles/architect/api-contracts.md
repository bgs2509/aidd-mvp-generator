# Функция: Определение контрактов API

> **Назначение**: Проектирование API контрактов между сервисами.

---

## Цель

Определить чёткие контракты API для всех сервисов,
обеспечивающие корректное взаимодействие компонентов.

---

## Принципы проектирования API

### 1. RESTful

```
GET    /api/v1/{resource}      — список ресурсов
GET    /api/v1/{resource}/{id} — получить один
POST   /api/v1/{resource}      — создать
PUT    /api/v1/{resource}/{id} — обновить полностью
PATCH  /api/v1/{resource}/{id} — обновить частично
DELETE /api/v1/{resource}/{id} — удалить
```

### 2. Версионирование

```
/api/v1/...  — первая версия
/api/v2/...  — вторая версия (при необходимости)

ПРАВИЛО: Всегда использовать версионирование с v1.
```

### 3. Именование путей

```
ПРАВИЛО: Пути в kebab-case, множественное число для коллекций.

✓ /api/v1/restaurants
✓ /api/v1/user-profiles
✓ /api/v1/order-items

✗ /api/v1/restaurant
✗ /api/v1/userProfiles
✗ /api/v1/order_items
```

### 4. Формат ответов

```json
// Успешный ответ (один объект)
{
  "id": "uuid",
  "field1": "value1",
  "field2": "value2",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}

// Успешный ответ (список с пагинацией)
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}

// Ошибка
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Описание ошибки",
    "details": [...]
  }
}
```

---

## Шаблон контракта API

### Business API контракт

```markdown
## Business API: {context}_api

**Base URL**: http://localhost:8000
**Prefix**: /api/v1

### Эндпоинты

| Метод | Путь | Описание | Req ID |
|-------|------|----------|--------|
| POST | /restaurants | Создать ресторан | FR-001 |
| GET | /restaurants | Список ресторанов | FR-002 |
| GET | /restaurants/{id} | Получить ресторан | FR-003 |
| POST | /bookings | Создать бронирование | FR-004 |
| GET | /bookings/{id} | Получить бронирование | FR-005 |

---

### POST /restaurants

**Описание**: Создание нового ресторана

**Request Body**:
```json
{
  "name": "string (required)",
  "address": "string (required)",
  "phone": "string (optional)",
  "capacity": "integer (required)"
}
```

**Response 201**:
```json
{
  "id": "uuid",
  "name": "string",
  "address": "string",
  "phone": "string | null",
  "capacity": "integer",
  "created_at": "datetime"
}
```

**Response 400**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {"field": "name", "message": "Field is required"}
    ]
  }
}
```

---

### GET /restaurants

**Описание**: Получение списка ресторанов

**Query Parameters**:
| Параметр | Тип | Описание | По умолчанию |
|----------|-----|----------|--------------|
| page | integer | Номер страницы | 1 |
| page_size | integer | Размер страницы | 20 |
| search | string | Поиск по имени | — |

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "string",
      "address": "string",
      "capacity": "integer"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```
```

### Data API контракт

```markdown
## Data API: {context}_data

**Base URL**: http://localhost:8001
**Prefix**: /api/v1

### Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /restaurants | Создать запись |
| GET | /restaurants | Получить записи |
| GET | /restaurants/{id} | Получить по ID |
| PUT | /restaurants/{id} | Обновить запись |
| DELETE | /restaurants/{id} | Удалить запись |

---

### Особенности Data API

1. **Прямой CRUD** — без бизнес-логики
2. **Валидация схем** — на уровне Pydantic
3. **Используется только Business API** — не клиентами напрямую

---

### POST /restaurants

**Описание**: Создание записи в БД

**Request Body**:
```json
{
  "name": "string",
  "address": "string",
  "phone": "string | null",
  "capacity": "integer"
}
```

**Response 201**:
```json
{
  "id": "uuid",
  "name": "string",
  "address": "string",
  "phone": "string | null",
  "capacity": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
```

---

## Схемы (Pydantic)

### Base схемы

```python
"""Базовые схемы для API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Базовая схема с общими настройками."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TimestampMixin(BaseModel):
    """Миксин для временных меток."""

    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseModel):
    """Схема пагинированного ответа."""

    total: int
    page: int
    page_size: int
    pages: int
```

### Пример схем ресурса

```python
"""Схемы для ресторанов."""

from uuid import UUID

from .base import BaseSchema, TimestampMixin


class RestaurantCreate(BaseSchema):
    """Схема создания ресторана."""

    name: str
    address: str
    phone: str | None = None
    capacity: int


class RestaurantUpdate(BaseSchema):
    """Схема обновления ресторана."""

    name: str | None = None
    address: str | None = None
    phone: str | None = None
    capacity: int | None = None


class RestaurantResponse(BaseSchema, TimestampMixin):
    """Схема ответа с рестораном."""

    id: UUID
    name: str
    address: str
    phone: str | None
    capacity: int


class RestaurantListResponse(BaseSchema):
    """Схема списка ресторанов."""

    items: list[RestaurantResponse]
    total: int
    page: int
    page_size: int
    pages: int
```

---

## HTTP коды ответов

| Код | Описание | Когда использовать |
|-----|----------|--------------------|
| 200 | OK | Успешный GET, PUT, PATCH |
| 201 | Created | Успешный POST (создание) |
| 204 | No Content | Успешный DELETE |
| 400 | Bad Request | Ошибка валидации |
| 401 | Unauthorized | Не авторизован |
| 403 | Forbidden | Нет доступа |
| 404 | Not Found | Ресурс не найден |
| 409 | Conflict | Конфликт (дубликат) |
| 422 | Unprocessable Entity | Ошибка бизнес-логики |
| 500 | Internal Server Error | Внутренняя ошибка |

---

## Коды ошибок

```python
"""Коды ошибок API."""

class ErrorCodes:
    """Стандартные коды ошибок."""

    # Валидация
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FORMAT = "INVALID_FORMAT"

    # Ресурсы
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"

    # Авторизация
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    # Бизнес-логика
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"

    # Внешние сервисы
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    DATA_API_ERROR = "DATA_API_ERROR"
```

---

## Взаимодействие сервисов

### Business API → Data API

```
Business API                          Data API
    │                                     │
    │  POST /api/v1/restaurants           │
    │ ──────────────────────────────────▶ │
    │                                     │
    │  201 Created                        │
    │ ◀────────────────────────────────── │
    │                                     │
```

### Telegram Bot → Business API

```
Telegram Bot                       Business API
    │                                    │
    │  GET /api/v1/restaurants?search=   │
    │ ─────────────────────────────────▶ │
    │                                    │
    │  200 OK (list)                     │
    │ ◀───────────────────────────────── │
    │                                    │
```

---

## Результат

```markdown
## API контракты проекта

### Сервисы

| Сервис | Base URL | Документация |
|--------|----------|--------------|
| Business API | http://localhost:8000 | /docs |
| Data API | http://localhost:8001 | /docs |

### Файлы контрактов

- ai-docs/docs/api/business-api-contract.md
- ai-docs/docs/api/data-api-contract.md

### Схемы

- services/{context}_api/src/schemas/
- services/{context}_data/src/schemas/
```

---

## Источники

| Документ | Описание |
|----------|----------|
| `knowledge/services/fastapi/routing-patterns.md` | Паттерны роутинга |
| `knowledge/services/fastapi/schema-validation.md` | Валидация схем |
| `conventions.md` | Соглашения об именовании |
