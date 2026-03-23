# Function: Stage 4.6 — Testing

> **Purpose**: Creating tests for all components.

---

## Goal

Create tests to achieve the required code coverage (>=75%)
and ensure implementation quality.

---

## Testing Requirements

### Level 2 (MVP)

```
REQUIRED:
✓ Unit tests
✓ Integration tests
✓ Coverage ≥75%

NOT REQUIRED:
✗ E2E tests
✗ Performance tests
✗ Security tests
```

---

## Test Structure

```
services/{context}_{service}/
└── tests/
    ├── __init__.py
    ├── conftest.py           # Shared fixtures
    ├── unit/                 # Unit tests
    │   ├── __init__.py
    │   ├── test_services.py
    │   └── test_repositories.py
    └── integration/          # Integration tests
        ├── __init__.py
        └── test_api.py
```

---

## Components

### 1. conftest.py (shared fixtures)

```python
"""Shared test fixtures."""

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


# Event loop setup for pytest-asyncio
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test database
@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create a test DB engine."""
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
    """Create a DB session for a test."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


# HTTP client for API tests
@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an HTTP client for API tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


# Factories for creating test data
@pytest.fixture
def {entity}_factory():
    """Factory for creating test {entities}."""
    from tests.factories import {Entity}Factory
    return {Entity}Factory
```

### 2. Factories (tests/factories.py)

```python
"""Factories for creating test data."""

from datetime import datetime
from uuid import uuid4

from {context}_{service}.domain.entities.{entity} import {Entity}


class {Entity}Factory:
    """Factory for creating test {entities}."""

    @staticmethod
    def create(**kwargs) -> {Entity}:
        """Create {entity} with test data."""
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
        """Create a dictionary with test data."""
        defaults = {
            "name": f"Test {Entity} {uuid4().hex[:6]}",
        }
        defaults.update(kwargs)
        return defaults
```

### 3. Service Unit Tests

```python
"""Unit tests for {Entity}Service."""

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
    """Tests for creating {entity}."""

    @pytest.mark.asyncio
    async def test_create_{entity}_success(self):
        """Successful {entity} creation."""
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
        """Validation error on creation."""
        # Arrange
        mock_client = AsyncMock()
        service = {Entity}Service(mock_client)

        # Act & Assert
        with pytest.raises(ValueError):
            dto = Create{Entity}DTO(name="")  # Empty name
            await service.create_{entity}(dto)


class TestGet{Entity}:
    """Tests for getting {entity}."""

    @pytest.mark.asyncio
    async def test_get_{entity}_success(self):
        """Successful {entity} retrieval."""
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
        """{Entity} not found."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.get_{entity}.return_value = None

        service = {Entity}Service(mock_client)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await service.get_{entity}(uuid4())


class TestUpdate{Entity}:
    """Tests for updating {entity}."""

    @pytest.mark.asyncio
    async def test_update_{entity}_success(self):
        """Successful {entity} update."""
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
    """Tests for deleting {entity}."""

    @pytest.mark.asyncio
    async def test_delete_{entity}_success(self):
        """Successful {entity} deletion."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.delete_{entity}.return_value = True

        service = {Entity}Service(mock_client)

        # Act & Assert (should not raise an exception)
        await service.delete_{entity}(uuid4())

    @pytest.mark.asyncio
    async def test_delete_{entity}_not_found(self):
        """{Entity} not found on deletion."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.delete_{entity}.return_value = False

        service = {Entity}Service(mock_client)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await service.delete_{entity}(uuid4())
```

### 4. Repository Unit Tests

```python
"""Unit tests for {Entity}Repository."""

import pytest
from uuid import uuid4

from {context}_data.infrastructure.repositories.{entity}_repository import (
    {Entity}Repository,
)


class TestCreate{Entity}:
    """Tests for repository creation."""

    @pytest.mark.asyncio
    async def test_create_{entity}(self, db_session, {entity}_factory):
        """Creating {entity} in the DB."""
        # Arrange
        repo = {Entity}Repository(db_session)
        data = {entity}_factory.create_dict()

        # Act
        result = await repo.create(**data)

        # Assert
        assert result.id is not None
        assert result.name == data["name"]


class TestGet{Entity}:
    """Tests for repository retrieval."""

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session, {entity}_factory):
        """Getting {entity} by ID."""
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
        """{Entity} not found."""
        # Arrange
        repo = {Entity}Repository(db_session)

        # Act
        result = await repo.get_by_id(uuid4())

        # Assert
        assert result is None


class TestList{Entities}:
    """Tests for listing."""

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, db_session, {entity}_factory):
        """Getting list with pagination."""
        # Arrange
        repo = {Entity}Repository(db_session)

        # Create 5 records
        for _ in range(5):
            await repo.create(**{entity}_factory.create_dict())

        # Act
        result = await repo.get_all(offset=0, limit=3)

        # Assert
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_count(self, db_session, {entity}_factory):
        """Record counting."""
        # Arrange
        repo = {Entity}Repository(db_session)

        for _ in range(3):
            await repo.create(**{entity}_factory.create_dict())

        # Act
        count = await repo.count()

        # Assert
        assert count >= 3
```

### 5. API Integration Tests

```python
"""Integration tests for {Entity} API."""

import pytest
from uuid import uuid4

from httpx import AsyncClient


class TestCreate{Entity}API:
    """Tests for creation via API."""

    @pytest.mark.asyncio
    async def test_create_{entity}_success(self, client: AsyncClient):
        """Successful creation via API."""
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
        """Validation error."""
        # Arrange
        data = {}  # Empty data

        # Act
        response = await client.post("/api/v1/{entities}", json=data)

        # Assert
        assert response.status_code == 422


class TestGet{Entity}API:
    """Tests for retrieval via API."""

    @pytest.mark.asyncio
    async def test_get_{entity}_success(self, client: AsyncClient):
        """Successful retrieval."""
        # Arrange - create {entity}
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
        """{Entity} not found."""
        # Act
        response = await client.get(f"/api/v1/{entities}/{uuid4()}")

        # Assert
        assert response.status_code == 404


class TestList{Entities}API:
    """Tests for listing via API."""

    @pytest.mark.asyncio
    async def test_list_{entities}(self, client: AsyncClient):
        """Getting the list."""
        # Arrange - create several {entities}
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
        """List pagination."""
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
    """Tests for updating via API."""

    @pytest.mark.asyncio
    async def test_update_{entity}_success(self, client: AsyncClient):
        """Successful update."""
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
    """Tests for deletion via API."""

    @pytest.mark.asyncio
    async def test_delete_{entity}_success(self, client: AsyncClient):
        """Successful deletion."""
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

        # Verify deletion
        get_response = await client.get(f"/api/v1/{entities}/{{{entity}_id}}")
        assert get_response.status_code == 404
```

---

## Running Tests

### Makefile Commands

```makefile
# All tests
test:
	pytest -v

# With coverage
test-cov:
	pytest --cov=src --cov-report=html --cov-report=term

# Unit tests only
test-unit:
	pytest tests/unit -v

# Integration tests only
test-integration:
	pytest tests/integration -v

# Coverage check
check-coverage:
	pytest --cov=src --cov-fail-under=75
```

---

## Quality Gates

### TESTS_READY

- [ ] Unit tests created for all services
- [ ] Unit tests created for all repositories
- [ ] Integration tests created for all API endpoints
- [ ] Coverage >=75%
- [ ] All tests pass (`pytest` without errors)

---

## References

| Document | Description |
|----------|-------------|
| `knowledge/quality/testing/pytest-setup.md` | pytest setup |
| `knowledge/quality/testing/fixture-patterns.md` | Fixture patterns |
| `knowledge/quality/testing/mocking.md` | Mocking strategies |
| `knowledge/quality/testing/fastapi-testing.md` | FastAPI testing |
