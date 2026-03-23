# Testcontainers

> **Purpose**: Using Testcontainers for integration tests.

---

## Installation

```bash
pip install testcontainers[postgres,redis]
```

---

## PostgreSQL Container

```python
"""Fixtures with PostgreSQL container."""

import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from {context}_data.domain.entities.base import Base


@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL container for tests."""
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def database_url(postgres_container) -> str:
    """Database URL."""
    # Convert sync URL to async
    sync_url = postgres_container.get_connection_url()
    return sync_url.replace("postgresql://", "postgresql+asyncpg://")


@pytest.fixture(scope="session")
async def engine(database_url):
    """SQLAlchemy engine."""
    engine = create_async_engine(database_url, echo=True)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncSession:
    """DB session with rollback."""
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()
```

---

## Redis Container

```python
"""Fixtures with Redis container."""

import pytest
from testcontainers.redis import RedisContainer
import redis.asyncio as redis


@pytest.fixture(scope="session")
def redis_container():
    """Redis container for tests."""
    with RedisContainer("redis:7-alpine") as redis_cont:
        yield redis_cont


@pytest.fixture(scope="session")
def redis_url(redis_container) -> str:
    """Redis URL."""
    host = redis_container.get_container_host_ip()
    port = redis_container.get_exposed_port(6379)
    return f"redis://{host}:{port}/0"


@pytest.fixture
async def redis_client(redis_url) -> redis.Redis:
    """Redis client."""
    client = redis.from_url(redis_url)
    yield client
    await client.flushall()
    await client.close()
```

---

## Full Stack

```python
"""Full stack fixtures."""

import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from httpx import AsyncClient

from {context}_api.main import create_app
from {context}_api.core.config import settings


@pytest.fixture(scope="session")
def containers():
    """All containers."""
    postgres = PostgresContainer("postgres:15-alpine")
    redis = RedisContainer("redis:7-alpine")

    postgres.start()
    redis.start()

    yield {
        "postgres": postgres,
        "redis": redis,
    }

    postgres.stop()
    redis.stop()


@pytest.fixture(scope="session")
def test_settings(containers):
    """Test settings."""
    postgres = containers["postgres"]
    redis = containers["redis"]

    return {
        "database_url": postgres.get_connection_url().replace(
            "postgresql://", "postgresql+asyncpg://"
        ),
        "redis_url": f"redis://{redis.get_container_host_ip()}:{redis.get_exposed_port(6379)}/0",
    }


@pytest.fixture(scope="session")
def app(test_settings):
    """Application with test settings."""
    # Override settings
    settings.database_url = test_settings["database_url"]
    settings.redis_url = test_settings["redis_url"]

    return create_app()


@pytest.fixture
async def client(app) -> AsyncClient:
    """Test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

---

## Integration Tests

```python
"""Integration tests with real DB."""

import pytest
from uuid import uuid4


@pytest.mark.integration
class TestUserIntegration:
    """User integration tests."""

    @pytest.mark.asyncio
    async def test_create_and_get_user(self, client):
        """Create and get a user."""
        # Create
        create_response = await client.post(
            "/api/v1/users",
            json={"name": "Test", "email": f"test_{uuid4().hex[:8]}@example.com"},
        )
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Get
        get_response = await client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Test"

    @pytest.mark.asyncio
    async def test_user_crud_flow(self, client):
        """Full CRUD flow."""
        # Create
        response = await client.post(
            "/api/v1/users",
            json={"name": "CRUD Test", "email": f"crud_{uuid4().hex[:8]}@example.com"},
        )
        user_id = response.json()["id"]

        # Read
        response = await client.get(f"/api/v1/users/{user_id}")
        assert response.json()["name"] == "CRUD Test"

        # Update
        response = await client.put(
            f"/api/v1/users/{user_id}",
            json={"name": "Updated"},
        )
        assert response.json()["name"] == "Updated"

        # Delete
        response = await client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 204

        # Verify deleted
        response = await client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 404
```

---

## conftest.py for integration

```python
"""conftest.py for integration tests."""

# tests/integration/conftest.py

import pytest

# Marker for all tests in directory
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def anyio_backend():
    """Backend for anyio."""
    return "asyncio"
```

---

## Running

```bash
# Integration tests only
pytest tests/integration -m integration

# With verbose
pytest tests/integration -v -s

# Specific file
pytest tests/integration/test_user_api.py
```

---

## Checklist

- [ ] testcontainers installed
- [ ] PostgresContainer configured
- [ ] RedisContainer configured
- [ ] scope="session" for containers
- [ ] Cleanup after tests
- [ ] @pytest.mark.integration marker
