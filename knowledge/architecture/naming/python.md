# Python Naming

> **Purpose**: Naming rules for Python code.

---

## Summary Table

| Element | Style | Example |
|---------|-------|--------|
| Package | snake_case | `booking_api` |
| Module | snake_case | `user_service.py` |
| Class | PascalCase | `UserService` |
| Function | snake_case | `create_user` |
| Method | snake_case | `get_by_id` |
| Variable | snake_case | `user_id` |
| Constant | UPPER_SNAKE | `MAX_RETRIES` |
| Private | _prefix | `_internal_method` |
| Protected | _prefix | `_calculate_total` |
| Type Variable | PascalCase | `T`, `ModelType` |

---

## Classes

### Services

```python
# Pattern: {Entity}Service
class UserService:
    """User service."""
    pass

class OrderService:
    """Order service."""
    pass

class RestaurantService:
    """Restaurant service."""
    pass
```

### Repositories

```python
# Pattern: {Entity}Repository
class UserRepository:
    """User repository."""
    pass

class OrderRepository:
    """Order repository."""
    pass
```

### HTTP Clients

```python
# Pattern: {Service}Client or {Service}ApiClient
class DataApiClient:
    """Client for Data API."""
    pass

class BusinessApiClient:
    """Client for Business API."""
    pass
```

### Exceptions

```python
# Pattern: {Name}Error
class NotFoundError(Exception):
    """Resource not found."""
    pass

class ValidationError(Exception):
    """Validation error."""
    pass

class DataApiError(Exception):
    """Data API error."""
    pass
```

### Pydantic Schemas

```python
# Pattern: {Entity}{Action}
class UserCreate(BaseModel):
    """User creation schema."""
    pass

class UserUpdate(BaseModel):
    """User update schema."""
    pass

class UserResponse(BaseModel):
    """User response schema."""
    pass

class UserListResponse(BaseModel):
    """User list schema."""
    pass
```

### DTO (Data Transfer Objects)

```python
# Pattern: {Action}{Entity}DTO
class CreateUserDTO(BaseModel):
    """DTO for user creation."""
    pass

class UpdateUserDTO(BaseModel):
    """DTO for user update."""
    pass

class UserDTO(BaseModel):
    """User DTO."""
    pass
```

---

## Functions and Methods

### CRUD Operations

```python
# Pattern: {action}_{entity}
async def create_user(data: UserCreate) -> User:
    """Create a user."""
    pass

async def get_user(user_id: UUID) -> User:
    """Get a user."""
    pass

async def update_user(user_id: UUID, data: UserUpdate) -> User:
    """Update a user."""
    pass

async def delete_user(user_id: UUID) -> None:
    """Delete a user."""
    pass

async def list_users(page: int = 1) -> list[User]:
    """Get a list of users."""
    pass
```

### Repository Methods

```python
class UserRepository:
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get by ID."""
        pass

    async def get_by_email(self, email: str) -> User | None:
        """Get by email."""
        pass

    async def get_all(self, offset: int = 0, limit: int = 100) -> list[User]:
        """Get all records."""
        pass

    async def create(self, **kwargs) -> User:
        """Create a record."""
        pass

    async def update(self, user_id: UUID, **kwargs) -> User | None:
        """Update a record."""
        pass

    async def delete(self, user_id: UUID) -> bool:
        """Delete a record."""
        pass

    async def count(self) -> int:
        """Count records."""
        pass

    async def exists(self, user_id: UUID) -> bool:
        """Check existence."""
        pass
```

### Validation

```python
# Pattern: validate_{what} or is_{condition}
def validate_email(email: str) -> bool:
    """Validate email."""
    pass

def is_valid_phone(phone: str) -> bool:
    """Check phone number."""
    pass

async def check_user_exists(user_id: UUID) -> bool:
    """Check user existence."""
    pass
```

### Private Methods

```python
class OrderService:
    async def create_order(self, data: CreateOrderDTO) -> Order:
        """Public method."""
        await self._validate_items(data.items)
        total = self._calculate_total(data.items)
        return await self._save_order(data, total)

    async def _validate_items(self, items: list) -> None:
        """Private validation."""
        pass

    def _calculate_total(self, items: list) -> Decimal:
        """Private calculation."""
        pass

    async def _save_order(self, data, total) -> Order:
        """Private save."""
        pass
```

---

## Variables

### General Rules

```python
# snake_case for variables
user_id = UUID("...")
order_items = []
total_amount = Decimal("0")
is_active = True
has_permission = False

# UPPER_SNAKE for constants
MAX_RETRIES = 3
DEFAULT_PAGE_SIZE = 20
API_VERSION = "v1"
HTTP_TIMEOUT = 30.0
```

### Typing

```python
from typing import TypeVar
from uuid import UUID

# Type variables — PascalCase
T = TypeVar("T")
ModelType = TypeVar("ModelType", bound=Base)
EntityType = TypeVar("EntityType")

# Typed variables
user_ids: list[UUID] = []
settings: dict[str, str] = {}
optional_name: str | None = None
```

---

## Files and Modules

### Package Structure

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
│       └── user.py            # snake_case (singular)
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

## Examples

### Full Service Example

```python
"""User service."""

from uuid import UUID

from booking_api.application.dtos.user_dtos import (
    CreateUserDTO,
    UpdateUserDTO,
    UserDTO,
)
from booking_api.core.exceptions import NotFoundError
from booking_api.infrastructure.http.data_api_client import DataApiClient


class UserService:
    """Service for working with users."""

    def __init__(self, data_client: DataApiClient):
        """Initialize service."""
        self.data_client = data_client

    async def create_user(self, dto: CreateUserDTO) -> UserDTO:
        """Create a new user."""
        await self._validate_email_unique(dto.email)
        result = await self.data_client.create_user(dto.model_dump())
        return UserDTO.model_validate(result)

    async def get_user(self, user_id: UUID) -> UserDTO:
        """Get a user by ID."""
        result = await self.data_client.get_user(user_id)
        if result is None:
            raise NotFoundError(f"User {user_id} not found")
        return UserDTO.model_validate(result)

    async def _validate_email_unique(self, email: str) -> None:
        """Check email uniqueness."""
        existing = await self.data_client.get_user_by_email(email)
        if existing:
            raise ValueError(f"Email {email} already exists")
```
