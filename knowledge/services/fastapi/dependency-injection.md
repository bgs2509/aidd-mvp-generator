# FastAPI Dependency Injection

> **Purpose**: DI patterns in FastAPI.

---

## Basic Structure

```python
"""API dependencies."""

from fastapi import Depends, Request

from {context}_api.application.services.user_service import UserService
from {context}_api.infrastructure.http.data_api_client import DataApiClient


def get_http_client(request: Request) -> DataApiClient:
    """
    Get HTTP client from application state.

    Args:
        request: HTTP request.

    Returns:
        Configured HTTP client.
    """
    return DataApiClient(request.app.state.http_client)


def get_user_service(
    data_client: DataApiClient = Depends(get_http_client),
) -> UserService:
    """
    Create user service.

    Args:
        data_client: HTTP client for Data API.

    Returns:
        Service instance.
    """
    return UserService(data_client)


def get_order_service(
    data_client: DataApiClient = Depends(get_http_client),
) -> OrderService:
    """
    Create order service.

    Args:
        data_client: HTTP client for Data API.

    Returns:
        Service instance.
    """
    return OrderService(data_client)
```

---

## Dependency Graph

```
Request
    |
    v
get_http_client()
    |
    +-------------------+-------------------+
    v                   v                   v
get_user_service() get_order_service() get_restaurant_service()
    |                   |                   |
    v                   v                   v
UserRoutes          OrderRoutes         RestaurantRoutes
```

---

## Request-scoped Dependencies

```python
"""Request-scoped dependencies."""

from contextlib import asynccontextmanager
from fastapi import Depends, Request


async def get_request_id(request: Request) -> str:
    """
    Get request ID.

    Args:
        request: HTTP request.

    Returns:
        Request ID.
    """
    return getattr(request.state, "request_id", "unknown")


async def get_current_user(
    request: Request,
    user_service: UserService = Depends(get_user_service),
) -> User:
    """
    Get current user from token.

    Args:
        request: HTTP request.
        user_service: User service.

    Returns:
        Current user.

    Raises:
        HTTPException: If token is invalid.
    """
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = decode_token(token)
    return await user_service.get_user(user_id)
```

---

## Parameterized Dependencies

```python
"""Dependencies with parameters."""

from functools import lru_cache


class PaginationParams:
    """Pagination parameters."""

    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100,
    ):
        """
        Initialize parameters.

        Args:
            page: Page number.
            page_size: Page size.
            max_page_size: Maximum page size.
        """
        self.page = max(1, page)
        self.page_size = min(page_size, max_page_size)
        self.offset = (self.page - 1) * self.page_size


def pagination_params(
    page: int = 1,
    page_size: int = 20,
) -> PaginationParams:
    """
    Create pagination parameters.

    Args:
        page: Page number.
        page_size: Page size.

    Returns:
        Pagination parameters.
    """
    return PaginationParams(page=page, page_size=page_size)


# Usage
@router.get("")
async def list_items(
    pagination: PaginationParams = Depends(pagination_params),
):
    """List with pagination."""
    return await service.list(
        offset=pagination.offset,
        limit=pagination.page_size,
    )
```

---

## Dependency Factory

```python
"""Factory for creating dependencies with parameters."""

def get_service_with_config(service_class, config_key: str):
    """
    Create service factory with configuration.

    Args:
        service_class: Service class.
        config_key: Configuration key.

    Returns:
        Dependency function.
    """
    def dependency(
        data_client: DataApiClient = Depends(get_http_client),
    ):
        config = get_config(config_key)
        return service_class(data_client, config)

    return dependency


# Usage
get_order_service = get_service_with_config(OrderService, "orders")
```

---

## Dependency Caching

```python
"""Application-level caching."""

from functools import lru_cache


@lru_cache
def get_settings():
    """
    Get settings (cached).

    Returns:
        Settings object.
    """
    return Settings()


# Usage in routes
@router.get("/info")
async def get_info(
    settings = Depends(get_settings),
):
    """Service information."""
    return {"service": settings.service_name}
```

---

## Anti-patterns

```python
# BAD: Creating client on every request
def get_client():
    return httpx.AsyncClient()  # Resource leak!

# GOOD: Using application state
def get_client(request: Request):
    return request.app.state.http_client


# BAD: Global variables
_service = None

def get_service():
    global _service
    if _service is None:
        _service = MyService()
    return _service

# GOOD: Depends chain
def get_service(client = Depends(get_client)):
    return MyService(client)
```
