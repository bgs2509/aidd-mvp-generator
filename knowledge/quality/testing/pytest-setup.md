# pytest Setup

> **Purpose**: Basic pytest setup for the project.

---

## pyproject.toml

```toml
# pyproject.toml

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "-ra",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow tests",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]
```

---

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── conftest.py         # Unit fixtures
│   ├── test_user_service.py
│   └── test_order_service.py
├── integration/            # Integration tests
│   ├── __init__.py
│   ├── conftest.py         # Integration fixtures
│   ├── test_user_api.py
│   └── test_order_api.py
└── e2e/                    # E2E tests (optional)
    ├── __init__.py
    └── test_user_flow.py
```

---

## conftest.py

```python
"""Shared fixtures."""

import pytest
from unittest.mock import AsyncMock

import httpx
from fastapi.testclient import TestClient
from httpx import AsyncClient

from {context}_api.main import app


@pytest.fixture
def client() -> TestClient:
    """Synchronous test client."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncClient:
    """Async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_http_client() -> AsyncMock:
    """Mock HTTP client."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def anyio_backend() -> str:
    """Backend for anyio."""
    return "asyncio"
```

---

## requirements-dev.txt

```
# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
pytest-xdist>=3.3.0

# HTTP testing
httpx>=0.24.0

# Mocking
respx>=0.20.0

# Factories
factory-boy>=3.3.0

# Async
anyio>=3.7.0
```

---

## Run Commands

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=term --cov-report=html

# Check coverage threshold
pytest --cov=src --cov-fail-under=75

# Unit tests only
pytest tests/unit -m unit

# Integration tests only
pytest tests/integration -m integration

# Parallel run
pytest -n auto

# Specific file
pytest tests/unit/test_user_service.py

# Specific test
pytest tests/unit/test_user_service.py::TestUserService::test_create_user

# Verbose with print output
pytest -v -s
```

---

## Basic Test

```python
"""Basic test example."""

import pytest
from uuid import uuid4

from {context}_api.application.services.user_service import UserService
from {context}_api.application.dtos.user_dtos import CreateUserDTO


class TestUserService:
    """UserService tests."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_http_client):
        """Successful user creation."""
        # Arrange
        mock_http_client.post.return_value = httpx.Response(
            201,
            json={"id": str(uuid4()), "name": "Test", "email": "test@example.com"},
        )
        service = UserService(mock_http_client)
        dto = CreateUserDTO(name="Test", email="test@example.com")

        # Act
        result = await service.create_user(dto)

        # Assert
        assert result.name == "Test"
        assert result.email == "test@example.com"
        mock_http_client.post.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, mock_http_client):
        """User not found."""
        # Arrange
        mock_http_client.get.return_value = httpx.Response(404)
        service = UserService(mock_http_client)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await service.get_user(uuid4())
```

---

## Coverage Configuration

```toml
# pyproject.toml

[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/tests/*",
    "*/__init__.py",
    "*/migrations/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
fail_under = 75
show_missing = true
```

---

## Makefile

```makefile
.PHONY: test test-unit test-integration test-cov

# All tests
test:
	pytest

# Unit tests
test-unit:
	pytest tests/unit -m unit

# Integration tests
test-integration:
	pytest tests/integration -m integration

# With coverage
test-cov:
	pytest --cov=src --cov-report=term --cov-report=html --cov-fail-under=75
```

---

## Checklist

- [ ] pytest.ini or pyproject.toml configured
- [ ] tests/ structure created
- [ ] conftest.py with basic fixtures
- [ ] unit/integration markers defined
- [ ] Coverage configured with 75% threshold
