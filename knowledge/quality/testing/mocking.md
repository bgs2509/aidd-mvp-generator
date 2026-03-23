# Mocking Strategies

> **Purpose**: Mocking patterns for isolated tests.

---

## AsyncMock

```python
"""Mocking asynchronous functions."""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_service() -> AsyncMock:
    """Mock async service."""
    mock = AsyncMock()

    # Set up return values
    mock.get_user.return_value = {"id": "123", "name": "Test"}
    mock.create_user.return_value = {"id": "456", "name": "New"}

    # Set up side_effect
    mock.delete_user.side_effect = None  # Returns None

    return mock


@pytest.mark.asyncio
async def test_with_async_mock(mock_service):
    """Test with async mock."""
    result = await mock_service.get_user("123")

    assert result["name"] == "Test"
    mock_service.get_user.assert_called_once_with("123")
```

---

## HTTP Client Mocking

```python
"""Mocking httpx."""

import pytest
from unittest.mock import AsyncMock
import httpx


@pytest.fixture
def mock_http_client() -> AsyncMock:
    """Mock httpx.AsyncClient."""
    mock = AsyncMock(spec=httpx.AsyncClient)

    # Successful GET
    mock.get.return_value = httpx.Response(
        200,
        json={"id": "123", "name": "Test"},
    )

    # Successful POST
    mock.post.return_value = httpx.Response(
        201,
        json={"id": "456", "name": "Created"},
    )

    # 404 for specific call
    async def get_side_effect(url, **kwargs):
        if "nonexistent" in url:
            return httpx.Response(404, json={"detail": "Not found"})
        return httpx.Response(200, json={"id": "123"})

    mock.get.side_effect = get_side_effect

    return mock


@pytest.mark.asyncio
async def test_http_client_mock(mock_http_client):
    """Test with mock HTTP client."""
    # Successful request
    response = await mock_http_client.get("/api/v1/users/123")
    assert response.status_code == 200

    # 404
    response = await mock_http_client.get("/api/v1/users/nonexistent")
    assert response.status_code == 404
```

---

## respx for HTTP Mocking

```python
"""Mocking with respx."""

import pytest
import respx
import httpx


@pytest.fixture
def mock_data_api():
    """Mock Data API with respx."""
    with respx.mock(base_url="http://data-api:8001") as respx_mock:
        # GET user
        respx_mock.get("/api/v1/users/123").respond(
            json={"id": "123", "name": "Test"},
        )

        # POST user
        respx_mock.post("/api/v1/users").respond(
            status_code=201,
            json={"id": "456", "name": "New"},
        )

        # 404
        respx_mock.get("/api/v1/users/999").respond(status_code=404)

        yield respx_mock


@pytest.mark.asyncio
async def test_with_respx(mock_data_api):
    """Test with respx."""
    async with httpx.AsyncClient(base_url="http://data-api:8001") as client:
        response = await client.get("/api/v1/users/123")
        assert response.json()["name"] == "Test"

        response = await client.get("/api/v1/users/999")
        assert response.status_code == 404
```

---

## FastAPI Dependency Mocking

```python
"""Mocking DI in FastAPI."""

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from unittest.mock import AsyncMock

from {context}_api.main import app
from {context}_api.api.dependencies import get_user_service


@pytest.fixture
def mock_user_service() -> AsyncMock:
    """Mock UserService."""
    mock = AsyncMock()
    mock.get_user.return_value = UserDTO(
        id="123",
        name="Test",
        email="test@example.com",
    )
    return mock


@pytest.fixture
def app_with_mocks(mock_user_service) -> FastAPI:
    """Application with overridden dependencies."""
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    yield app
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_with_dependency_mock(app_with_mocks):
    """Test with dependency override."""
    async with AsyncClient(app=app_with_mocks, base_url="http://test") as client:
        response = await client.get("/api/v1/users/123")
        assert response.status_code == 200
        assert response.json()["name"] == "Test"
```

---

## patch and monkeypatch

```python
"""Using patch and monkeypatch."""

import pytest
from unittest.mock import patch, AsyncMock


# unittest.mock.patch
@pytest.mark.asyncio
async def test_with_patch():
    """Test with patch."""
    with patch(
        "{context}_api.infrastructure.http.data_api_client.DataApiClient.get_user",
        new_callable=AsyncMock,
        return_value={"id": "123", "name": "Test"},
    ):
        # Code that uses DataApiClient.get_user
        pass


# pytest monkeypatch
def test_with_monkeypatch(monkeypatch):
    """Test with monkeypatch."""
    # Environment variables
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("DATA_API_URL", "http://mock:8001")

    # Module attributes
    monkeypatch.setattr("module.attribute", "new_value")

    # Remove attribute
    monkeypatch.delattr("module.attribute", raising=False)
```

---

## Time Mocking

```python
"""Mocking datetime."""

import pytest
from datetime import datetime
from unittest.mock import patch
from freezegun import freeze_time


# With freezegun
@freeze_time("2024-01-15 12:00:00")
def test_with_frozen_time():
    """Test with frozen time."""
    assert datetime.now() == datetime(2024, 1, 15, 12, 0, 0)


# With patch
def test_with_patched_time():
    """Test with patched time."""
    fixed_time = datetime(2024, 1, 15, 12, 0, 0)

    with patch("module.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = fixed_time
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # Test
        pass
```

---

## Call Verification

```python
"""Mock call verification."""

import pytest
from unittest.mock import AsyncMock, call


@pytest.mark.asyncio
async def test_mock_calls():
    """Call verification."""
    mock = AsyncMock()

    await mock.method("arg1", key="value")
    await mock.method("arg2")

    # Check call count
    assert mock.method.call_count == 2

    # Check specific call
    mock.method.assert_called_with("arg2")
    mock.method.assert_any_call("arg1", key="value")

    # Check all calls
    mock.method.assert_has_calls([
        call("arg1", key="value"),
        call("arg2"),
    ])

    # Check called at least once
    mock.method.assert_called()

    # Check not called
    mock.other_method.assert_not_called()
```

---

## Checklist

- [ ] AsyncMock for async functions
- [ ] respx for HTTP clients
- [ ] dependency_overrides for FastAPI
- [ ] monkeypatch for env
- [ ] freezegun for time
- [ ] assert_called for call verification
