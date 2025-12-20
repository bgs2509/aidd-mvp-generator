"""
Общие Pydantic схемы.

Базовые схемы для переиспользования во всех сервисах.
"""

from .base import (
    BaseSchema,
    BaseResponseSchema,
    TimestampMixin,
    IDMixin,
    FullModelMixin,
)
from .pagination import (
    PaginationQueryParams,
    PaginationResponse,
    PaginatedResponse,
    CursorPaginationQueryParams,
    CursorPaginationResponse,
)
from .errors import (
    ErrorDetail,
    ErrorResponse,
    ValidationErrorDetail,
    ValidationErrorResponse,
)

__all__ = [
    # Base
    "BaseSchema",
    "BaseResponseSchema",
    "TimestampMixin",
    "IDMixin",
    "FullModelMixin",
    # Pagination
    "PaginationQueryParams",
    "PaginationResponse",
    "PaginatedResponse",
    "CursorPaginationQueryParams",
    "CursorPaginationResponse",
    # Errors
    "ErrorDetail",
    "ErrorResponse",
    "ValidationErrorDetail",
    "ValidationErrorResponse",
]
