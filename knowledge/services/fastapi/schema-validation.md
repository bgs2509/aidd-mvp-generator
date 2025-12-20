# Валидация схем FastAPI

> **Назначение**: Pydantic схемы для валидации данных.

---

## Базовые схемы

```python
"""Базовые Pydantic схемы."""

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
    """Миксин с временными метками."""

    created_at: datetime
    updated_at: datetime | None = None


class IDMixin(BaseModel):
    """Миксин с идентификатором."""

    id: UUID
```

---

## CRUD схемы

```python
"""Схемы пользователя."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from {context}_api.schemas.base import BaseSchema, TimestampMixin


class UserBase(BaseModel):
    """Базовые поля пользователя."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    """Схема создания пользователя."""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Схема обновления пользователя."""

    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None


class UserResponse(UserBase, TimestampMixin, BaseSchema):
    """Схема ответа с пользователем."""

    id: UUID
    is_active: bool = True


class UserListResponse(BaseModel):
    """Схема списка пользователей."""

    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int
```

---

## Валидаторы

```python
"""Схемы с кастомными валидаторами."""

from pydantic import BaseModel, field_validator, model_validator
import re


class PhoneNumber(BaseModel):
    """Схема с валидацией телефона."""

    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """
        Валидировать номер телефона.

        Args:
            v: Номер телефона.

        Returns:
            Нормализованный номер.

        Raises:
            ValueError: Если формат неверный.
        """
        # Удаляем всё кроме цифр
        digits = re.sub(r"\D", "", v)

        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Неверный формат телефона")

        return digits


class DateRange(BaseModel):
    """Схема с валидацией диапазона дат."""

    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def validate_dates(self) -> "DateRange":
        """
        Валидировать диапазон дат.

        Returns:
            Валидная модель.

        Raises:
            ValueError: Если end_date раньше start_date.
        """
        if self.end_date < self.start_date:
            raise ValueError("end_date должна быть позже start_date")
        return self
```

---

## Вложенные схемы

```python
"""Вложенные схемы."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    """Элемент заказа."""

    product_id: UUID
    quantity: int = Field(..., ge=1)
    price: Decimal = Field(..., ge=0)


class OrderCreate(BaseModel):
    """Создание заказа."""

    customer_id: UUID
    items: list[OrderItem] = Field(..., min_length=1)
    notes: str | None = Field(None, max_length=500)


class OrderResponse(BaseModel):
    """Ответ с заказом."""

    id: UUID
    customer_id: UUID
    items: list[OrderItem]
    total: Decimal
    status: str
    created_at: datetime
```

---

## Enum и Literal

```python
"""Схемы с ограниченными значениями."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel


class OrderStatus(str, Enum):
    """Статусы заказа."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderFilter(BaseModel):
    """Фильтр заказов."""

    status: OrderStatus | None = None
    sort_by: Literal["created_at", "total", "status"] = "created_at"
    sort_order: Literal["asc", "desc"] = "desc"
```

---

## Схемы ошибок

```python
"""Схемы ошибок API."""

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Детали ошибки."""

    loc: list[str | int]
    msg: str
    type: str


class ErrorResponse(BaseModel):
    """Ответ с ошибкой."""

    detail: str
    errors: list[ErrorDetail] | None = None


class ValidationErrorResponse(BaseModel):
    """Ответ с ошибкой валидации."""

    detail: str = "Validation error"
    errors: list[ErrorDetail]
```

---

## Пагинация

```python
"""Схемы пагинации."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Пагинированный ответ."""

    items: list[T]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    pages: int = Field(..., ge=0)

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """
        Создать пагинированный ответ.

        Args:
            items: Элементы страницы.
            total: Общее количество.
            page: Текущая страница.
            page_size: Размер страницы.

        Returns:
            Пагинированный ответ.
        """
        pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )
```

---

## Правила

| Тип схемы | Паттерн | Пример |
|-----------|---------|--------|
| Создание | `{Entity}Create` | `UserCreate` |
| Обновление | `{Entity}Update` | `UserUpdate` |
| Ответ | `{Entity}Response` | `UserResponse` |
| Список | `{Entity}ListResponse` | `UserListResponse` |
| Фильтр | `{Entity}Filter` | `UserFilter` |
