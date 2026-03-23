# HTTP Calls Business → Data API

> **Purpose**: Patterns for Business API interaction with Data API.

---

## HTTP-only Principle

```
┌─────────────────┐    HTTP     ┌─────────────────┐    SQL     ┌──────────────┐
│  Business API   │────────────>│    Data API     │───────────>│  PostgreSQL  │
│ (business logic)│<────────────│ (data access)   │<───────────│   (DB)       │
└─────────────────┘             └─────────────────┘            └──────────────┘

Business API NEVER accesses the database directly
All data operations go through HTTP to Data API
```

---

## HTTP Client

```python
"""HTTP client for Data API."""

from typing import Any
from uuid import UUID

import httpx

from {context}_api.core.config import settings


class DataApiClient:
    """Client for interacting with Data API."""

    def __init__(self, client: httpx.AsyncClient):
        """
        Initialize client.

        Args:
            client: httpx.AsyncClient instance.
        """
        self.client = client
        self.base_url = settings.data_api_url

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        """
        Execute HTTP request.

        Args:
            method: HTTP method.
            path: API path.
            **kwargs: Additional parameters.

        Returns:
            API response.

        Raises:
            DataApiError: On API error.
        """
        url = f"{self.base_url}{path}"

        response = await self.client.request(method, url, **kwargs)

        if response.status_code == 204:
            return None

        if response.status_code >= 400:
            raise DataApiError(
                message=response.text,
                status_code=response.status_code,
            )

        return response.json()

    # === Users ===

    async def get_user(self, user_id: UUID) -> dict | None:
        """
        Get a user.

        Args:
            user_id: User ID.

        Returns:
            User data or None.
        """
        try:
            return await self._request("GET", f"/api/v1/users/{user_id}")
        except DataApiError as e:
            if e.status_code == 404:
                return None
            raise

    async def create_user(self, data: dict) -> dict:
        """
        Create a user.

        Args:
            data: User data.

        Returns:
            Created user.
        """
        return await self._request("POST", "/api/v1/users", json=data)

    async def update_user(self, user_id: UUID, data: dict) -> dict:
        """
        Update a user.

        Args:
            user_id: User ID.
            data: Update data.

        Returns:
            Updated user.
        """
        return await self._request("PUT", f"/api/v1/users/{user_id}", json=data)

    async def delete_user(self, user_id: UUID) -> None:
        """
        Delete a user.

        Args:
            user_id: User ID.
        """
        await self._request("DELETE", f"/api/v1/users/{user_id}")

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        Get user list.

        Args:
            page: Page number.
            page_size: Page size.

        Returns:
            User list with pagination metadata.
        """
        return await self._request(
            "GET",
            "/api/v1/users",
            params={"page": page, "page_size": page_size},
        )

    async def get_user_by_email(self, email: str) -> dict | None:
        """
        Get user by email.

        Args:
            email: User email.

        Returns:
            User data or None.
        """
        try:
            return await self._request(
                "GET",
                "/api/v1/users/by-email",
                params={"email": email},
            )
        except DataApiError as e:
            if e.status_code == 404:
                return None
            raise

    # === Orders ===

    async def get_order(self, order_id: UUID) -> dict | None:
        """Get an order."""
        try:
            return await self._request("GET", f"/api/v1/orders/{order_id}")
        except DataApiError as e:
            if e.status_code == 404:
                return None
            raise

    async def create_order(self, data: dict) -> dict:
        """Create an order."""
        return await self._request("POST", "/api/v1/orders", json=data)

    async def get_user_orders(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Get user orders."""
        return await self._request(
            "GET",
            f"/api/v1/users/{user_id}/orders",
            params={"page": page, "page_size": page_size},
        )
```

---

## Usage in Service

```python
"""Application Service with HTTP client."""

from uuid import UUID

from {context}_api.application.dtos.user_dtos import CreateUserDTO, UserDTO
from {context}_api.core.exceptions import NotFoundError, ValidationError
from {context}_api.infrastructure.http.data_api_client import DataApiClient


class UserService:
    """User service."""

    def __init__(self, data_client: DataApiClient):
        """
        Initialize service.

        Args:
            data_client: HTTP client for Data API.
        """
        self.data_client = data_client

    async def create_user(self, dto: CreateUserDTO) -> UserDTO:
        """
        Create a user.

        Args:
            dto: Creation data.

        Returns:
            Created user.

        Raises:
            ValidationError: If email already exists.
        """
        # Uniqueness check (business logic)
        existing = await self.data_client.get_user_by_email(dto.email)
        if existing:
            raise ValidationError(
                message=f"Email {dto.email} already exists",
                field="email",
            )

        # Create via Data API
        result = await self.data_client.create_user(dto.model_dump())
        return UserDTO.model_validate(result)

    async def get_user(self, user_id: UUID) -> UserDTO:
        """
        Get a user.

        Args:
            user_id: User ID.

        Returns:
            User data.

        Raises:
            NotFoundError: If not found.
        """
        result = await self.data_client.get_user(user_id)
        if result is None:
            raise NotFoundError("User", str(user_id))
        return UserDTO.model_validate(result)
```

---

## Lifespan Setup

```python
"""HTTP client management in lifespan."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx

from {context}_api.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle."""
    # Create HTTP client
    app.state.http_client = httpx.AsyncClient(
        base_url=settings.data_api_url,
        timeout=httpx.Timeout(30.0),
        headers={"Content-Type": "application/json"},
    )

    yield

    # Close client
    await app.state.http_client.aclose()
```

---

## Request ID Forwarding

```python
"""Request ID forwarding between services."""

from fastapi import Request


class DataApiClient:
    """Client with request_id forwarding."""

    def __init__(self, client: httpx.AsyncClient, request_id: str | None = None):
        """Initialize."""
        self.client = client
        self.request_id = request_id

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Execute request with request_id."""
        headers = kwargs.pop("headers", {})

        if self.request_id:
            headers["X-Request-ID"] = self.request_id

        return await self.client.request(
            method,
            path,
            headers=headers,
            **kwargs,
        )


# In dependencies.py
def get_data_client(request: Request) -> DataApiClient:
    """Create client with request_id."""
    request_id = getattr(request.state, "request_id", None)
    return DataApiClient(
        request.app.state.http_client,
        request_id=request_id,
    )
```

---

## Checklist

- [ ] Business API has no direct DB access
- [ ] All data retrieved through Data API
- [ ] HTTP client created in lifespan
- [ ] Request ID forwarded between services
- [ ] Data API errors handled
