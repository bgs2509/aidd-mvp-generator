# Функция: Stage 4.2 — Data Service

> **Назначение**: Создание сервиса доступа к данным (Data API).

---

## Цель

Создать Data API сервис, который предоставляет HTTP интерфейс
к базе данных PostgreSQL для других сервисов.

---

## Архитектурный принцип

```
ПРАВИЛО: Data API — единственная точка доступа к базе данных.

Business API ──HTTP──▶ Data API ──SQL──▶ PostgreSQL

Бизнес-сервисы НИКОГДА не подключаются к БД напрямую.
Они всегда работают через HTTP вызовы к Data API.
```

---

## Структура Data Service

```
services/{context}_data/
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── alembic.ini
├── migrations/
│   └── versions/
├── src/
│   └── {context}_data/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── v1/
│       │   │   ├── __init__.py
│       │   │   ├── router.py
│       │   │   └── {entity}_routes.py
│       │   └── dependencies.py
│       ├── domain/
│       │   ├── __init__.py
│       │   └── entities/
│       │       ├── __init__.py
│       │       ├── base.py
│       │       └── {entity}.py
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── database/
│       │   │   ├── __init__.py
│       │   │   ├── connection.py
│       │   │   └── session.py
│       │   └── repositories/
│       │       ├── __init__.py
│       │       ├── base.py
│       │       └── {entity}_repository.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── {entity}_schemas.py
│       └── core/
│           ├── __init__.py
│           ├── config.py
│           └── logging.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    │   └── test_{entity}_repository.py
    └── integration/
        └── test_{entity}_api.py
```

---

## Компоненты

### 1. main.py

```python
"""Точка входа Data API сервиса."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from {context}_data.api.v1.router import api_router
from {context}_data.core.config import settings
from {context}_data.core.logging import setup_logging
from {context}_data.infrastructure.database.connection import (
    create_db_engine,
    dispose_engine,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Инициализация
    setup_logging()
    engine = create_db_engine()
    app.state.engine = engine

    yield

    # Очистка
    await dispose_engine(engine)


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

### 2. Entity (domain/entities/)

```python
"""Сущность {Entity}."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from {context}_data.domain.entities.base import Base


class {Entity}(Base):
    """Модель {Entity} в базе данных."""

    __tablename__ = "{entities}"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # ... другие поля ...
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
```

### 3. Repository (infrastructure/repositories/)

```python
"""Репозиторий для {Entity}."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from {context}_data.domain.entities.{entity} import {Entity}
from {context}_data.infrastructure.repositories.base import BaseRepository


class {Entity}Repository(BaseRepository[{Entity}]):
    """Репозиторий для работы с {Entity}."""

    def __init__(self, session: AsyncSession):
        """Инициализация репозитория."""
        super().__init__({Entity}, session)

    async def get_by_name(self, name: str) -> {Entity} | None:
        """Получить {entity} по имени."""
        query = select({Entity}).where({Entity}.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
```

### 4. Base Repository

```python
"""Базовый репозиторий."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from {context}_data.domain.entities.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий с CRUD операциями."""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        """Инициализация репозитория."""
        self.model = model
        self.session = session

    async def get_by_id(self, id: UUID) -> ModelType | None:
        """Получить запись по ID."""
        return await self.session.get(self.model, id)

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Получить все записи с пагинацией."""
        query = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self) -> int:
        """Получить количество записей."""
        query = select(func.count()).select_from(self.model)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def create(self, **kwargs) -> ModelType:
        """Создать новую запись."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: UUID, **kwargs) -> ModelType | None:
        """Обновить запись."""
        instance = await self.get_by_id(id)
        if instance is None:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: UUID) -> bool:
        """Удалить запись."""
        instance = await self.get_by_id(id)
        if instance is None:
            return False

        await self.session.delete(instance)
        await self.session.commit()
        return True
```

### 5. API Routes (api/v1/)

```python
"""API роуты для {Entity}."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from {context}_data.api.dependencies import get_session
from {context}_data.infrastructure.repositories.{entity}_repository import (
    {Entity}Repository,
)
from {context}_data.schemas.{entity}_schemas import (
    {Entity}Create,
    {Entity}Response,
    {Entity}Update,
    {Entity}ListResponse,
)

router = APIRouter(prefix="/{entities}", tags=["{Entities}"])


@router.post("", response_model={Entity}Response, status_code=status.HTTP_201_CREATED)
async def create_{entity}(
    data: {Entity}Create,
    session=Depends(get_session),
):
    """Создать {entity}."""
    repo = {Entity}Repository(session)
    {entity} = await repo.create(**data.model_dump())
    return {entity}


@router.get("", response_model={Entity}ListResponse)
async def list_{entities}(
    page: int = 1,
    page_size: int = 20,
    session=Depends(get_session),
):
    """Получить список {entities}."""
    repo = {Entity}Repository(session)
    offset = (page - 1) * page_size

    items = await repo.get_all(offset=offset, limit=page_size)
    total = await repo.count()
    pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.get("/{{{entity}_id}}", response_model={Entity}Response)
async def get_{entity}(
    {entity}_id: UUID,
    session=Depends(get_session),
):
    """Получить {entity} по ID."""
    repo = {Entity}Repository(session)
    {entity} = await repo.get_by_id({entity}_id)

    if {entity} is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{Entity} not found",
        )

    return {entity}


@router.put("/{{{entity}_id}}", response_model={Entity}Response)
async def update_{entity}(
    {entity}_id: UUID,
    data: {Entity}Update,
    session=Depends(get_session),
):
    """Обновить {entity}."""
    repo = {Entity}Repository(session)
    {entity} = await repo.update({entity}_id, **data.model_dump(exclude_unset=True))

    if {entity} is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{Entity} not found",
        )

    return {entity}


@router.delete("/{{{entity}_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{entity}(
    {entity}_id: UUID,
    session=Depends(get_session),
):
    """Удалить {entity}."""
    repo = {Entity}Repository(session)
    deleted = await repo.delete({entity}_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{Entity} not found",
        )
```

---

## Шаблон для использования

```
templates/services/postgres_data_api/
```

---

## Порядок создания

```
1. Создать структуру директорий
2. Создать Dockerfile
3. Создать requirements.txt
4. Создать core/config.py
5. Создать domain/entities/base.py
6. Создать domain/entities/{entity}.py
7. Создать infrastructure/database/
8. Создать infrastructure/repositories/base.py
9. Создать infrastructure/repositories/{entity}_repository.py
10. Создать schemas/{entity}_schemas.py
11. Создать api/v1/{entity}_routes.py
12. Создать api/v1/router.py
13. Создать main.py
14. Настроить Alembic для миграций
```

---

## Качественные ворота

### DATA_SERVICE_READY

- [ ] Структура проекта создана по шаблону
- [ ] Все модели созданы
- [ ] Все репозитории созданы
- [ ] API эндпоинты созданы
- [ ] Миграции настроены
- [ ] Dockerfile создан
- [ ] `docker-compose up {context}-data` запускается
- [ ] Health check проходит: `GET /api/v1/health`

---

## Источники

| Документ | Описание |
|----------|----------|
| `knowledge/services/data-services/postgres-setup.md` | Настройка PostgreSQL |
| `knowledge/services/data-services/repository-patterns.md` | Паттерны репозиториев |
| `templates/services/postgres_data_api/` | Шаблон сервиса |
