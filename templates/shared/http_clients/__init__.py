"""
HTTP клиенты.

Базовые HTTP клиенты для межсервисного взаимодействия.
"""

from .base_client import BaseHTTPClient
from .data_api_client import DataAPIClient

__all__ = [
    "BaseHTTPClient",
    "DataAPIClient",
]
