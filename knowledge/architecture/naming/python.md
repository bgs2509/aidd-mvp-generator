# Именование в Python

> **Назначение**: Правила именования в Python коде.

---

## Сводная таблица

| Элемент | Стиль | Пример |
|---------|-------|--------|
| Пакет | snake_case | `booking_api` |
| Модуль | snake_case | `user_service.py` |
| Класс | PascalCase | `UserService` |
| Функция | snake_case | `create_user` |
| Метод | snake_case | `get_by_id` |
| Переменная | snake_case | `user_id` |
| Константа | UPPER_SNAKE | `MAX_RETRIES` |
| Приватный | _prefix | `_internal_method` |
| Protected | _prefix | `_calculate_total` |
| Type Variable | PascalCase | `T`, `ModelType` |

---

## Классы

### Сервисы

```python
# Паттерн: {Entity}Service
class UserService:
    """Сервис пользователей."""
    pass

class OrderService:
    """Сервис заказов."""
    pass

class RestaurantService:
    """Сервис ресторанов."""
    pass
```

### Репозитории

```python
# Паттерн: {Entity}Repository
class UserRepository:
    """Репозиторий пользователей."""
    pass

class OrderRepository:
    """Репозиторий заказов."""
    pass
```

### HTTP клиенты

```python
# Паттерн: {Service}Client или {Service}ApiClient
class DataApiClient:
    """Клиент для Data API."""
    pass

class BusinessApiClient:
    """Клиент для Business API."""
    pass
```

### Исключения

```python
# Паттерн: {Name}Error
class NotFoundError(Exception):
    """Ресурс не найден."""
    pass

class ValidationError(Exception):
    """Ошибка валидации."""
    pass

class DataApiError(Exception):
    """Ошибка Data API."""
    pass
```

### Pydantic схемы

```python
# Паттерн: {Entity}{Action}
class UserCreate(BaseModel):
    """Схема создания пользователя."""
    pass

class UserUpdate(BaseModel):
    """Схема обновления пользователя."""
    pass

class UserResponse(BaseModel):
    """Схема ответа с пользователем."""
    pass

class UserListResponse(BaseModel):
    """Схема списка пользователей."""
    pass
```

### DTO (Data Transfer Objects)

```python
# Паттерн: {Action}{Entity}DTO
class CreateUserDTO(BaseModel):
    """DTO для создания пользователя."""
    pass

class UpdateUserDTO(BaseModel):
    """DTO для обновления пользователя."""
    pass

class UserDTO(BaseModel):
    """DTO пользователя."""
    pass
```

---

## Функции и методы

### CRUD операции

```python
# Паттерн: {action}_{entity}
async def create_user(data: UserCreate) -> User:
    """Создать пользователя."""
    pass

async def get_user(user_id: UUID) -> User:
    """Получить пользователя."""
    pass

async def update_user(user_id: UUID, data: UserUpdate) -> User:
    """Обновить пользователя."""
    pass

async def delete_user(user_id: UUID) -> None:
    """Удалить пользователя."""
    pass

async def list_users(page: int = 1) -> list[User]:
    """Получить список пользователей."""
    pass
```

### Репозиторий методы

```python
class UserRepository:
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Получить по ID."""
        pass

    async def get_by_email(self, email: str) -> User | None:
        """Получить по email."""
        pass

    async def get_all(self, offset: int = 0, limit: int = 100) -> list[User]:
        """Получить все записи."""
        pass

    async def create(self, **kwargs) -> User:
        """Создать запись."""
        pass

    async def update(self, user_id: UUID, **kwargs) -> User | None:
        """Обновить запись."""
        pass

    async def delete(self, user_id: UUID) -> bool:
        """Удалить запись."""
        pass

    async def count(self) -> int:
        """Подсчитать записи."""
        pass

    async def exists(self, user_id: UUID) -> bool:
        """Проверить существование."""
        pass
```

### Валидация

```python
# Паттерн: validate_{what} или is_{condition}
def validate_email(email: str) -> bool:
    """Валидировать email."""
    pass

def is_valid_phone(phone: str) -> bool:
    """Проверить телефон."""
    pass

async def check_user_exists(user_id: UUID) -> bool:
    """Проверить существование пользователя."""
    pass
```

### Приватные методы

```python
class OrderService:
    async def create_order(self, data: CreateOrderDTO) -> Order:
        """Публичный метод."""
        await self._validate_items(data.items)
        total = self._calculate_total(data.items)
        return await self._save_order(data, total)

    async def _validate_items(self, items: list) -> None:
        """Приватная валидация."""
        pass

    def _calculate_total(self, items: list) -> Decimal:
        """Приватный расчёт."""
        pass

    async def _save_order(self, data, total) -> Order:
        """Приватное сохранение."""
        pass
```

---

## Переменные

### Общие правила

```python
# snake_case для переменных
user_id = UUID("...")
order_items = []
total_amount = Decimal("0")
is_active = True
has_permission = False

# UPPER_SNAKE для констант
MAX_RETRIES = 3
DEFAULT_PAGE_SIZE = 20
API_VERSION = "v1"
HTTP_TIMEOUT = 30.0
```

### Типизация

```python
from typing import TypeVar
from uuid import UUID

# Type variables — PascalCase
T = TypeVar("T")
ModelType = TypeVar("ModelType", bound=Base)
EntityType = TypeVar("EntityType")

# Типизированные переменные
user_ids: list[UUID] = []
settings: dict[str, str] = {}
optional_name: str | None = None
```

---

## Файлы и модули

### Структура пакета

```
{context}_api/
├── __init__.py
├── main.py
├── api/
│   ├── __init__.py
│   ├── dependencies.py
│   └── v1/
│       ├── __init__.py
│       ├── router.py
│       └── user_routes.py     # snake_case
├── application/
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py    # snake_case
│   └── dtos/
│       ├── __init__.py
│       └── user_dtos.py       # snake_case
├── domain/
│   ├── __init__.py
│   └── entities/
│       ├── __init__.py
│       └── user.py            # snake_case (единственное число)
├── infrastructure/
│   ├── __init__.py
│   └── http/
│       ├── __init__.py
│       ├── base_client.py
│       └── data_api_client.py
├── schemas/
│   ├── __init__.py
│   ├── base.py
│   └── user_schemas.py
└── core/
    ├── __init__.py
    ├── config.py
    ├── logging.py
    └── exceptions.py
```

---

## Примеры

### Полный пример сервиса

```python
"""Сервис пользователей."""

from uuid import UUID

from booking_api.application.dtos.user_dtos import (
    CreateUserDTO,
    UpdateUserDTO,
    UserDTO,
)
from booking_api.core.exceptions import NotFoundError
from booking_api.infrastructure.http.data_api_client import DataApiClient


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(self, data_client: DataApiClient):
        """Инициализация сервиса."""
        self.data_client = data_client

    async def create_user(self, dto: CreateUserDTO) -> UserDTO:
        """Создать нового пользователя."""
        await self._validate_email_unique(dto.email)
        result = await self.data_client.create_user(dto.model_dump())
        return UserDTO.model_validate(result)

    async def get_user(self, user_id: UUID) -> UserDTO:
        """Получить пользователя по ID."""
        result = await self.data_client.get_user(user_id)
        if result is None:
            raise NotFoundError(f"User {user_id} not found")
        return UserDTO.model_validate(result)

    async def _validate_email_unique(self, email: str) -> None:
        """Проверить уникальность email."""
        existing = await self.data_client.get_user_by_email(email)
        if existing:
            raise ValueError(f"Email {email} already exists")
```
