"""
Базовые фабрики для тестов.

Паттерн Factory для генерации тестовых данных.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Any, Generic, TypeVar
from uuid import uuid4


T = TypeVar("T")


class BaseFactory:
    """
    Базовая фабрика для генерации тестовых данных.

    Предоставляет методы для генерации случайных данных
    различных типов.

    Использование:
        ```python
        class UserFactory(BaseFactory):
            @classmethod
            def build(cls, **overrides) -> dict:
                return {
                    "id": cls.uuid(),
                    "email": cls.email(),
                    "name": cls.name(),
                    "created_at": cls.datetime(),
                    **overrides,
                }

        # В тестах
        user = UserFactory.build()
        user_with_email = UserFactory.build(email="specific@test.com")
        ```
    """

    # === Генераторы строк ===

    @classmethod
    def string(cls, length: int = 10, prefix: str = "") -> str:
        """
        Сгенерировать случайную строку.

        Args:
            length: Длина строки.
            prefix: Префикс.

        Returns:
            Случайная строка.
        """
        chars = string.ascii_lowercase + string.digits
        random_str = "".join(random.choices(chars, k=length))
        return f"{prefix}{random_str}"

    @classmethod
    def uuid(cls) -> str:
        """Сгенерировать UUID."""
        return str(uuid4())

    @classmethod
    def email(cls, domain: str = "test.com") -> str:
        """
        Сгенерировать email.

        Args:
            domain: Домен email.

        Returns:
            Случайный email.
        """
        username = cls.string(8)
        return f"{username}@{domain}"

    @classmethod
    def phone(cls, country_code: str = "+7") -> str:
        """
        Сгенерировать номер телефона.

        Args:
            country_code: Код страны.

        Returns:
            Случайный номер телефона.
        """
        number = "".join(random.choices(string.digits, k=10))
        return f"{country_code}{number}"

    @classmethod
    def name(cls) -> str:
        """Сгенерировать случайное имя."""
        first_names = ["Иван", "Пётр", "Анна", "Мария", "Алексей", "Елена"]
        last_names = ["Иванов", "Петров", "Сидоров", "Козлова", "Смирнова"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    @classmethod
    def slug(cls, words: int = 2) -> str:
        """
        Сгенерировать slug.

        Args:
            words: Количество слов.

        Returns:
            Slug в формате word-word.
        """
        word_list = ["test", "sample", "demo", "example", "mock", "fake"]
        selected = random.choices(word_list, k=words)
        return "-".join(selected) + f"-{cls.string(4)}"

    @classmethod
    def text(cls, sentences: int = 3) -> str:
        """
        Сгенерировать случайный текст.

        Args:
            sentences: Количество предложений.

        Returns:
            Случайный текст.
        """
        templates = [
            "Это тестовое предложение номер {n}.",
            "Данные сгенерированы автоматически ({n}).",
            "Пример текста для тестирования #{n}.",
            "Случайный текст для проверки ({n}).",
        ]
        return " ".join(
            random.choice(templates).format(n=i)
            for i in range(1, sentences + 1)
        )

    # === Генераторы чисел ===

    @classmethod
    def integer(cls, min_value: int = 0, max_value: int = 1000) -> int:
        """
        Сгенерировать случайное целое число.

        Args:
            min_value: Минимальное значение.
            max_value: Максимальное значение.

        Returns:
            Случайное число.
        """
        return random.randint(min_value, max_value)

    @classmethod
    def decimal(
        cls,
        min_value: float = 0.0,
        max_value: float = 1000.0,
        precision: int = 2,
    ) -> float:
        """
        Сгенерировать случайное десятичное число.

        Args:
            min_value: Минимальное значение.
            max_value: Максимальное значение.
            precision: Количество знаков после запятой.

        Returns:
            Случайное число.
        """
        value = random.uniform(min_value, max_value)
        return round(value, precision)

    @classmethod
    def boolean(cls, probability: float = 0.5) -> bool:
        """
        Сгенерировать случайный boolean.

        Args:
            probability: Вероятность True.

        Returns:
            Случайный boolean.
        """
        return random.random() < probability

    # === Генераторы дат ===

    @classmethod
    def datetime(
        cls,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> datetime:
        """
        Сгенерировать случайную дату/время.

        Args:
            start: Начало диапазона (по умолчанию год назад).
            end: Конец диапазона (по умолчанию сейчас).

        Returns:
            Случайная дата/время.
        """
        if end is None:
            end = datetime.utcnow()
        if start is None:
            start = end - timedelta(days=365)

        delta = end - start
        random_seconds = random.randint(0, int(delta.total_seconds()))
        return start + timedelta(seconds=random_seconds)

    @classmethod
    def past_datetime(cls, days_ago: int = 30) -> datetime:
        """
        Сгенерировать дату в прошлом.

        Args:
            days_ago: Максимальное количество дней назад.

        Returns:
            Дата в прошлом.
        """
        now = datetime.utcnow()
        return cls.datetime(
            start=now - timedelta(days=days_ago),
            end=now,
        )

    @classmethod
    def future_datetime(cls, days_ahead: int = 30) -> datetime:
        """
        Сгенерировать дату в будущем.

        Args:
            days_ahead: Максимальное количество дней вперёд.

        Returns:
            Дата в будущем.
        """
        now = datetime.utcnow()
        return cls.datetime(
            start=now,
            end=now + timedelta(days=days_ahead),
        )

    # === Генераторы коллекций ===

    @classmethod
    def choice(cls, options: list[T]) -> T:
        """
        Выбрать случайный элемент из списка.

        Args:
            options: Список вариантов.

        Returns:
            Случайный элемент.
        """
        return random.choice(options)

    @classmethod
    def choices(cls, options: list[T], count: int = 3) -> list[T]:
        """
        Выбрать несколько случайных элементов.

        Args:
            options: Список вариантов.
            count: Количество элементов.

        Returns:
            Список случайных элементов.
        """
        return random.choices(options, k=count)

    @classmethod
    def sample(cls, options: list[T], count: int = 3) -> list[T]:
        """
        Выбрать несколько уникальных элементов.

        Args:
            options: Список вариантов.
            count: Количество элементов.

        Returns:
            Список уникальных элементов.
        """
        count = min(count, len(options))
        return random.sample(options, k=count)


class ModelFactory(BaseFactory, Generic[T]):
    """
    Фабрика для создания моделей.

    Расширяет BaseFactory методами для создания
    экземпляров моделей.

    Использование:
        ```python
        class UserFactory(ModelFactory[User]):
            model = User

            @classmethod
            def get_defaults(cls) -> dict:
                return {
                    "id": cls.uuid(),
                    "email": cls.email(),
                    "name": cls.name(),
                }

        # Создание экземпляра
        user = UserFactory.build()  # dict
        user_model = UserFactory.create()  # User instance
        users = UserFactory.build_batch(5)  # list[dict]
        ```
    """

    model: type[T] = None  # type: ignore

    @classmethod
    def get_defaults(cls) -> dict[str, Any]:
        """
        Получить значения по умолчанию.

        Переопределите в подклассе.

        Returns:
            Словарь значений по умолчанию.
        """
        return {}

    @classmethod
    def build(cls, **overrides: Any) -> dict[str, Any]:
        """
        Построить словарь данных модели.

        Args:
            **overrides: Переопределяемые значения.

        Returns:
            Словарь данных.
        """
        defaults = cls.get_defaults()
        defaults.update(overrides)
        return defaults

    @classmethod
    def create(cls, **overrides: Any) -> T:
        """
        Создать экземпляр модели.

        Args:
            **overrides: Переопределяемые значения.

        Returns:
            Экземпляр модели.

        Raises:
            ValueError: Если model не определён.
        """
        if cls.model is None:
            raise ValueError(
                f"Атрибут 'model' не определён в {cls.__name__}"
            )

        data = cls.build(**overrides)
        return cls.model(**data)

    @classmethod
    def build_batch(
        cls,
        count: int,
        **overrides: Any,
    ) -> list[dict[str, Any]]:
        """
        Построить список словарей.

        Args:
            count: Количество элементов.
            **overrides: Переопределяемые значения для всех.

        Returns:
            Список словарей.
        """
        return [cls.build(**overrides) for _ in range(count)]

    @classmethod
    def create_batch(cls, count: int, **overrides: Any) -> list[T]:
        """
        Создать список экземпляров модели.

        Args:
            count: Количество элементов.
            **overrides: Переопределяемые значения для всех.

        Returns:
            Список экземпляров.
        """
        return [cls.create(**overrides) for _ in range(count)]
