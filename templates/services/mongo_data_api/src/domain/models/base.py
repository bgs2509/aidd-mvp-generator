"""
Базовая модель MongoDB.

Общие поля для всех документов.
"""

from datetime import datetime
from typing import Annotated

from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict


class PyObjectId(str):
    """Кастомный тип для ObjectId."""

    @classmethod
    def __get_validators__(cls):
        """Валидаторы."""
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Валидация ObjectId."""
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


class MongoModel(BaseModel):
    """Базовая модель для MongoDB документов."""

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: Annotated[PyObjectId | None, Field(alias="_id")] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_mongo(self) -> dict:
        """
        Преобразовать в MongoDB документ.

        Returns:
            Словарь для MongoDB.
        """
        data = self.model_dump(by_alias=True, exclude_none=True)
        if "id" in data:
            data["_id"] = ObjectId(data.pop("id"))
        return data

    @classmethod
    def from_mongo(cls, data: dict) -> "MongoModel":
        """
        Создать модель из MongoDB документа.

        Args:
            data: Данные из MongoDB.

        Returns:
            Экземпляр модели.
        """
        if "_id" in data:
            data["id"] = str(data.pop("_id"))
        return cls(**data)


# === Пример модели ===
# class Event(MongoModel):
#     """Модель события."""
#
#     event_type: str
#     payload: dict
#     user_id: str | None = None
