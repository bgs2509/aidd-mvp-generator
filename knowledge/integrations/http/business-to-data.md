# HTTP вызовы Business → Data API

> **Назначение**: Паттерны взаимодействия Business API с Data API.

---

## Принцип HTTP-only

```
┌─────────────────┐    HTTP     ┌─────────────────┐    SQL     ┌──────────────┐
│  Business API   │────────────▶│    Data API     │───────────▶│  PostgreSQL  │
│  (бизнес-логика)│◀────────────│ (доступ к данным)│◀───────────│   (БД)       │
└─────────────────┘             └─────────────────┘            └──────────────┘

❌ Business API НИКОГДА не обращается к БД напрямую
✓ Все операции с данными через HTTP к Data API
```

---

## HTTP клиент

```python
"""HTTP клиент для Data API."""

from typing import Any
from uuid import UUID

import httpx

from {context}_api.core.config import settings


class DataApiClient:
    """Клиент для взаимодействия с Data API."""

    def __init__(self, client: httpx.AsyncClient):
        """
        Инициализация клиента.

        Args:
            client: Экземпляр httpx.AsyncClient.
        """
        self.client = client
        self.base_url = settings.data_api_url

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        """
        Выполнить HTTP запрос.

        Args:
            method: HTTP метод.
            path: Путь API.
            **kwargs: Дополнительные параметры.

        Returns:
            Ответ API.

        Raises:
            DataApiError: При ошибке API.
        """
        url = f"{self.base_url}{path}"

        response = await self.client.request(method, url, **kwargs)

        if response.status_code == 204:
            return None

        if response.status_code >= 400:
            raise DataApiError(
                message=response.text,
                status_code=response.status_code,
            )

        return response.json()

    # === Users ===

    async def get_user(self, user_id: UUID) -> dict | None:
        """
        Получить пользователя.

        Args:
            user_id: ID пользователя.

        Returns:
            Данные пользователя или None.
        """
        try:
            return await self._request("GET", f"/api/v1/users/{user_id}")
        except DataApiError as e:
            if e.status_code == 404:
                return None
            raise

    async def create_user(self, data: dict) -> dict:
        """
        Создать пользователя.

        Args:
            data: Данные пользователя.

        Returns:
            Созданный пользователь.
        """
        return await self._request("POST", "/api/v1/users", json=data)

    async def update_user(self, user_id: UUID, data: dict) -> dict:
        """
        Обновить пользователя.

        Args:
            user_id: ID пользователя.
            data: Данные для обновления.

        Returns:
            Обновлённый пользователь.
        """
        return await self._request("PUT", f"/api/v1/users/{user_id}", json=data)

    async def delete_user(self, user_id: UUID) -> None:
        """
        Удалить пользователя.

        Args:
            user_id: ID пользователя.
        """
        await self._request("DELETE", f"/api/v1/users/{user_id}")

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        Получить список пользователей.

        Args:
            page: Номер страницы.
            page_size: Размер страницы.

        Returns:
            Список пользователей с метаданными пагинации.
        """
        return await self._request(
            "GET",
            "/api/v1/users",
            params={"page": page, "page_size": page_size},
        )

    async def get_user_by_email(self, email: str) -> dict | None:
        """
        Получить пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            Данные пользователя или None.
        """
        try:
            return await self._request(
                "GET",
                "/api/v1/users/by-email",
                params={"email": email},
            )
        except DataApiError as e:
            if e.status_code == 404:
                return None
            raise

    # === Orders ===

    async def get_order(self, order_id: UUID) -> dict | None:
        """Получить заказ."""
        try:
            return await self._request("GET", f"/api/v1/orders/{order_id}")
        except DataApiError as e:
            if e.status_code == 404:
                return None
            raise

    async def create_order(self, data: dict) -> dict:
        """Создать заказ."""
        return await self._request("POST", "/api/v1/orders", json=data)

    async def get_user_orders(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Получить заказы пользователя."""
        return await self._request(
            "GET",
            f"/api/v1/users/{user_id}/orders",
            params={"page": page, "page_size": page_size},
        )
```

---

## Использование в сервисе

```python
"""Application Service с HTTP клиентом."""

from uuid import UUID

from {context}_api.application.dtos.user_dtos import CreateUserDTO, UserDTO
from {context}_api.core.exceptions import NotFoundError, ValidationError
from {context}_api.infrastructure.http.data_api_client import DataApiClient


class UserService:
    """Сервис пользователей."""

    def __init__(self, data_client: DataApiClient):
        """
        Инициализация сервиса.

        Args:
            data_client: HTTP клиент для Data API.
        """
        self.data_client = data_client

    async def create_user(self, dto: CreateUserDTO) -> UserDTO:
        """
        Создать пользователя.

        Args:
            dto: Данные для создания.

        Returns:
            Созданный пользователь.

        Raises:
            ValidationError: Если email уже существует.
        """
        # Проверка уникальности (бизнес-логика)
        existing = await self.data_client.get_user_by_email(dto.email)
        if existing:
            raise ValidationError(
                message=f"Email {dto.email} already exists",
                field="email",
            )

        # Создание через Data API
        result = await self.data_client.create_user(dto.model_dump())
        return UserDTO.model_validate(result)

    async def get_user(self, user_id: UUID) -> UserDTO:
        """
        Получить пользователя.

        Args:
            user_id: ID пользователя.

        Returns:
            Данные пользователя.

        Raises:
            NotFoundError: Если не найден.
        """
        result = await self.data_client.get_user(user_id)
        if result is None:
            raise NotFoundError("User", str(user_id))
        return UserDTO.model_validate(result)
```

---

## Настройка в lifespan

```python
"""Управление HTTP клиентом в lifespan."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx

from {context}_api.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения."""
    # Создание HTTP клиента
    app.state.http_client = httpx.AsyncClient(
        base_url=settings.data_api_url,
        timeout=httpx.Timeout(30.0),
        headers={"Content-Type": "application/json"},
    )

    yield

    # Закрытие клиента
    await app.state.http_client.aclose()
```

---

## Передача Request ID

```python
"""Передача request_id между сервисами."""

from fastapi import Request


class DataApiClient:
    """Клиент с передачей request_id."""

    def __init__(self, client: httpx.AsyncClient, request_id: str | None = None):
        """Инициализация."""
        self.client = client
        self.request_id = request_id

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Выполнить запрос с request_id."""
        headers = kwargs.pop("headers", {})

        if self.request_id:
            headers["X-Request-ID"] = self.request_id

        return await self.client.request(
            method,
            path,
            headers=headers,
            **kwargs,
        )


# В dependencies.py
def get_data_client(request: Request) -> DataApiClient:
    """Создать клиент с request_id."""
    request_id = getattr(request.state, "request_id", None)
    return DataApiClient(
        request.app.state.http_client,
        request_id=request_id,
    )
```

---

## Чек-лист

- [ ] Business API не имеет доступа к БД
- [ ] Все данные получаются через Data API
- [ ] HTTP клиент создаётся в lifespan
- [ ] Request ID передаётся между сервисами
- [ ] Ошибки Data API обрабатываются
