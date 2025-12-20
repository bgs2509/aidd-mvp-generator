# Testcontainers

> **Назначение**: Использование Testcontainers для integration тестов.

---

## Установка

```bash
pip install testcontainers[postgres,redis]
```

---

## PostgreSQL контейнер

```python
"""Фикстуры с PostgreSQL контейнером."""

import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from {context}_data.domain.entities.base import Base


@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL контейнер для тестов."""
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def database_url(postgres_container) -> str:
    """URL базы данных."""
    # Преобразуем sync URL в async
    sync_url = postgres_container.get_connection_url()
    return sync_url.replace("postgresql://", "postgresql+asyncpg://")


@pytest.fixture(scope="session")
async def engine(database_url):
    """Движок SQLAlchemy."""
    engine = create_async_engine(database_url, echo=True)

    # Создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Удаление таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncSession:
    """Сессия БД с откатом."""
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

## Redis контейнер

```python
"""Фикстуры с Redis контейнером."""

import pytest
from testcontainers.redis import RedisContainer
import redis.asyncio as redis


@pytest.fixture(scope="session")
def redis_container():
    """Redis контейнер для тестов."""
    with RedisContainer("redis:7-alpine") as redis_cont:
        yield redis_cont


@pytest.fixture(scope="session")
def redis_url(redis_container) -> str:
    """URL Redis."""
    host = redis_container.get_container_host_ip()
    port = redis_container.get_exposed_port(6379)
    return f"redis://{host}:{port}/0"


@pytest.fixture
async def redis_client(redis_url) -> redis.Redis:
    """Клиент Redis."""
    client = redis.from_url(redis_url)
    yield client
    await client.flushall()
    await client.close()
```

---

## Полный стек

```python
"""Фикстуры полного стека."""

import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from httpx import AsyncClient

from {context}_api.main import create_app
from {context}_api.core.config import settings


@pytest.fixture(scope="session")
def containers():
    """Все контейнеры."""
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
    """Настройки для тестов."""
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
    """Приложение с тестовыми настройками."""
    # Подмена настроек
    settings.database_url = test_settings["database_url"]
    settings.redis_url = test_settings["redis_url"]

    return create_app()


@pytest.fixture
async def client(app) -> AsyncClient:
    """Тест-клиент."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

---

## Integration тесты

```python
"""Integration тесты с реальной БД."""

import pytest
from uuid import uuid4


@pytest.mark.integration
class TestUserIntegration:
    """Integration тесты пользователей."""

    @pytest.mark.asyncio
    async def test_create_and_get_user(self, client):
        """Создание и получение пользователя."""
        # Создание
        create_response = await client.post(
            "/api/v1/users",
            json={"name": "Test", "email": f"test_{uuid4().hex[:8]}@example.com"},
        )
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Получение
        get_response = await client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Test"

    @pytest.mark.asyncio
    async def test_user_crud_flow(self, client):
        """Полный CRUD flow."""
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

## conftest.py для integration

```python
"""conftest.py для integration тестов."""

# tests/integration/conftest.py

import pytest

# Маркер для всех тестов в директории
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def anyio_backend():
    """Бэкенд для anyio."""
    return "asyncio"
```

---

## Запуск

```bash
# Только integration тесты
pytest tests/integration -m integration

# С verbose
pytest tests/integration -v -s

# Конкретный файл
pytest tests/integration/test_user_api.py
```

---

## Чек-лист

- [ ] testcontainers установлен
- [ ] PostgresContainer настроен
- [ ] RedisContainer настроен
- [ ] scope="session" для контейнеров
- [ ] Cleanup после тестов
- [ ] Маркер @pytest.mark.integration
