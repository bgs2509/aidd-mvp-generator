"""
Схемы пагинации.

Pydantic схемы для запросов и ответов с пагинацией.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from .base import BaseSchema, BaseResponseSchema


T = TypeVar("T")


# === Query параметры ===

class PaginationQueryParams(BaseSchema):
    """
    Query параметры для пагинации.

    Использование в FastAPI:
        ```python
        @router.get("/items")
        async def list_items(
            pagination: Annotated[PaginationQueryParams, Query()]
        ):
            ...
        ```
    """

    page: int = Field(
        default=1,
        ge=1,
        description="Номер страницы (начиная с 1)",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        alias="pageSize",
        description="Количество элементов на странице",
    )

    @property
    def offset(self) -> int:
        """Вычислить offset для SQL."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Получить limit для SQL."""
        return self.page_size


class CursorPaginationQueryParams(BaseSchema):
    """
    Query параметры для cursor-based пагинации.

    Использование в FastAPI:
        ```python
        @router.get("/feed")
        async def get_feed(
            pagination: Annotated[CursorPaginationQueryParams, Query()]
        ):
            ...
        ```
    """

    cursor: str | None = Field(
        default=None,
        description="Курсор (ID последнего элемента)",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Количество элементов",
    )
    direction: str = Field(
        default="forward",
        pattern="^(forward|backward)$",
        description="Направление (forward/backward)",
    )


# === Response схемы ===

class PaginationResponse(BaseResponseSchema):
    """
    Метаданные пагинации в ответе.

    Attributes:
        page: Текущая страница.
        page_size: Размер страницы.
        total_items: Общее количество элементов.
        total_pages: Общее количество страниц.
        has_next: Есть ли следующая страница.
        has_prev: Есть ли предыдущая страница.
    """

    page: int = Field(..., ge=1, description="Текущая страница")
    page_size: int = Field(
        ...,
        ge=1,
        alias="pageSize",
        description="Размер страницы",
    )
    total_items: int = Field(
        ...,
        ge=0,
        alias="totalItems",
        description="Общее количество элементов",
    )
    total_pages: int = Field(
        ...,
        ge=0,
        alias="totalPages",
        description="Общее количество страниц",
    )
    has_next: bool = Field(
        ...,
        alias="hasNext",
        description="Есть следующая страница",
    )
    has_prev: bool = Field(
        ...,
        alias="hasPrev",
        description="Есть предыдущая страница",
    )


class PaginatedResponse(BaseResponseSchema, Generic[T]):
    """
    Generic пагинированный ответ.

    Использование:
        ```python
        class ItemResponse(BaseResponseSchema):
            id: UUID
            name: str

        @router.get("/items", response_model=PaginatedResponse[ItemResponse])
        async def list_items():
            ...
        ```
    """

    items: list[T] = Field(..., description="Список элементов")
    pagination: PaginationResponse = Field(
        ...,
        description="Метаданные пагинации",
    )

    @classmethod
    def create(
        cls,
        items: list[T],
        page: int,
        page_size: int,
        total_items: int,
    ) -> "PaginatedResponse[T]":
        """
        Создать пагинированный ответ.

        Args:
            items: Список элементов.
            page: Текущая страница.
            page_size: Размер страницы.
            total_items: Общее количество.

        Returns:
            Пагинированный ответ.
        """
        from math import ceil

        total_pages = ceil(total_items / page_size) if total_items > 0 else 0

        return cls(
            items=items,
            pagination=PaginationResponse(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1,
            ),
        )


class CursorPaginationResponse(BaseResponseSchema):
    """
    Метаданные cursor-based пагинации.

    Attributes:
        next_cursor: Курсор для следующей страницы.
        prev_cursor: Курсор для предыдущей страницы.
        has_next: Есть следующая страница.
        has_prev: Есть предыдущая страница.
    """

    next_cursor: str | None = Field(
        None,
        alias="nextCursor",
        description="Курсор следующей страницы",
    )
    prev_cursor: str | None = Field(
        None,
        alias="prevCursor",
        description="Курсор предыдущей страницы",
    )
    has_next: bool = Field(
        ...,
        alias="hasNext",
        description="Есть следующая страница",
    )
    has_prev: bool = Field(
        ...,
        alias="hasPrev",
        description="Есть предыдущая страница",
    )


class CursorPaginatedResponse(BaseResponseSchema, Generic[T]):
    """Generic cursor-пагинированный ответ."""

    items: list[T] = Field(..., description="Список элементов")
    pagination: CursorPaginationResponse = Field(
        ...,
        description="Метаданные пагинации",
    )
