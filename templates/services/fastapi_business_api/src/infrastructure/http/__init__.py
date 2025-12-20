"""
HTTP клиенты.

Клиенты для взаимодействия с внешними сервисами.
"""

from src.infrastructure.http.base_client import BaseHttpClient
from src.infrastructure.http.data_api_client import DataApiClient

__all__ = ["BaseHttpClient", "DataApiClient"]
