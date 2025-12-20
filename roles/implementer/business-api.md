# Функция: Stage 4.3 — Business API

> **Назначение**: Создание бизнес-логики и REST API.

---

## Цель

Создать Business API сервис, который содержит бизнес-логику
и предоставляет REST API для внешних клиентов.

---

## Архитектурный принцип

```
ПРАВИЛО: Business API содержит бизнес-логику,
         но НЕ обращается к БД напрямую.

Client ──HTTP──▶ Business API ──HTTP──▶ Data API ──SQL──▶ PostgreSQL

Для доступа к данным Business API использует HTTP клиент
для вызова Data API.
```

---

## Структура Business API

```
services/{context}_api/
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── src/
│   └── {context}_api/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── v1/
│       │   │   ├── __init__.py
│       │   │   ├── router.py
│       │   │   └── {entity}_routes.py
│       │   └── dependencies.py
│       ├── application/
│       │   ├── __init__.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   └── {entity}_service.py
│       │   └── dtos/
│       │       ├── __init__.py
│       │       └── {entity}_dtos.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── entities/
│       │   ├── value_objects/
│       │   └── services/
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   └── http/
│       │       ├── __init__.py
│       │       ├── base_client.py
│       │       └── data_api_client.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── {entity}_schemas.py
│       └── core/
│           ├── __init__.py
│           ├── config.py
│           ├── logging.py
│           └── exceptions.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    │   └── test_{entity}_service.py
    └── integration/
        └── test_{entity}_api.py
```

---

## Компоненты

### 1. main.py

```python
"""Точка входа Business API сервиса."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from {context}_api.api.v1.router import api_router
from {context}_api.core.config import settings
from {context}_api.core.logging import setup_logging
from {context}_api.infrastructure.http.data_api_client import DataApiClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Инициализация
    setup_logging()
    app.state.data_client = DataApiClient(settings.data_api_url)

    yield

    # Очистка
    await app.state.data_client.close()


def create_app() -> FastAPI:
    """Фабрика приложения."""
    app = FastAPI(
        title=f"{settings.service_name} API",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
```

### 2. HTTP Client (infrastructure/http/)

```python
"""HTTP клиент для Data API."""

from typing import Any
from uuid import UUID

import httpx

from {context}_api.core.exceptions import DataApiError


class DataApiClient:
    """Клиент для взаимодействия с Data API."""

    def __init__(self, base_url: str):
        """Инициализация клиента."""
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Получить HTTP клиент."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Закрыть соединение."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Выполнить HTTP запрос."""
        try:
            response = await self.client.request(method, path, **kwargs)
            response.raise_for_status()

            if response.status_code == 204:
                return {}

            return response.json()

        except httpx.HTTPStatusError as e:
            raise DataApiError(
                f"Data API error: {e.response.status_code}",
                status_code=e.response.status_code,
            )
        except httpx.RequestError as e:
            raise DataApiError(f"Data API connection error: {e}")

    # CRUD методы для {Entity}

    async def create_{entity}(self, data: dict) -> dict:
        """Создать {entity}."""
        return await self._request("POST", "/api/v1/{entities}", json=data)

    async def get_{entity}(self, {entity}_id: UUID) -> dict | None:
        """Получить {entity} по ID."""
        try:
            return await self._request("GET", f"/api/v1/{entities}/{{{entity}_id}}")
        except DataApiError as e:
            if e.status_code == 404:
                return None
            raise

    async def list_{entities}(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Получить список {entities}."""
        return await self._request(
            "GET",
            "/api/v1/{entities}",
            params={"page": page, "page_size": page_size},
        )

    async def update_{entity}(self, {entity}_id: UUID, data: dict) -> dict | None:
        """Обновить {entity}."""
        try:
            return await self._request(
                "PUT",
                f"/api/v1/{entities}/{{{entity}_id}}",
                json=data,
            )
        except DataApiError as e:
            if e.status_code == 404:
                return None
            raise

    async def delete_{entity}(self, {entity}_id: UUID) -> bool:
        """Удалить {entity}."""
        try:
            await self._request("DELETE", f"/api/v1/{entities}/{{{entity}_id}}")
            return True
        except DataApiError as e:
            if e.status_code == 404:
                return False
            raise
```

### 3. Application Service (application/services/)

```python
"""Сервис для {Entity}."""

from uuid import UUID

from {context}_api.application.dtos.{entity}_dtos import (
    Create{Entity}DTO,
    Update{Entity}DTO,
    {Entity}DTO,
    {Entity}ListDTO,
)
from {context}_api.core.exceptions import NotFoundError, BusinessRuleError
from {context}_api.infrastructure.http.data_api_client import DataApiClient


class {Entity}Service:
    """Сервис бизнес-логики для {Entity}."""

    def __init__(self, data_client: DataApiClient):
        """Инициализация сервиса."""
        self.data_client = data_client

    async def create_{entity}(self, dto: Create{Entity}DTO) -> {Entity}DTO:
        """
        Создать новый {entity}.

        Бизнес-правила:
        - {Правило 1}
        - {Правило 2}
        """
        # Валидация бизнес-правил
        await self._validate_creation(dto)

        # Создание через Data API
        result = await self.data_client.create_{entity}(dto.model_dump())

        return {Entity}DTO.model_validate(result)

    async def get_{entity}(self, {entity}_id: UUID) -> {Entity}DTO:
        """Получить {entity} по ID."""
        result = await self.data_client.get_{entity}({entity}_id)

        if result is None:
            raise NotFoundError(f"{Entity} with id {{{entity}_id}} not found")

        return {Entity}DTO.model_validate(result)

    async def list_{entities}(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> {Entity}ListDTO:
        """Получить список {entities}."""
        result = await self.data_client.list_{entities}(
            page=page,
            page_size=page_size,
        )

        return {Entity}ListDTO.model_validate(result)

    async def update_{entity}(
        self,
        {entity}_id: UUID,
        dto: Update{Entity}DTO,
    ) -> {Entity}DTO:
        """Обновить {entity}."""
        # Проверка существования
        existing = await self.data_client.get_{entity}({entity}_id)
        if existing is None:
            raise NotFoundError(f"{Entity} with id {{{entity}_id}} not found")

        # Валидация бизнес-правил
        await self._validate_update(existing, dto)

        # Обновление через Data API
        result = await self.data_client.update_{entity}(
            {entity}_id,
            dto.model_dump(exclude_unset=True),
        )

        return {Entity}DTO.model_validate(result)

    async def delete_{entity}(self, {entity}_id: UUID) -> None:
        """Удалить {entity}."""
        deleted = await self.data_client.delete_{entity}({entity}_id)

        if not deleted:
            raise NotFoundError(f"{Entity} with id {{{entity}_id}} not found")

    async def _validate_creation(self, dto: Create{Entity}DTO) -> None:
        """Валидация бизнес-правил при создании."""
        # Реализовать бизнес-правила
        pass

    async def _validate_update(
        self,
        existing: dict,
        dto: Update{Entity}DTO,
    ) -> None:
        """Валидация бизнес-правил при обновлении."""
        # Реализовать бизнес-правила
        pass
```

### 4. API Routes (api/v1/)

```python
"""API роуты для {Entity}."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from {context}_api.api.dependencies import get_{entity}_service
from {context}_api.application.services.{entity}_service import {Entity}Service
from {context}_api.core.exceptions import NotFoundError, BusinessRuleError
from {context}_api.schemas.{entity}_schemas import (
    {Entity}CreateRequest,
    {Entity}UpdateRequest,
    {Entity}Response,
    {Entity}ListResponse,
)

router = APIRouter(prefix="/{entities}", tags=["{Entities}"])


@router.post("", response_model={Entity}Response, status_code=status.HTTP_201_CREATED)
async def create_{entity}(
    request: {Entity}CreateRequest,
    service: {Entity}Service = Depends(get_{entity}_service),
):
    """Создать {entity}."""
    try:
        result = await service.create_{entity}(request.to_dto())
        return {Entity}Response.from_dto(result)
    except BusinessRuleError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.get("", response_model={Entity}ListResponse)
async def list_{entities}(
    page: int = 1,
    page_size: int = 20,
    service: {Entity}Service = Depends(get_{entity}_service),
):
    """Получить список {entities}."""
    result = await service.list_{entities}(page=page, page_size=page_size)
    return {Entity}ListResponse.from_dto(result)


@router.get("/{{{entity}_id}}", response_model={Entity}Response)
async def get_{entity}(
    {entity}_id: UUID,
    service: {Entity}Service = Depends(get_{entity}_service),
):
    """Получить {entity} по ID."""
    try:
        result = await service.get_{entity}({entity}_id)
        return {Entity}Response.from_dto(result)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{Entity} not found",
        )


@router.put("/{{{entity}_id}}", response_model={Entity}Response)
async def update_{entity}(
    {entity}_id: UUID,
    request: {Entity}UpdateRequest,
    service: {Entity}Service = Depends(get_{entity}_service),
):
    """Обновить {entity}."""
    try:
        result = await service.update_{entity}({entity}_id, request.to_dto())
        return {Entity}Response.from_dto(result)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{Entity} not found",
        )
    except BusinessRuleError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.delete("/{{{entity}_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{entity}(
    {entity}_id: UUID,
    service: {Entity}Service = Depends(get_{entity}_service),
):
    """Удалить {entity}."""
    try:
        await service.delete_{entity}({entity}_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{Entity} not found",
        )
```

---

## Шаблон для использования

```
templates/services/fastapi_business_api/
```

---

## Порядок создания

```
1. Создать структуру директорий
2. Создать Dockerfile
3. Создать requirements.txt
4. Создать core/config.py, logging.py, exceptions.py
5. Создать infrastructure/http/base_client.py
6. Создать infrastructure/http/data_api_client.py
7. Создать application/dtos/{entity}_dtos.py
8. Создать application/services/{entity}_service.py
9. Создать schemas/{entity}_schemas.py
10. Создать api/dependencies.py
11. Создать api/v1/{entity}_routes.py
12. Создать api/v1/router.py
13. Создать main.py
```

---

## Качественные ворота

### BUSINESS_API_READY

- [ ] Структура проекта создана по шаблону
- [ ] HTTP клиент для Data API создан
- [ ] Application services созданы
- [ ] API эндпоинты созданы
- [ ] Dockerfile создан
- [ ] `docker-compose up {context}-api` запускается
- [ ] Health check проходит: `GET /api/v1/health`
- [ ] Все FR из PRD покрыты эндпоинтами

---

## Источники

| Документ | Описание |
|----------|----------|
| `knowledge/services/fastapi/application-factory.md` | Фабрика приложения |
| `knowledge/services/fastapi/routing-patterns.md` | Паттерны роутинга |
| `knowledge/integrations/http/client-patterns.md` | HTTP клиенты |
| `templates/services/fastapi_business_api/` | Шаблон сервиса |
