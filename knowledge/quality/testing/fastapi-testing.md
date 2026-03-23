# FastAPI Testing

> **Purpose**: Testing patterns for FastAPI applications.

---

## Test Client

```python
"""Test client setup."""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from {context}_api.main import create_app


@pytest.fixture
def app() -> FastAPI:
    """Test application."""
    return create_app()


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    """Async test client."""
    async with AsyncClient(
        app=app,
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client
```

---

## Endpoint Testing

```python
"""API endpoint tests."""

import pytest
from uuid import uuid4


class TestUserAPI:
    """User API tests."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, client):
        """Successful user creation."""
        response = await client.post(
            "/api/v1/users",
            json={
                "name": "Test User",
                "email": "test@example.com",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test User"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_user_validation_error(self, client):
        """Validation error on creation."""
        response = await client.post(
            "/api/v1/users",
            json={
                "name": "",  # Empty name
                "email": "invalid-email",  # Invalid email
            },
        )

        assert response.status_code == 422
        errors = response.json()["errors"]
        assert len(errors) >= 1

    @pytest.mark.asyncio
    async def test_get_user_success(self, client, created_user):
        """Successful user retrieval."""
        response = await client.get(f"/api/v1/users/{created_user['id']}")

        assert response.status_code == 200
        assert response.json()["id"] == created_user["id"]

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client):
        """User not found."""
        response = await client.get(f"/api/v1/users/{uuid4()}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_users_pagination(self, client):
        """User list pagination."""
        response = await client.get(
            "/api/v1/users",
            params={"page": 1, "page_size": 10},
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data

    @pytest.mark.asyncio
    async def test_update_user_success(self, client, created_user):
        """Successful user update."""
        response = await client.put(
            f"/api/v1/users/{created_user['id']}",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete_user_success(self, client, created_user):
        """Successful user deletion."""
        response = await client.delete(f"/api/v1/users/{created_user['id']}")

        assert response.status_code == 204
```

---

## Testing with Mocks

```python
"""Tests with dependency mocks."""

import pytest
from unittest.mock import AsyncMock
from fastapi import FastAPI

from {context}_api.main import app
from {context}_api.api.dependencies import get_user_service
from {context}_api.application.services.user_service import UserService


@pytest.fixture
def mock_user_service() -> AsyncMock:
    """Mock UserService."""
    mock = AsyncMock(spec=UserService)
    return mock


@pytest.fixture
def app_with_mock_service(mock_user_service) -> FastAPI:
    """Application with mock service."""
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
async def client_with_mocks(app_with_mock_service) -> AsyncClient:
    """Client with mocks."""
    async with AsyncClient(app=app_with_mock_service, base_url="http://test") as client:
        yield client


class TestUserAPIWithMocks:
    """Tests with mocks."""

    @pytest.mark.asyncio
    async def test_get_user_calls_service(
        self,
        client_with_mocks,
        mock_user_service,
    ):
        """Verify service is called."""
        user_id = "123"
        mock_user_service.get_user.return_value = UserDTO(
            id=user_id,
            name="Test",
            email="test@example.com",
        )

        response = await client_with_mocks.get(f"/api/v1/users/{user_id}")

        assert response.status_code == 200
        mock_user_service.get_user.assert_called_once()
```

---

## Authentication Testing

```python
"""Authentication tests."""

import pytest


@pytest.fixture
def auth_headers() -> dict:
    """Authentication headers."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
async def authenticated_client(client, auth_headers) -> AsyncClient:
    """Client with authentication."""
    client.headers.update(auth_headers)
    return client


class TestAuthenticatedAPI:
    """Protected endpoint tests."""

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_auth(self, client):
        """Access without authentication is denied."""
        response = await client.get("/api/v1/protected")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_auth(self, authenticated_client):
        """Access with authentication is allowed."""
        response = await authenticated_client.get("/api/v1/protected")
        assert response.status_code == 200
```

---

## Error Handling Testing

```python
"""Error handling tests."""

import pytest
from unittest.mock import AsyncMock


class TestErrorHandling:
    """Error handling tests."""

    @pytest.mark.asyncio
    async def test_internal_error_returns_500(
        self,
        client_with_mocks,
        mock_user_service,
    ):
        """Internal error returns 500."""
        mock_user_service.get_user.side_effect = Exception("Internal error")

        response = await client_with_mocks.get("/api/v1/users/123")

        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_validation_error_format(self, client):
        """Validation error format."""
        response = await client.post(
            "/api/v1/users",
            json={"invalid": "data"},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "errors" in data
```

---

## File Upload Testing

```python
"""File upload tests."""

import pytest
from io import BytesIO


class TestFileUpload:
    """File upload tests."""

    @pytest.mark.asyncio
    async def test_upload_image(self, client):
        """Image upload."""
        file_content = b"fake image content"
        files = {"file": ("image.png", BytesIO(file_content), "image/png")}

        response = await client.post("/api/v1/upload", files=files)

        assert response.status_code == 200
        assert "url" in response.json()
```

---

## Checklist

- [ ] AsyncClient for async tests
- [ ] dependency_overrides for mocks
- [ ] Success scenario tests
- [ ] Error tests (4xx, 5xx)
- [ ] Validation tests
- [ ] Authentication tests
