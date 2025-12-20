# Настройка pytest

> **Назначение**: Базовая настройка pytest для проекта.

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

## Структура тестов

```
tests/
├── __init__.py
├── conftest.py              # Общие фикстуры
├── unit/                    # Unit тесты
│   ├── __init__.py
│   ├── conftest.py         # Фикстуры для unit
│   ├── test_user_service.py
│   └── test_order_service.py
├── integration/            # Integration тесты
│   ├── __init__.py
│   ├── conftest.py         # Фикстуры для integration
│   ├── test_user_api.py
│   └── test_order_api.py
└── e2e/                    # E2E тесты (опционально)
    ├── __init__.py
    └── test_user_flow.py
```

---

## conftest.py

```python
"""Общие фикстуры."""

import pytest
from unittest.mock import AsyncMock

import httpx
from fastapi.testclient import TestClient
from httpx import AsyncClient

from {context}_api.main import app


@pytest.fixture
def client() -> TestClient:
    """Синхронный тест-клиент."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncClient:
    """Асинхронный тест-клиент."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_http_client() -> AsyncMock:
    """Мок HTTP клиента."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def anyio_backend() -> str:
    """Бэкенд для anyio."""
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

## Команды запуска

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=src --cov-report=term --cov-report=html

# Проверка порога покрытия
pytest --cov=src --cov-fail-under=75

# Только unit тесты
pytest tests/unit -m unit

# Только integration тесты
pytest tests/integration -m integration

# Параллельный запуск
pytest -n auto

# Конкретный файл
pytest tests/unit/test_user_service.py

# Конкретный тест
pytest tests/unit/test_user_service.py::TestUserService::test_create_user

# Verbose с выводом print
pytest -v -s
```

---

## Базовый тест

```python
"""Пример базового теста."""

import pytest
from uuid import uuid4

from {context}_api.application.services.user_service import UserService
from {context}_api.application.dtos.user_dtos import CreateUserDTO


class TestUserService:
    """Тесты UserService."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_http_client):
        """Успешное создание пользователя."""
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
        """Пользователь не найден."""
        # Arrange
        mock_http_client.get.return_value = httpx.Response(404)
        service = UserService(mock_http_client)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await service.get_user(uuid4())
```

---

## Coverage конфигурация

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

# Все тесты
test:
	pytest

# Unit тесты
test-unit:
	pytest tests/unit -m unit

# Integration тесты
test-integration:
	pytest tests/integration -m integration

# С покрытием
test-cov:
	pytest --cov=src --cov-report=term --cov-report=html --cov-fail-under=75
```

---

## Чек-лист

- [ ] pytest.ini или pyproject.toml настроен
- [ ] Структура tests/ создана
- [ ] conftest.py с базовыми фикстурами
- [ ] Маркеры unit/integration определены
- [ ] Coverage настроен с порогом 75%
