"""
Базовые Pydantic схемы.

Общие схемы и миксины для всех сервисов.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """
    Базовая схема.

    Все схемы должны наследоваться от этого класса.

    Конфигурация:
        - from_attributes: Позволяет создавать из ORM моделей.
        - populate_by_name: Позволяет использовать alias.
        - str_strip_whitespace: Автоматически удаляет пробелы.
        - validate_assignment: Валидация при присваивании.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class BaseResponseSchema(BaseSchema):
    """
    Базовая схема для API ответов.

    Включает сериализацию UUID и datetime.

    Конфигурация:
        - ser_json_timedelta: Сериализация timedelta в секунды.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        ser_json_timedelta="float",
    )


class TimestampMixin(BaseModel):
    """
    Миксин с временными метками.

    Attributes:
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    created_at: datetime = Field(
        ...,
        description="Время создания записи",
    )
    updated_at: datetime = Field(
        ...,
        description="Время последнего обновления",
    )


class IDMixin(BaseModel):
    """
    Миксин с идентификатором.

    Attributes:
        id: Уникальный идентификатор (UUID).
    """

    id: UUID = Field(
        ...,
        description="Уникальный идентификатор",
    )


class FullModelMixin(IDMixin, TimestampMixin):
    """
    Полный миксин для сущностей.

    Включает ID и временные метки.
    Используется для схем чтения (Response).
    """

    pass


# === Общие схемы для запросов ===

class IDRequest(BaseSchema):
    """Запрос с ID."""

    id: UUID = Field(..., description="Идентификатор")


class IDsRequest(BaseSchema):
    """Запрос с несколькими ID."""

    ids: list[UUID] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Список идентификаторов",
    )


# === Общие схемы для ответов ===

class SuccessResponse(BaseResponseSchema):
    """Успешный ответ без данных."""

    success: bool = Field(default=True, description="Флаг успеха")
    message: str = Field(default="OK", description="Сообщение")


class DeleteResponse(BaseResponseSchema):
    """Ответ на удаление."""

    success: bool = Field(default=True, description="Флаг успеха")
    deleted_id: UUID = Field(..., description="ID удалённой записи")


class CountResponse(BaseResponseSchema):
    """Ответ с количеством."""

    count: int = Field(..., ge=0, description="Количество")


class BulkOperationResponse(BaseResponseSchema):
    """Ответ на массовую операцию."""

    success_count: int = Field(
        ...,
        ge=0,
        description="Количество успешных операций",
    )
    failed_count: int = Field(
        ...,
        ge=0,
        description="Количество неудачных операций",
    )
    errors: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Список ошибок",
    )
