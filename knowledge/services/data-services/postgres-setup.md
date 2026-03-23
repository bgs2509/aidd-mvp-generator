# PostgreSQL Data Service Setup

> **Purpose**: Setting up Data API with PostgreSQL and SQLAlchemy.

---

## Entry Point

```python
"""Data API entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from {context}_data.api.v1.router import api_router
from {context}_data.core.config import settings
from {context}_data.core.logging import setup_logging
from {context}_data.infrastructure.database.connection import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    setup_logging()
    yield
    # Close database connections
    await engine.dispose()


def create_app() -> FastAPI:
    """Create Data API application."""
    app = FastAPI(
        title=settings.service_name,
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
```

---

## Configuration

```python
"""Data API configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Data API settings."""

    service_name: str = "{Context} Data API"
    debug: bool = False
    log_level: str = "INFO"

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/db"

    # Pool
    db_pool_size: int = 5
    db_max_overflow: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
```

---

## Database Connection

```python
"""PostgreSQL connection."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from {context}_data.core.config import settings


# Create engine
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    echo=settings.debug,
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """
    Get a database session.

    Yields:
        Async SQLAlchemy session.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

---

## Base Model

```python
"""SQLAlchemy base model."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class TimestampMixin:
    """Mixin with timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )


class UUIDMixin:
    """Mixin with UUID primary key."""

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
```

---

## Entity Model

```python
"""User model."""

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from {context}_data.domain.entities.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User database model."""

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        """String representation."""
        return f"<User(id={self.id}, email={self.email})>"
```

---

## Project Structure

```
{context}_data/
├── __init__.py
├── main.py
│
├── api/
│   ├── __init__.py
│   ├── dependencies.py
│   └── v1/
│       ├── __init__.py
│       ├── router.py
│       └── user_routes.py
│
├── domain/
│   ├── __init__.py
│   └── entities/
│       ├── __init__.py
│       ├── base.py
│       └── user.py
│
├── infrastructure/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── session.py
│   └── repositories/
│       ├── __init__.py
│       ├── base.py
│       └── user_repository.py
│
├── schemas/
│   ├── __init__.py
│   ├── base.py
│   └── user_schemas.py
│
└── core/
    ├── __init__.py
    ├── config.py
    └── logging.py

migrations/
├── env.py
├── script.py.mako
└── versions/
    └── 001_initial.py
```

---

## Alembic Setup

```python
"""migrations/env.py"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from {context}_data.core.config import settings
from {context}_data.domain.entities.base import Base

# Import all models for autogeneration
from {context}_data.domain.entities import user  # noqa

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Execute migrations."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in online mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## Alembic Commands

```bash
# Create migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View current version
alembic current

# Migration history
alembic history
```

---

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY migrations/ ./migrations/
COPY alembic.ini .
COPY src/ ./src/

# Startup command with migrations
CMD alembic upgrade head && uvicorn src.{context}_data.main:app --host 0.0.0.0 --port 8001
```

---

## Checklist

- [ ] AsyncEngine created with connection pool
- [ ] async_sessionmaker configured
- [ ] Base class with mixins created
- [ ] Models defined
- [ ] Alembic configured for async
- [ ] Migrations created
