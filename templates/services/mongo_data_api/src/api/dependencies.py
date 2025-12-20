"""
Зависимости API.

Dependency Injection для FastAPI.
"""

from typing import Annotated

from fastapi import Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase


def get_database(request: Request) -> AsyncIOMotorDatabase:
    """
    Получить базу данных MongoDB.

    Args:
        request: HTTP запрос.

    Returns:
        База данных MongoDB.
    """
    return request.app.state.db


# Тип для аннотаций
DatabaseDep = Annotated[AsyncIOMotorDatabase, Depends(get_database)]


# === Пример зависимости репозитория ===
# def get_{domain}_repository(
#     db: DatabaseDep,
# ) -> {Domain}Repository:
#     """Получить репозиторий {domain}."""
#     collection = db["{domain}s"]
#     return {Domain}Repository(collection=collection)
#
# {Domain}RepositoryDep = Annotated[
#     {Domain}Repository,
#     Depends(get_{domain}_repository),
# ]
