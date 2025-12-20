# Функция: Stage 4.6 — Тестирование

> **Назначение**: Создание тестов для всех компонентов.

---

## Цель

Создать тесты для достижения требуемого покрытия кода (≥75%)
и обеспечения качества реализации.

---

## Требования к тестированию

### Level 2 (MVP)

```
ОБЯЗАТЕЛЬНО:
✓ Unit тесты
✓ Integration тесты
✓ Coverage ≥75%

НЕ ТРЕБУЕТСЯ:
✗ E2E тесты
✗ Performance тесты
✗ Security тесты
```

---

## Структура тестов

```
services/{context}_{service}/
└── tests/
    ├── __init__.py
    ├── conftest.py           # Общие фикстуры
    ├── unit/                 # Unit тесты
    │   ├── __init__.py
    │   ├── test_services.py
    │   └── test_repositories.py
    └── integration/          # Integration тесты
        ├── __init__.py
        └── test_api.py
```

---

## Компоненты

### 1. conftest.py (общие фикстуры)

```python
"""Общие фикстуры для тестов."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from {context}_{service}.main import app
from {context}_{service}.domain.entities.base import Base
from {context}_{service}.core.config import settings


# Настройка event loop для pytest-asyncio
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Создать event loop для сессии тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Тестовая база данных
@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Создать тестовый движок БД."""
    engine = create_async_engine(
        settings.test_database_url,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Создать сессию БД для теста."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


# HTTP клиент для API тестов
@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Создать HTTP клиент для тестов API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


# Фабрики для создания тестовых данных
@pytest.fixture
def {entity}_factory():
    """Фабрика для создания тестовых {entities}."""
    from tests.factories import {Entity}Factory
    return {Entity}Factory
```

### 2. Фабрики (tests/factories.py)

```python
"""Фабрики для создания тестовых данных."""

from datetime import datetime
from uuid import uuid4

from {context}_{service}.domain.entities.{entity} import {Entity}


class {Entity}Factory:
    """Фабрика для создания тестовых {entities}."""

    @staticmethod
    def create(**kwargs) -> {Entity}:
        """Создать {entity} с тестовыми данными."""
        defaults = {
            "id": uuid4(),
            "name": f"Test {Entity} {uuid4().hex[:6]}",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        defaults.update(kwargs)
        return {Entity}(**defaults)

    @staticmethod
    def create_dict(**kwargs) -> dict:
        """Создать словарь с тестовыми данными."""
        defaults = {
            "name": f"Test {Entity} {uuid4().hex[:6]}",
        }
        defaults.update(kwargs)
        return defaults
```

### 3. Unit тесты сервисов

```python
"""Unit тесты для {Entity}Service."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from {context}_api.application.services.{entity}_service import {Entity}Service
from {context}_api.application.dtos.{entity}_dtos import (
    Create{Entity}DTO,
    Update{Entity}DTO,
)
from {context}_api.core.exceptions import NotFoundError


class TestCreate{Entity}:
    """Тесты создания {entity}."""

    @pytest.mark.asyncio
    async def test_create_{entity}_success(self):
        """Успешное создание {entity}."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.create_{entity}.return_value = {
            "id": str(uuid4()),
            "name": "Test",
        }

        service = {Entity}Service(mock_client)
        dto = Create{Entity}DTO(name="Test")

        # Act
        result = await service.create_{entity}(dto)

        # Assert
        assert result.name == "Test"
        mock_client.create_{entity}.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_{entity}_validation_error(self):
        """Ошибка валидации при создании."""
        # Arrange
        mock_client = AsyncMock()
        service = {Entity}Service(mock_client)

        # Act & Assert
        with pytest.raises(ValueError):
            dto = Create{Entity}DTO(name="")  # Пустое имя
            await service.create_{entity}(dto)


class TestGet{Entity}:
    """Тесты получения {entity}."""

    @pytest.mark.asyncio
    async def test_get_{entity}_success(self):
        """Успешное получение {entity}."""
        # Arrange
        {entity}_id = uuid4()
        mock_client = AsyncMock()
        mock_client.get_{entity}.return_value = {
            "id": str({entity}_id),
            "name": "Test",
        }

        service = {Entity}Service(mock_client)

        # Act
        result = await service.get_{entity}({entity}_id)

        # Assert
        assert result.name == "Test"

    @pytest.mark.asyncio
    async def test_get_{entity}_not_found(self):
        """{Entity} не найден."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.get_{entity}.return_value = None

        service = {Entity}Service(mock_client)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await service.get_{entity}(uuid4())


class TestUpdate{Entity}:
    """Тесты обновления {entity}."""

    @pytest.mark.asyncio
    async def test_update_{entity}_success(self):
        """Успешное обновление {entity}."""
        # Arrange
        {entity}_id = uuid4()
        mock_client = AsyncMock()
        mock_client.get_{entity}.return_value = {
            "id": str({entity}_id),
            "name": "Old Name",
        }
        mock_client.update_{entity}.return_value = {
            "id": str({entity}_id),
            "name": "New Name",
        }

        service = {Entity}Service(mock_client)
        dto = Update{Entity}DTO(name="New Name")

        # Act
        result = await service.update_{entity}({entity}_id, dto)

        # Assert
        assert result.name == "New Name"


class TestDelete{Entity}:
    """Тесты удаления {entity}."""

    @pytest.mark.asyncio
    async def test_delete_{entity}_success(self):
        """Успешное удаление {entity}."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.delete_{entity}.return_value = True

        service = {Entity}Service(mock_client)

        # Act & Assert (не должен бросить исключение)
        await service.delete_{entity}(uuid4())

    @pytest.mark.asyncio
    async def test_delete_{entity}_not_found(self):
        """{Entity} не найден при удалении."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.delete_{entity}.return_value = False

        service = {Entity}Service(mock_client)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await service.delete_{entity}(uuid4())
```

### 4. Unit тесты репозиториев

```python
"""Unit тесты для {Entity}Repository."""

import pytest
from uuid import uuid4

from {context}_data.infrastructure.repositories.{entity}_repository import (
    {Entity}Repository,
)


class TestCreate{Entity}:
    """Тесты создания в репозитории."""

    @pytest.mark.asyncio
    async def test_create_{entity}(self, db_session, {entity}_factory):
        """Создание {entity} в БД."""
        # Arrange
        repo = {Entity}Repository(db_session)
        data = {entity}_factory.create_dict()

        # Act
        result = await repo.create(**data)

        # Assert
        assert result.id is not None
        assert result.name == data["name"]


class TestGet{Entity}:
    """Тесты получения из репозитория."""

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session, {entity}_factory):
        """Получение {entity} по ID."""
        # Arrange
        repo = {Entity}Repository(db_session)
        created = await repo.create(**{entity}_factory.create_dict())

        # Act
        result = await repo.get_by_id(created.id)

        # Assert
        assert result is not None
        assert result.id == created.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session):
        """{Entity} не найден."""
        # Arrange
        repo = {Entity}Repository(db_session)

        # Act
        result = await repo.get_by_id(uuid4())

        # Assert
        assert result is None


class TestList{Entities}:
    """Тесты получения списка."""

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, db_session, {entity}_factory):
        """Получение списка с пагинацией."""
        # Arrange
        repo = {Entity}Repository(db_session)

        # Создаём 5 записей
        for _ in range(5):
            await repo.create(**{entity}_factory.create_dict())

        # Act
        result = await repo.get_all(offset=0, limit=3)

        # Assert
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_count(self, db_session, {entity}_factory):
        """Подсчёт записей."""
        # Arrange
        repo = {Entity}Repository(db_session)

        for _ in range(3):
            await repo.create(**{entity}_factory.create_dict())

        # Act
        count = await repo.count()

        # Assert
        assert count >= 3
```

### 5. Integration тесты API

```python
"""Integration тесты для {Entity} API."""

import pytest
from uuid import uuid4

from httpx import AsyncClient


class TestCreate{Entity}API:
    """Тесты создания через API."""

    @pytest.mark.asyncio
    async def test_create_{entity}_success(self, client: AsyncClient):
        """Успешное создание через API."""
        # Arrange
        data = {"name": "Test Entity"}

        # Act
        response = await client.post("/api/v1/{entities}", json=data)

        # Assert
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == "Test Entity"
        assert "id" in result

    @pytest.mark.asyncio
    async def test_create_{entity}_validation_error(self, client: AsyncClient):
        """Ошибка валидации."""
        # Arrange
        data = {}  # Пустые данные

        # Act
        response = await client.post("/api/v1/{entities}", json=data)

        # Assert
        assert response.status_code == 422


class TestGet{Entity}API:
    """Тесты получения через API."""

    @pytest.mark.asyncio
    async def test_get_{entity}_success(self, client: AsyncClient):
        """Успешное получение."""
        # Arrange - создаём {entity}
        create_response = await client.post(
            "/api/v1/{entities}",
            json={"name": "Test"},
        )
        {entity}_id = create_response.json()["id"]

        # Act
        response = await client.get(f"/api/v1/{entities}/{{{entity}_id}}")

        # Assert
        assert response.status_code == 200
        assert response.json()["id"] == {entity}_id

    @pytest.mark.asyncio
    async def test_get_{entity}_not_found(self, client: AsyncClient):
        """{Entity} не найден."""
        # Act
        response = await client.get(f"/api/v1/{entities}/{uuid4()}")

        # Assert
        assert response.status_code == 404


class TestList{Entities}API:
    """Тесты списка через API."""

    @pytest.mark.asyncio
    async def test_list_{entities}(self, client: AsyncClient):
        """Получение списка."""
        # Arrange - создаём несколько {entities}
        for i in range(3):
            await client.post(
                "/api/v1/{entities}",
                json={"name": f"Test {i}"},
            )

        # Act
        response = await client.get("/api/v1/{entities}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "items" in result
        assert "total" in result

    @pytest.mark.asyncio
    async def test_list_{entities}_pagination(self, client: AsyncClient):
        """Пагинация списка."""
        # Act
        response = await client.get(
            "/api/v1/{entities}",
            params={"page": 1, "page_size": 10},
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["page"] == 1
        assert result["page_size"] == 10


class TestUpdate{Entity}API:
    """Тесты обновления через API."""

    @pytest.mark.asyncio
    async def test_update_{entity}_success(self, client: AsyncClient):
        """Успешное обновление."""
        # Arrange
        create_response = await client.post(
            "/api/v1/{entities}",
            json={"name": "Old Name"},
        )
        {entity}_id = create_response.json()["id"]

        # Act
        response = await client.put(
            f"/api/v1/{entities}/{{{entity}_id}}",
            json={"name": "New Name"},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"


class TestDelete{Entity}API:
    """Тесты удаления через API."""

    @pytest.mark.asyncio
    async def test_delete_{entity}_success(self, client: AsyncClient):
        """Успешное удаление."""
        # Arrange
        create_response = await client.post(
            "/api/v1/{entities}",
            json={"name": "To Delete"},
        )
        {entity}_id = create_response.json()["id"]

        # Act
        response = await client.delete(f"/api/v1/{entities}/{{{entity}_id}}")

        # Assert
        assert response.status_code == 204

        # Проверяем, что удалено
        get_response = await client.get(f"/api/v1/{entities}/{{{entity}_id}}")
        assert get_response.status_code == 404
```

---

## Запуск тестов

### Makefile команды

```makefile
# Все тесты
test:
	pytest -v

# С покрытием
test-cov:
	pytest --cov=src --cov-report=html --cov-report=term

# Только unit тесты
test-unit:
	pytest tests/unit -v

# Только integration тесты
test-integration:
	pytest tests/integration -v

# Проверка покрытия
check-coverage:
	pytest --cov=src --cov-fail-under=75
```

---

## Качественные ворота

### TESTS_READY

- [ ] Unit тесты созданы для всех сервисов
- [ ] Unit тесты созданы для всех репозиториев
- [ ] Integration тесты созданы для всех API эндпоинтов
- [ ] Coverage ≥75%
- [ ] Все тесты проходят (`pytest` без ошибок)

---

## Источники

| Документ | Описание |
|----------|----------|
| `knowledge/quality/testing/pytest-setup.md` | Настройка pytest |
| `knowledge/quality/testing/fixture-patterns.md` | Паттерны фикстур |
| `knowledge/quality/testing/mocking.md` | Стратегии мокирования |
| `knowledge/quality/testing/fastapi-testing.md` | Тестирование FastAPI |
