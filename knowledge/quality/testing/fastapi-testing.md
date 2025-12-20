# Тестирование FastAPI

> **Назначение**: Паттерны тестирования FastAPI приложений.

---

## Тест-клиент

```python
"""Настройка тест-клиента."""

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
    """Асинхронный тест-клиент."""
    async with AsyncClient(
        app=app,
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client
```

---

## Тестирование эндпоинтов

```python
"""Тесты API эндпоинтов."""

import pytest
from uuid import uuid4


class TestUserAPI:
    """Тесты API пользователей."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, client):
        """Успешное создание пользователя."""
        response = await client.post(
            "/api/v1/users",
            json={
                "name": "Test User",
                "email": "test@example.com",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test User"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_user_validation_error(self, client):
        """Ошибка валидации при создании."""
        response = await client.post(
            "/api/v1/users",
            json={
                "name": "",  # Пустое имя
                "email": "invalid-email",  # Невалидный email
            },
        )

        assert response.status_code == 422
        errors = response.json()["errors"]
        assert len(errors) >= 1

    @pytest.mark.asyncio
    async def test_get_user_success(self, client, created_user):
        """Успешное получение пользователя."""
        response = await client.get(f"/api/v1/users/{created_user['id']}")

        assert response.status_code == 200
        assert response.json()["id"] == created_user["id"]

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client):
        """Пользователь не найден."""
        response = await client.get(f"/api/v1/users/{uuid4()}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_users_pagination(self, client):
        """Пагинация списка пользователей."""
        response = await client.get(
            "/api/v1/users",
            params={"page": 1, "page_size": 10},
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data

    @pytest.mark.asyncio
    async def test_update_user_success(self, client, created_user):
        """Успешное обновление пользователя."""
        response = await client.put(
            f"/api/v1/users/{created_user['id']}",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete_user_success(self, client, created_user):
        """Успешное удаление пользователя."""
        response = await client.delete(f"/api/v1/users/{created_user['id']}")

        assert response.status_code == 204
```

---

## Тестирование с моками

```python
"""Тесты с моками зависимостей."""

import pytest
from unittest.mock import AsyncMock
from fastapi import FastAPI

from {context}_api.main import app
from {context}_api.api.dependencies import get_user_service
from {context}_api.application.services.user_service import UserService


@pytest.fixture
def mock_user_service() -> AsyncMock:
    """Мок UserService."""
    mock = AsyncMock(spec=UserService)
    return mock


@pytest.fixture
def app_with_mock_service(mock_user_service) -> FastAPI:
    """Приложение с мок сервисом."""
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
async def client_with_mocks(app_with_mock_service) -> AsyncClient:
    """Клиент с моками."""
    async with AsyncClient(app=app_with_mock_service, base_url="http://test") as client:
        yield client


class TestUserAPIWithMocks:
    """Тесты с моками."""

    @pytest.mark.asyncio
    async def test_get_user_calls_service(
        self,
        client_with_mocks,
        mock_user_service,
    ):
        """Проверка вызова сервиса."""
        user_id = "123"
        mock_user_service.get_user.return_value = UserDTO(
            id=user_id,
            name="Test",
            email="test@example.com",
        )

        response = await client_with_mocks.get(f"/api/v1/users/{user_id}")

        assert response.status_code == 200
        mock_user_service.get_user.assert_called_once()
```

---

## Тестирование аутентификации

```python
"""Тесты аутентификации."""

import pytest


@pytest.fixture
def auth_headers() -> dict:
    """Заголовки аутентификации."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
async def authenticated_client(client, auth_headers) -> AsyncClient:
    """Клиент с аутентификацией."""
    client.headers.update(auth_headers)
    return client


class TestAuthenticatedAPI:
    """Тесты защищённых эндпоинтов."""

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_auth(self, client):
        """Доступ без аутентификации запрещён."""
        response = await client.get("/api/v1/protected")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_auth(self, authenticated_client):
        """Доступ с аутентификацией разрешён."""
        response = await authenticated_client.get("/api/v1/protected")
        assert response.status_code == 200
```

---

## Тестирование ошибок

```python
"""Тесты обработки ошибок."""

import pytest
from unittest.mock import AsyncMock


class TestErrorHandling:
    """Тесты обработки ошибок."""

    @pytest.mark.asyncio
    async def test_internal_error_returns_500(
        self,
        client_with_mocks,
        mock_user_service,
    ):
        """Внутренняя ошибка возвращает 500."""
        mock_user_service.get_user.side_effect = Exception("Internal error")

        response = await client_with_mocks.get("/api/v1/users/123")

        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_validation_error_format(self, client):
        """Формат ошибки валидации."""
        response = await client.post(
            "/api/v1/users",
            json={"invalid": "data"},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "errors" in data
```

---

## Тестирование загрузки файлов

```python
"""Тесты загрузки файлов."""

import pytest
from io import BytesIO


class TestFileUpload:
    """Тесты загрузки файлов."""

    @pytest.mark.asyncio
    async def test_upload_image(self, client):
        """Загрузка изображения."""
        file_content = b"fake image content"
        files = {"file": ("image.png", BytesIO(file_content), "image/png")}

        response = await client.post("/api/v1/upload", files=files)

        assert response.status_code == 200
        assert "url" in response.json()
```

---

## Чек-лист

- [ ] AsyncClient для async тестов
- [ ] dependency_overrides для моков
- [ ] Тесты успешных сценариев
- [ ] Тесты ошибок (4xx, 5xx)
- [ ] Тесты валидации
- [ ] Тесты аутентификации
