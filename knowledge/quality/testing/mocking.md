# Стратегии мокирования

> **Назначение**: Паттерны мокирования для изолированных тестов.

---

## AsyncMock

```python
"""Мокирование асинхронных функций."""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_service() -> AsyncMock:
    """Мок асинхронного сервиса."""
    mock = AsyncMock()

    # Настройка возвращаемых значений
    mock.get_user.return_value = {"id": "123", "name": "Test"}
    mock.create_user.return_value = {"id": "456", "name": "New"}

    # Настройка side_effect
    mock.delete_user.side_effect = None  # Возвращает None

    return mock


@pytest.mark.asyncio
async def test_with_async_mock(mock_service):
    """Тест с async mock."""
    result = await mock_service.get_user("123")

    assert result["name"] == "Test"
    mock_service.get_user.assert_called_once_with("123")
```

---

## Мокирование HTTP клиента

```python
"""Мокирование httpx."""

import pytest
from unittest.mock import AsyncMock
import httpx


@pytest.fixture
def mock_http_client() -> AsyncMock:
    """Мок httpx.AsyncClient."""
    mock = AsyncMock(spec=httpx.AsyncClient)

    # Успешный GET
    mock.get.return_value = httpx.Response(
        200,
        json={"id": "123", "name": "Test"},
    )

    # Успешный POST
    mock.post.return_value = httpx.Response(
        201,
        json={"id": "456", "name": "Created"},
    )

    # 404 для определённого вызова
    async def get_side_effect(url, **kwargs):
        if "nonexistent" in url:
            return httpx.Response(404, json={"detail": "Not found"})
        return httpx.Response(200, json={"id": "123"})

    mock.get.side_effect = get_side_effect

    return mock


@pytest.mark.asyncio
async def test_http_client_mock(mock_http_client):
    """Тест с мок HTTP клиентом."""
    # Успешный запрос
    response = await mock_http_client.get("/api/v1/users/123")
    assert response.status_code == 200

    # 404
    response = await mock_http_client.get("/api/v1/users/nonexistent")
    assert response.status_code == 404
```

---

## respx для HTTP мокирования

```python
"""Мокирование с respx."""

import pytest
import respx
import httpx


@pytest.fixture
def mock_data_api():
    """Мок Data API с respx."""
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
    """Тест с respx."""
    async with httpx.AsyncClient(base_url="http://data-api:8001") as client:
        response = await client.get("/api/v1/users/123")
        assert response.json()["name"] == "Test"

        response = await client.get("/api/v1/users/999")
        assert response.status_code == 404
```

---

## Мокирование зависимостей FastAPI

```python
"""Мокирование DI в FastAPI."""

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from unittest.mock import AsyncMock

from {context}_api.main import app
from {context}_api.api.dependencies import get_user_service


@pytest.fixture
def mock_user_service() -> AsyncMock:
    """Мок UserService."""
    mock = AsyncMock()
    mock.get_user.return_value = UserDTO(
        id="123",
        name="Test",
        email="test@example.com",
    )
    return mock


@pytest.fixture
def app_with_mocks(mock_user_service) -> FastAPI:
    """Приложение с подменёнными зависимостями."""
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    yield app
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_with_dependency_mock(app_with_mocks):
    """Тест с подменой зависимости."""
    async with AsyncClient(app=app_with_mocks, base_url="http://test") as client:
        response = await client.get("/api/v1/users/123")
        assert response.status_code == 200
        assert response.json()["name"] == "Test"
```

---

## patch и monkeypatch

```python
"""Использование patch и monkeypatch."""

import pytest
from unittest.mock import patch, AsyncMock


# unittest.mock.patch
@pytest.mark.asyncio
async def test_with_patch():
    """Тест с patch."""
    with patch(
        "{context}_api.infrastructure.http.data_api_client.DataApiClient.get_user",
        new_callable=AsyncMock,
        return_value={"id": "123", "name": "Test"},
    ):
        # Код, использующий DataApiClient.get_user
        pass


# pytest monkeypatch
def test_with_monkeypatch(monkeypatch):
    """Тест с monkeypatch."""
    # Переменные окружения
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("DATA_API_URL", "http://mock:8001")

    # Атрибуты модуля
    monkeypatch.setattr("module.attribute", "new_value")

    # Удаление атрибута
    monkeypatch.delattr("module.attribute", raising=False)
```

---

## Мокирование времени

```python
"""Мокирование datetime."""

import pytest
from datetime import datetime
from unittest.mock import patch
from freezegun import freeze_time


# С freezegun
@freeze_time("2024-01-15 12:00:00")
def test_with_frozen_time():
    """Тест с замороженным временем."""
    assert datetime.now() == datetime(2024, 1, 15, 12, 0, 0)


# С patch
def test_with_patched_time():
    """Тест с подменой времени."""
    fixed_time = datetime(2024, 1, 15, 12, 0, 0)

    with patch("module.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = fixed_time
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # Тест
        pass
```

---

## Проверка вызовов

```python
"""Проверка вызовов моков."""

import pytest
from unittest.mock import AsyncMock, call


@pytest.mark.asyncio
async def test_mock_calls():
    """Проверка вызовов."""
    mock = AsyncMock()

    await mock.method("arg1", key="value")
    await mock.method("arg2")

    # Проверка количества вызовов
    assert mock.method.call_count == 2

    # Проверка конкретного вызова
    mock.method.assert_called_with("arg2")
    mock.method.assert_any_call("arg1", key="value")

    # Проверка всех вызовов
    mock.method.assert_has_calls([
        call("arg1", key="value"),
        call("arg2"),
    ])

    # Проверка что вызван хотя бы раз
    mock.method.assert_called()

    # Проверка что не вызван
    mock.other_method.assert_not_called()
```

---

## Чек-лист

- [ ] AsyncMock для async функций
- [ ] respx для HTTP клиентов
- [ ] dependency_overrides для FastAPI
- [ ] monkeypatch для env
- [ ] freezegun для времени
- [ ] assert_called для проверки вызовов
