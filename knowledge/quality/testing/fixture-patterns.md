# pytest Fixture Patterns

> **Purpose**: Effective use of fixtures.

---

## Basic Fixtures

```python
"""Basic fixtures."""

import pytest
from uuid import uuid4
from datetime import datetime


@pytest.fixture
def user_id() -> str:
    """Fixed user UUID."""
    return str(uuid4())


@pytest.fixture
def current_time() -> datetime:
    """Current time."""
    return datetime.utcnow()


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user data."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+79001234567",
    }
```

---

## Parameterized Fixtures

```python
"""Parameterized fixtures."""

import pytest


@pytest.fixture(params=["active", "inactive", "blocked"])
def user_status(request) -> str:
    """Various user statuses."""
    return request.param


@pytest.fixture(params=[1, 10, 100])
def page_size(request) -> int:
    """Various page sizes."""
    return request.param


# Test will run for each value
def test_user_with_status(user_status):
    """Test for each status."""
    assert user_status in ["active", "inactive", "blocked"]
```

---

## Fixtures with Scope

```python
"""Fixtures with different scopes."""

import pytest


@pytest.fixture(scope="session")
def database_url() -> str:
    """Database URL (one per session)."""
    return "postgresql://test:test@localhost/test_db"


@pytest.fixture(scope="module")
def test_data() -> dict:
    """Test data (one per module)."""
    return {"key": "value"}


@pytest.fixture(scope="function")
def temp_user() -> dict:
    """Temporary user (for each test)."""
    return {"id": str(uuid4()), "name": "Temp"}


@pytest.fixture(scope="class")
def shared_state() -> dict:
    """Shared state for test class."""
    return {}
```

---

## Mock Fixtures

```python
"""Mock fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_data_client() -> AsyncMock:
    """Mock Data API client."""
    mock = AsyncMock()

    # Set up return values
    mock.get_user.return_value = {
        "id": "123",
        "name": "Test",
        "email": "test@example.com",
    }
    mock.create_user.return_value = {
        "id": "456",
        "name": "New User",
        "email": "new@example.com",
    }

    return mock


@pytest.fixture
def mock_redis() -> AsyncMock:
    """Mock Redis client."""
    mock = AsyncMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = 1
    return mock


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings."""
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATA_API_URL", "http://mock-api:8001")
```

---

## HTTP Client Fixtures

```python
"""HTTP testing fixtures."""

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
    """Async HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def authenticated_client(client: AsyncClient) -> AsyncClient:
    """Client with authentication."""
    client.headers["Authorization"] = "Bearer test-token"
    return client
```

---

## Database Fixtures

```python
"""Database fixtures."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from {context}_data.domain.entities.base import Base


@pytest.fixture(scope="session")
def engine():
    """DB engine for tests."""
    return create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5432/test_db",
        echo=True,
    )


@pytest.fixture(scope="function")
async def db_session(engine) -> AsyncSession:
    """DB session with rollback after test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

---

## Factories

```python
"""Factories for creating test data."""

import pytest
from uuid import uuid4
from datetime import datetime


class UserFactory:
    """User factory."""

    @staticmethod
    def create(**kwargs) -> dict:
        """Create a user."""
        defaults = {
            "id": str(uuid4()),
            "name": "Test User",
            "email": f"user_{uuid4().hex[:8]}@example.com",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
        }
        defaults.update(kwargs)
        return defaults


class OrderFactory:
    """Order factory."""

    @staticmethod
    def create(user_id: str = None, **kwargs) -> dict:
        """Create an order."""
        defaults = {
            "id": str(uuid4()),
            "user_id": user_id or str(uuid4()),
            "status": "pending",
            "total": "100.00",
            "items": [],
            "created_at": datetime.utcnow().isoformat(),
        }
        defaults.update(kwargs)
        return defaults


@pytest.fixture
def user_factory() -> type[UserFactory]:
    """User factory."""
    return UserFactory


@pytest.fixture
def order_factory() -> type[OrderFactory]:
    """Order factory."""
    return OrderFactory


# Usage
def test_with_factory(user_factory, order_factory):
    """Test with factories."""
    user = user_factory.create(name="Custom Name")
    order = order_factory.create(user_id=user["id"])

    assert order["user_id"] == user["id"]
```

---

## autouse Fixtures

```python
"""Automatic fixtures."""

import pytest


@pytest.fixture(autouse=True)
def reset_database(db_session):
    """Automatic DB reset before each test."""
    yield
    # Cleanup after test


@pytest.fixture(autouse=True)
def clear_cache(mock_redis):
    """Automatic cache clearing."""
    mock_redis.flushall()
    yield
```

---

## Checklist

- [ ] Basic fixtures in conftest.py
- [ ] Mocks for external services
- [ ] Factories for test data
- [ ] Scope chosen correctly
- [ ] autouse for cleanup
