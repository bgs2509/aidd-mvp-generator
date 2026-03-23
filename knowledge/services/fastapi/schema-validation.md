# FastAPI Schema Validation

> **Purpose**: Pydantic schemas for data validation.

---

## Base Schemas

```python
"""Base Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common settings."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TimestampMixin(BaseModel):
    """Mixin with timestamps."""

    created_at: datetime
    updated_at: datetime | None = None


class IDMixin(BaseModel):
    """Mixin with identifier."""

    id: UUID
```

---

## CRUD Schemas

```python
"""User schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from {context}_api.schemas.base import BaseSchema, TimestampMixin


class UserBase(BaseModel):
    """Base user fields."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """User update schema."""

    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None


class UserResponse(UserBase, TimestampMixin, BaseSchema):
    """User response schema."""

    id: UUID
    is_active: bool = True


class UserListResponse(BaseModel):
    """User list schema."""

    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int
```

---

## Validators

```python
"""Schemas with custom validators."""

from pydantic import BaseModel, field_validator, model_validator
import re


class PhoneNumber(BaseModel):
    """Schema with phone validation."""

    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """
        Validate phone number.

        Args:
            v: Phone number.

        Returns:
            Normalized number.

        Raises:
            ValueError: If format is invalid.
        """
        # Remove everything except digits
        digits = re.sub(r"\D", "", v)

        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Invalid phone format")

        return digits


class DateRange(BaseModel):
    """Schema with date range validation."""

    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def validate_dates(self) -> "DateRange":
        """
        Validate date range.

        Returns:
            Valid model.

        Raises:
            ValueError: If end_date is before start_date.
        """
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self
```

---

## Nested Schemas

```python
"""Nested schemas."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    """Order item."""

    product_id: UUID
    quantity: int = Field(..., ge=1)
    price: Decimal = Field(..., ge=0)


class OrderCreate(BaseModel):
    """Order creation."""

    customer_id: UUID
    items: list[OrderItem] = Field(..., min_length=1)
    notes: str | None = Field(None, max_length=500)


class OrderResponse(BaseModel):
    """Order response."""

    id: UUID
    customer_id: UUID
    items: list[OrderItem]
    total: Decimal
    status: str
    created_at: datetime
```

---

## Enum and Literal

```python
"""Schemas with constrained values."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel


class OrderStatus(str, Enum):
    """Order statuses."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderFilter(BaseModel):
    """Order filter."""

    status: OrderStatus | None = None
    sort_by: Literal["created_at", "total", "status"] = "created_at"
    sort_order: Literal["asc", "desc"] = "desc"
```

---

## Error Schemas

```python
"""API error schemas."""

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error detail."""

    loc: list[str | int]
    msg: str
    type: str


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str
    errors: list[ErrorDetail] | None = None


class ValidationErrorResponse(BaseModel):
    """Validation error response."""

    detail: str = "Validation error"
    errors: list[ErrorDetail]
```

---

## Pagination

```python
"""Pagination schemas."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response."""

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
        Create paginated response.

        Args:
            items: Page items.
            total: Total count.
            page: Current page.
            page_size: Page size.

        Returns:
            Paginated response.
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

## Rules

| Schema Type | Pattern | Example |
|-------------|---------|---------|
| Create | `{Entity}Create` | `UserCreate` |
| Update | `{Entity}Update` | `UserUpdate` |
| Response | `{Entity}Response` | `UserResponse` |
| List | `{Entity}ListResponse` | `UserListResponse` |
| Filter | `{Entity}Filter` | `UserFilter` |
