"""
Утилиты для пагинации.

Общие функции и классы для пагинации результатов.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar
from math import ceil


T = TypeVar("T")


# === Константы пагинации ===

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


@dataclass
class PaginationParams:
    """
    Параметры пагинации.

    Attributes:
        page: Номер страницы (начиная с 1).
        page_size: Размер страницы.
    """

    page: int = DEFAULT_PAGE
    page_size: int = DEFAULT_PAGE_SIZE

    def __post_init__(self) -> None:
        """Валидация и нормализация параметров."""
        # Нормализация номера страницы
        if self.page < 1:
            self.page = DEFAULT_PAGE

        # Нормализация размера страницы
        if self.page_size < 1:
            self.page_size = DEFAULT_PAGE_SIZE
        elif self.page_size > MAX_PAGE_SIZE:
            self.page_size = MAX_PAGE_SIZE

    @property
    def offset(self) -> int:
        """
        Вычислить offset для SQL запроса.

        Returns:
            Смещение от начала результатов.
        """
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """
        Получить limit для SQL запроса.

        Returns:
            Максимальное количество записей.
        """
        return self.page_size


@dataclass
class PaginationMeta:
    """
    Метаданные пагинации.

    Attributes:
        page: Текущая страница.
        page_size: Размер страницы.
        total_items: Общее количество элементов.
        total_pages: Общее количество страниц.
        has_next: Есть ли следующая страница.
        has_prev: Есть ли предыдущая страница.
    """

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def from_params(
        cls,
        params: PaginationParams,
        total_items: int,
    ) -> "PaginationMeta":
        """
        Создать метаданные из параметров и общего количества.

        Args:
            params: Параметры пагинации.
            total_items: Общее количество элементов.

        Returns:
            Метаданные пагинации.
        """
        total_pages = ceil(total_items / params.page_size) if total_items > 0 else 0

        return cls(
            page=params.page,
            page_size=params.page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_prev=params.page > 1,
        )

    def to_dict(self) -> dict:
        """
        Преобразовать в словарь для API ответа.

        Returns:
            Словарь с метаданными пагинации.
        """
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total_items": self.total_items,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }


@dataclass
class PaginatedResult(Generic[T]):
    """
    Результат пагинации.

    Generic класс для возврата пагинированных данных.

    Attributes:
        items: Список элементов на текущей странице.
        meta: Метаданные пагинации.
    """

    items: list[T]
    meta: PaginationMeta

    def to_dict(self) -> dict:
        """
        Преобразовать в словарь для API ответа.

        Returns:
            Словарь с данными и метаданными.
        """
        return {
            "items": self.items,
            "pagination": self.meta.to_dict(),
        }


def paginate_list(
    items: list[T],
    params: PaginationParams,
) -> PaginatedResult[T]:
    """
    Пагинировать список в памяти.

    Используется для небольших коллекций, когда
    пагинация на уровне БД невозможна.

    Args:
        items: Полный список элементов.
        params: Параметры пагинации.

    Returns:
        Пагинированный результат.
    """
    total_items = len(items)
    start = params.offset
    end = start + params.limit

    page_items = items[start:end]
    meta = PaginationMeta.from_params(params, total_items)

    return PaginatedResult(items=page_items, meta=meta)


# === Cursor-based пагинация ===

@dataclass
class CursorPaginationParams:
    """
    Параметры cursor-based пагинации.

    Attributes:
        cursor: Курсор (ID последнего элемента).
        limit: Количество элементов.
        direction: Направление (forward/backward).
    """

    cursor: str | None = None
    limit: int = DEFAULT_PAGE_SIZE
    direction: str = "forward"

    def __post_init__(self) -> None:
        """Валидация параметров."""
        if self.limit < 1:
            self.limit = DEFAULT_PAGE_SIZE
        elif self.limit > MAX_PAGE_SIZE:
            self.limit = MAX_PAGE_SIZE

        if self.direction not in ("forward", "backward"):
            self.direction = "forward"


@dataclass
class CursorPaginationMeta:
    """
    Метаданные cursor-based пагинации.

    Attributes:
        next_cursor: Курсор для следующей страницы.
        prev_cursor: Курсор для предыдущей страницы.
        has_next: Есть ли следующая страница.
        has_prev: Есть ли предыдущая страница.
    """

    next_cursor: str | None
    prev_cursor: str | None
    has_next: bool
    has_prev: bool

    def to_dict(self) -> dict:
        """Преобразовать в словарь."""
        return {
            "next_cursor": self.next_cursor,
            "prev_cursor": self.prev_cursor,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }


@dataclass
class CursorPaginatedResult(Generic[T]):
    """
    Результат cursor-based пагинации.

    Attributes:
        items: Список элементов.
        meta: Метаданные пагинации.
    """

    items: list[T]
    meta: CursorPaginationMeta

    def to_dict(self) -> dict:
        """Преобразовать в словарь."""
        return {
            "items": self.items,
            "pagination": self.meta.to_dict(),
        }
