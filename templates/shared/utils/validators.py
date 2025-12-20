"""
Общие валидаторы.

Переиспользуемые валидаторы для Pydantic моделей и бизнес-логики.
"""

import re
from typing import Any


# === Регулярные выражения ===

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

PHONE_REGEX = re.compile(
    r"^\+?[1-9]\d{1,14}$"  # E.164 формат
)

SLUG_REGEX = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
)

UUID_REGEX = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


# === Валидаторы строк ===

def validate_email(value: str) -> str:
    """
    Валидировать email адрес.

    Args:
        value: Email для проверки.

    Returns:
        Валидный email в нижнем регистре.

    Raises:
        ValueError: Если email невалиден.
    """
    if not value:
        raise ValueError("Email не может быть пустым")

    value = value.strip().lower()

    if not EMAIL_REGEX.match(value):
        raise ValueError(f"Невалидный email: {value}")

    return value


def validate_phone(value: str) -> str:
    """
    Валидировать номер телефона в формате E.164.

    Args:
        value: Номер телефона.

    Returns:
        Нормализованный номер телефона.

    Raises:
        ValueError: Если номер невалиден.
    """
    if not value:
        raise ValueError("Номер телефона не может быть пустым")

    # Удаляем пробелы, скобки, дефисы
    normalized = re.sub(r"[\s\-\(\)]", "", value)

    if not PHONE_REGEX.match(normalized):
        raise ValueError(f"Невалидный номер телефона: {value}")

    return normalized


def validate_slug(value: str) -> str:
    """
    Валидировать slug (URL-friendly идентификатор).

    Args:
        value: Slug для проверки.

    Returns:
        Валидный slug.

    Raises:
        ValueError: Если slug невалиден.
    """
    if not value:
        raise ValueError("Slug не может быть пустым")

    value = value.strip().lower()

    if not SLUG_REGEX.match(value):
        raise ValueError(
            f"Невалидный slug: {value}. "
            "Используйте только строчные буквы, цифры и дефисы."
        )

    return value


def validate_uuid(value: str) -> str:
    """
    Валидировать UUID строку.

    Args:
        value: UUID для проверки.

    Returns:
        UUID в нижнем регистре.

    Raises:
        ValueError: Если UUID невалиден.
    """
    if not value:
        raise ValueError("UUID не может быть пустым")

    value = value.strip().lower()

    if not UUID_REGEX.match(value):
        raise ValueError(f"Невалидный UUID: {value}")

    return value


# === Валидаторы чисел ===

def validate_positive(value: int | float, field_name: str = "Значение") -> int | float:
    """
    Валидировать положительное число.

    Args:
        value: Число для проверки.
        field_name: Название поля для сообщения об ошибке.

    Returns:
        Исходное значение, если валидно.

    Raises:
        ValueError: Если число не положительное.
    """
    if value <= 0:
        raise ValueError(f"{field_name} должно быть положительным числом")
    return value


def validate_non_negative(
    value: int | float,
    field_name: str = "Значение",
) -> int | float:
    """
    Валидировать неотрицательное число.

    Args:
        value: Число для проверки.
        field_name: Название поля для сообщения об ошибке.

    Returns:
        Исходное значение, если валидно.

    Raises:
        ValueError: Если число отрицательное.
    """
    if value < 0:
        raise ValueError(f"{field_name} не может быть отрицательным")
    return value


def validate_range(
    value: int | float,
    min_value: int | float,
    max_value: int | float,
    field_name: str = "Значение",
) -> int | float:
    """
    Валидировать число в диапазоне.

    Args:
        value: Число для проверки.
        min_value: Минимальное значение (включительно).
        max_value: Максимальное значение (включительно).
        field_name: Название поля для сообщения об ошибке.

    Returns:
        Исходное значение, если валидно.

    Raises:
        ValueError: Если число вне диапазона.
    """
    if not min_value <= value <= max_value:
        raise ValueError(
            f"{field_name} должно быть в диапазоне [{min_value}, {max_value}]"
        )
    return value


# === Валидаторы строк с ограничениями ===

def validate_length(
    value: str,
    min_length: int = 0,
    max_length: int | None = None,
    field_name: str = "Строка",
) -> str:
    """
    Валидировать длину строки.

    Args:
        value: Строка для проверки.
        min_length: Минимальная длина.
        max_length: Максимальная длина (None = без ограничения).
        field_name: Название поля для сообщения об ошибке.

    Returns:
        Исходная строка, если валидна.

    Raises:
        ValueError: Если длина строки не соответствует ограничениям.
    """
    length = len(value)

    if length < min_length:
        raise ValueError(
            f"{field_name} должна содержать минимум {min_length} символов"
        )

    if max_length is not None and length > max_length:
        raise ValueError(
            f"{field_name} не должна превышать {max_length} символов"
        )

    return value


def validate_not_empty(value: str, field_name: str = "Поле") -> str:
    """
    Валидировать непустую строку (после trim).

    Args:
        value: Строка для проверки.
        field_name: Название поля для сообщения об ошибке.

    Returns:
        Строка без пробелов по краям.

    Raises:
        ValueError: Если строка пустая или содержит только пробелы.
    """
    if not value or not value.strip():
        raise ValueError(f"{field_name} не может быть пустым")
    return value.strip()


# === Pydantic валидаторы (для использования с field_validator) ===

def pydantic_email_validator(value: Any) -> str:
    """Pydantic валидатор для email."""
    if not isinstance(value, str):
        raise ValueError("Email должен быть строкой")
    return validate_email(value)


def pydantic_phone_validator(value: Any) -> str:
    """Pydantic валидатор для телефона."""
    if not isinstance(value, str):
        raise ValueError("Телефон должен быть строкой")
    return validate_phone(value)


def pydantic_slug_validator(value: Any) -> str:
    """Pydantic валидатор для slug."""
    if not isinstance(value, str):
        raise ValueError("Slug должен быть строкой")
    return validate_slug(value)
