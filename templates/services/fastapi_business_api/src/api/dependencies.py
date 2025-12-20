"""
Зависимости API.

Dependency Injection для FastAPI.
"""

from typing import Annotated

import httpx
from fastapi import Depends, Request

from src.infrastructure.http.data_api_client import DataApiClient


def get_http_client(request: Request) -> httpx.AsyncClient:
    """
    Получить HTTP клиент.

    Args:
        request: HTTP запрос.

    Returns:
        Экземпляр HTTP клиента.
    """
    return request.app.state.http_client


def get_request_id(request: Request) -> str | None:
    """
    Получить Request ID.

    Args:
        request: HTTP запрос.

    Returns:
        Request ID или None.
    """
    return getattr(request.state, "request_id", None)


def get_data_api_client(
    http_client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    request_id: Annotated[str | None, Depends(get_request_id)],
) -> DataApiClient:
    """
    Получить клиент Data API.

    Args:
        http_client: HTTP клиент.
        request_id: Request ID для корреляции.

    Returns:
        Экземпляр клиента Data API.
    """
    return DataApiClient(
        client=http_client,
        request_id=request_id,
    )


# === Типы для аннотаций ===
HttpClientDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]
DataApiClientDep = Annotated[DataApiClient, Depends(get_data_api_client)]
RequestIdDep = Annotated[str | None, Depends(get_request_id)]


# === Пример зависимости сервиса ===
# def get_{domain}_service(
#     data_client: DataApiClientDep,
# ) -> {Domain}Service:
#     """Получить сервис {domain}."""
#     return {Domain}Service(data_client=data_client)
#
# {Domain}ServiceDep = Annotated[{Domain}Service, Depends(get_{domain}_service)]
