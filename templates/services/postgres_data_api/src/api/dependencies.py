"""
Зависимости API.

Dependency Injection для FastAPI.
"""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
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


# Тип для аннотаций
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# === Пример зависимости репозитория ===
# def get_{domain}_repository(
#     session: SessionDep,
# ) -> {Domain}Repository:
#     """Получить репозиторий {domain}."""
#     return {Domain}Repository(session=session)
#
# {Domain}RepositoryDep = Annotated[
#     {Domain}Repository,
#     Depends(get_{domain}_repository),
# ]
