"""
Общие утилиты.

Переиспользуемые функции и классы для всех сервисов.
"""

from .logger import setup_logging, get_logger
from .validators import (
    validate_email,
    validate_phone,
    validate_slug,
    validate_uuid,
    validate_positive,
    validate_non_negative,
    validate_range,
    validate_length,
    validate_not_empty,
    pydantic_email_validator,
    pydantic_phone_validator,
    pydantic_slug_validator,
)
from .exceptions import (
    BaseAppException,
    ValidationError,
    InvalidInputError,
    NotFoundError,
    AlreadyExistsError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
    ExternalServiceError,
    ServiceUnavailableError,
    TimeoutError,
    BusinessLogicError,
    InsufficientFundsError,
    QuotaExceededError,
    RateLimitError,
)
from .pagination import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    PaginationParams,
    PaginationMeta,
    PaginatedResult,
    paginate_list,
    CursorPaginationParams,
    CursorPaginationMeta,
    CursorPaginatedResult,
)
from .request_id import (
    REQUEST_ID_HEADER,
    CORRELATION_ID_HEADER,
    generate_request_id,
    get_request_id,
    set_request_id,
    get_or_create_request_id,
    RequestIdContext,
    with_request_id,
    extract_request_id_from_headers,
    create_request_id_headers,
)

__all__ = [
    # Logger
    "setup_logging",
    "get_logger",
    # Validators
    "validate_email",
    "validate_phone",
    "validate_slug",
    "validate_uuid",
    "validate_positive",
    "validate_non_negative",
    "validate_range",
    "validate_length",
    "validate_not_empty",
    "pydantic_email_validator",
    "pydantic_phone_validator",
    "pydantic_slug_validator",
    # Exceptions
    "BaseAppException",
    "ValidationError",
    "InvalidInputError",
    "NotFoundError",
    "AlreadyExistsError",
    "ConflictError",
    "UnauthorizedError",
    "ForbiddenError",
    "ExternalServiceError",
    "ServiceUnavailableError",
    "TimeoutError",
    "BusinessLogicError",
    "InsufficientFundsError",
    "QuotaExceededError",
    "RateLimitError",
    # Pagination
    "DEFAULT_PAGE",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "PaginationParams",
    "PaginationMeta",
    "PaginatedResult",
    "paginate_list",
    "CursorPaginationParams",
    "CursorPaginationMeta",
    "CursorPaginatedResult",
    # Request ID
    "REQUEST_ID_HEADER",
    "CORRELATION_ID_HEADER",
    "generate_request_id",
    "get_request_id",
    "set_request_id",
    "get_or_create_request_id",
    "RequestIdContext",
    "with_request_id",
    "extract_request_id_from_headers",
    "create_request_id_headers",
]
