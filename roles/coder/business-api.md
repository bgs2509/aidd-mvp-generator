# Function: Stage 4.3 — Business API

> **Purpose**: Creating business logic and REST API.

---

## Goal

Create a Business API service that contains business logic
and provides a REST API for external clients.

---

## Architectural Principle

```
RULE: Business API contains business logic,
      but NEVER accesses the database directly.

Client ──HTTP──▶ Business API ──HTTP──▶ Data API ──SQL──▶ PostgreSQL

To access data, Business API uses an HTTP client
to call the Data API.
```

---

## Business API Structure

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

## Components

### 1. main.py

```python
"""Business API service entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from {context}_api.api.v1.router import api_router
from {context}_api.core.config import settings
from {context}_api.core.logging import setup_logging
from {context}_api.infrastructure.http.data_api_client import DataApiClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Initialization
    setup_logging()
    app.state.data_client = DataApiClient(settings.data_api_url)

    yield

    # Cleanup
    await app.state.data_client.close()


def create_app() -> FastAPI:
    """Application factory."""
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
"""HTTP client for Data API."""

from typing import Any
from uuid import UUID

import httpx

from {context}_api.core.exceptions import DataApiError


class DataApiClient:
    """Client for interacting with the Data API."""

    def __init__(self, base_url: str):
        """Initialize the client."""
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Close the connection."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Execute an HTTP request."""
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

    # CRUD methods for {Entity}

    async def create_{entity}(self, data: dict) -> dict:
        """Create {entity}."""
        return await self._request("POST", "/api/v1/{entities}", json=data)

    async def get_{entity}(self, {entity}_id: UUID) -> dict | None:
        """Get {entity} by ID."""
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
        """Get list of {entities}."""
        return await self._request(
            "GET",
            "/api/v1/{entities}",
            params={"page": page, "page_size": page_size},
        )

    async def update_{entity}(self, {entity}_id: UUID, data: dict) -> dict | None:
        """Update {entity}."""
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
        """Delete {entity}."""
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
"""Service for {Entity}."""

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
    """Business logic service for {Entity}."""

    def __init__(self, data_client: DataApiClient):
        """Initialize the service."""
        self.data_client = data_client

    async def create_{entity}(self, dto: Create{Entity}DTO) -> {Entity}DTO:
        """
        Create a new {entity}.

        Business rules:
        - {Rule 1}
        - {Rule 2}
        """
        # Validate business rules
        await self._validate_creation(dto)

        # Create via Data API
        result = await self.data_client.create_{entity}(dto.model_dump())

        return {Entity}DTO.model_validate(result)

    async def get_{entity}(self, {entity}_id: UUID) -> {Entity}DTO:
        """Get {entity} by ID."""
        result = await self.data_client.get_{entity}({entity}_id)

        if result is None:
            raise NotFoundError(f"{Entity} with id {{{entity}_id}} not found")

        return {Entity}DTO.model_validate(result)

    async def list_{entities}(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> {Entity}ListDTO:
        """Get list of {entities}."""
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
        """Update {entity}."""
        # Check existence
        existing = await self.data_client.get_{entity}({entity}_id)
        if existing is None:
            raise NotFoundError(f"{Entity} with id {{{entity}_id}} not found")

        # Validate business rules
        await self._validate_update(existing, dto)

        # Update via Data API
        result = await self.data_client.update_{entity}(
            {entity}_id,
            dto.model_dump(exclude_unset=True),
        )

        return {Entity}DTO.model_validate(result)

    async def delete_{entity}(self, {entity}_id: UUID) -> None:
        """Delete {entity}."""
        deleted = await self.data_client.delete_{entity}({entity}_id)

        if not deleted:
            raise NotFoundError(f"{Entity} with id {{{entity}_id}} not found")

    async def _validate_creation(self, dto: Create{Entity}DTO) -> None:
        """Validate business rules on creation."""
        # Implement business rules
        pass

    async def _validate_update(
        self,
        existing: dict,
        dto: Update{Entity}DTO,
    ) -> None:
        """Validate business rules on update."""
        # Implement business rules
        pass
```

### 4. API Routes (api/v1/)

```python
"""API routes for {Entity}."""

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
    """Create {entity}."""
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
    """Get list of {entities}."""
    result = await service.list_{entities}(page=page, page_size=page_size)
    return {Entity}ListResponse.from_dto(result)


@router.get("/{{{entity}_id}}", response_model={Entity}Response)
async def get_{entity}(
    {entity}_id: UUID,
    service: {Entity}Service = Depends(get_{entity}_service),
):
    """Get {entity} by ID."""
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
    """Update {entity}."""
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
    """Delete {entity}."""
    try:
        await service.delete_{entity}({entity}_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{Entity} not found",
        )
```

---

## Template to Use

```
templates/services/fastapi_business_api/
```

---

## Creation Order

```
1. Create directory structure
2. Create Dockerfile
3. Create requirements.txt
4. Create core/config.py, logging.py, exceptions.py
5. Create infrastructure/http/base_client.py
6. Create infrastructure/http/data_api_client.py
7. Create application/dtos/{entity}_dtos.py
8. Create application/services/{entity}_service.py
9. Create schemas/{entity}_schemas.py
10. Create api/dependencies.py
11. Create api/v1/{entity}_routes.py
12. Create api/v1/router.py
13. Create main.py
```

---

## Quality Gates

### BUSINESS_API_READY

- [ ] Project structure created from template
- [ ] HTTP client for Data API created
- [ ] Application services created
- [ ] API endpoints created
- [ ] Dockerfile created
- [ ] `docker-compose up {context}-api` starts successfully
- [ ] Health check passes: `GET /api/v1/health`
- [ ] All FRs from PRD are covered by endpoints

---

## References

| Document | Description |
|----------|-------------|
| `knowledge/services/fastapi/application-factory.md` | Application factory |
| `knowledge/services/fastapi/routing-patterns.md` | Routing patterns |
| `knowledge/integrations/http/client-patterns.md` | HTTP clients |
| `templates/services/fastapi_business_api/` | Service template |
