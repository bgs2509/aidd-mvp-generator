"""
Главный роутер API v1.

Объединение всех роутеров версии 1.
"""

from fastapi import APIRouter

# Импорт роутеров доменов
# from src.api.v1.{domain} import router as {domain}_router

api_router = APIRouter()

# Подключение роутеров доменов
# api_router.include_router(
#     {domain}_router.router,
#     prefix="/{domain}s",
#     tags=["{Domain}s"],
# )

# === Пример подключения роутера users ===
# from src.api.v1.users import router as users_router
# api_router.include_router(
#     users_router.router,
#     prefix="/users",
#     tags=["Users"],
# )
