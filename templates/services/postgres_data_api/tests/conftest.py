"""
Фикстуры для тестов {context}_data.

Testcontainers для интеграционных тестов.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from testcontainers.postgres import PostgresContainer

from src.main import create_app
from src.domain.entities.base import Base
from src.api.dependencies import get_session


@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL контейнер для тестов."""
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def database_url(postgres_container) -> str:
    """URL базы данных."""
    sync_url = postgres_container.get_connection_url()
    return sync_url.replace("postgresql://", "postgresql+asyncpg://")


@pytest.fixture(scope="session")
async def engine(database_url):
    """Движок SQLAlchemy."""
    engine = create_async_engine(database_url, echo=True)

    # Создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Удаление таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncSession:
    """Сессия БД с откатом."""
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def app(db_session):
    """Тестовое приложение."""
    app = create_app()

    # Подмена зависимости сессии
    app.dependency_overrides[get_session] = lambda: db_session

    yield app

    app.dependency_overrides.clear()


@pytest.fixture
async def client(app) -> AsyncClient:
    """Асинхронный тест-клиент."""
    async with AsyncClient(
        app=app,
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client
