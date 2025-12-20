"""
Базовая модель SQLAlchemy.

Общие поля для всех сущностей.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""

    pass


class TimestampMixin:
    """Mixin с временными метками."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDMixin:
    """Mixin с UUID первичным ключом."""

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )


# === Пример модели ===
# class User(Base, UUIDMixin, TimestampMixin):
#     """Модель пользователя."""
#
#     __tablename__ = "users"
#
#     email: Mapped[str] = mapped_column(unique=True, index=True)
#     name: Mapped[str] = mapped_column(nullable=False)
#     is_active: Mapped[bool] = mapped_column(default=True)
