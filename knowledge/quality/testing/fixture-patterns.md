# Паттерны фикстур pytest

> **Назначение**: Эффективное использование фикстур.

---

## Базовые фикстуры

```python
"""Базовые фикстуры."""

import pytest
from uuid import uuid4
from datetime import datetime


@pytest.fixture
def user_id() -> str:
    """Фиксированный UUID пользователя."""
    return str(uuid4())


@pytest.fixture
def current_time() -> datetime:
    """Текущее время."""
    return datetime.utcnow()


@pytest.fixture
def sample_user_data() -> dict:
    """Пример данных пользователя."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+79001234567",
    }
```

---

## Фикстуры с параметрами

```python
"""Параметризованные фикстуры."""

import pytest


@pytest.fixture(params=["active", "inactive", "blocked"])
def user_status(request) -> str:
    """Различные статусы пользователя."""
    return request.param


@pytest.fixture(params=[1, 10, 100])
def page_size(request) -> int:
    """Различные размеры страницы."""
    return request.param


# Тест будет запущен для каждого значения
def test_user_with_status(user_status):
    """Тест для каждого статуса."""
    assert user_status in ["active", "inactive", "blocked"]
```

---

## Фикстуры с scope

```python
"""Фикстуры с разным scope."""

import pytest


@pytest.fixture(scope="session")
def database_url() -> str:
    """URL базы данных (один на сессию)."""
    return "postgresql://test:test@localhost/test_db"


@pytest.fixture(scope="module")
def test_data() -> dict:
    """Тестовые данные (один на модуль)."""
    return {"key": "value"}


@pytest.fixture(scope="function")
def temp_user() -> dict:
    """Временный пользователь (для каждого теста)."""
    return {"id": str(uuid4()), "name": "Temp"}


@pytest.fixture(scope="class")
def shared_state() -> dict:
    """Общее состояние для класса тестов."""
    return {}
```

---

## Фикстуры моков

```python
"""Фикстуры для моков."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_data_client() -> AsyncMock:
    """Мок Data API клиента."""
    mock = AsyncMock()

    # Настройка возвращаемых значений
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
    """Мок Redis клиента."""
    mock = AsyncMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = 1
    return mock


@pytest.fixture
def mock_settings(monkeypatch):
    """Мок настроек."""
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATA_API_URL", "http://mock-api:8001")
```

---

## Фикстуры HTTP клиента

```python
"""Фикстуры для HTTP тестирования."""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from {context}_api.main import create_app


@pytest.fixture
def app() -> FastAPI:
    """Тестовое приложение."""
    return create_app()


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    """Асинхронный HTTP клиент."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def authenticated_client(client: AsyncClient) -> AsyncClient:
    """Клиент с аутентификацией."""
    client.headers["Authorization"] = "Bearer test-token"
    return client
```

---

## Фикстуры базы данных

```python
"""Фикстуры для БД."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from {context}_data.domain.entities.base import Base


@pytest.fixture(scope="session")
def engine():
    """Движок БД для тестов."""
    return create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5432/test_db",
        echo=True,
    )


@pytest.fixture(scope="function")
async def db_session(engine) -> AsyncSession:
    """Сессия БД с откатом после теста."""
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

## Фабрики

```python
"""Фабрики для создания тестовых данных."""

import pytest
from uuid import uuid4
from datetime import datetime


class UserFactory:
    """Фабрика пользователей."""

    @staticmethod
    def create(**kwargs) -> dict:
        """Создать пользователя."""
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
    """Фабрика заказов."""

    @staticmethod
    def create(user_id: str = None, **kwargs) -> dict:
        """Создать заказ."""
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
    """Фабрика пользователей."""
    return UserFactory


@pytest.fixture
def order_factory() -> type[OrderFactory]:
    """Фабрика заказов."""
    return OrderFactory


# Использование
def test_with_factory(user_factory, order_factory):
    """Тест с фабриками."""
    user = user_factory.create(name="Custom Name")
    order = order_factory.create(user_id=user["id"])

    assert order["user_id"] == user["id"]
```

---

## autouse фикстуры

```python
"""Автоматические фикстуры."""

import pytest


@pytest.fixture(autouse=True)
def reset_database(db_session):
    """Автоматический сброс БД перед каждым тестом."""
    yield
    # Cleanup после теста


@pytest.fixture(autouse=True)
def clear_cache(mock_redis):
    """Автоматическая очистка кэша."""
    mock_redis.flushall()
    yield
```

---

## Чек-лист

- [ ] Базовые фикстуры в conftest.py
- [ ] Моки для внешних сервисов
- [ ] Фабрики для тестовых данных
- [ ] Scope выбран правильно
- [ ] autouse для cleanup
