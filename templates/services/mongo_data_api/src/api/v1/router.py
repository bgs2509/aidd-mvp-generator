"""
Главный роутер API v1.

Объединение всех роутеров.
"""

from fastapi import APIRouter

# Импорт роутеров доменов
# from src.api.v1.{domain} import router as {domain}_router

api_router = APIRouter()

# Подключение роутеров
# api_router.include_router(
#     {domain}_router.router,
#     prefix="/{domain}s",
#     tags=["{Domain}s"],
# )
