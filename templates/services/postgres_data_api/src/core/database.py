"""
Подключение к базе данных.

Async SQLAlchemy engine и session.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import settings


# Создание async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)

# Фабрика сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """
    Получить сессию базы данных.

    Yields:
        Async сессия SQLAlchemy.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
