"""
Middleware для FastAPI.

Log-Driven Design middleware:
- RequestLoggingMiddleware: логирование HTTP запросов
"""

from src.middlewares.request_logging import RequestLoggingMiddleware

__all__ = ["RequestLoggingMiddleware"]
