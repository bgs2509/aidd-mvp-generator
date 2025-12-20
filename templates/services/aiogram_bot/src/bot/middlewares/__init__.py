"""
Middleware бота.

Обработка запросов до/после хендлеров.
"""

from src.bot.middlewares.logging import LoggingMiddleware

__all__ = ["LoggingMiddleware"]
