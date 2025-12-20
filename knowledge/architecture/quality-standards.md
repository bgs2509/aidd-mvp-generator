# Стандарты качества

> **Назначение**: Требования к качеству кода по уровням зрелости.

---

## Level 2 (MVP) — Основной уровень

### Обязательные требования

| Категория | Требование | Порог |
|-----------|------------|-------|
| Покрытие тестами | Code coverage | ≥75% |
| Тестирование | Unit тесты | Обязательно |
| Тестирование | Integration тесты | Обязательно |
| Линтинг | Ruff check | 0 ошибок |
| Форматирование | Ruff format | Соответствует |
| Типизация | Type hints | Все функции |
| Документация | Docstrings | Все публичные |
| CI | Pipeline | Настроен |

### Метрики производительности

| Метрика | Порог |
|---------|-------|
| Время отклика API | <500ms (p95) |
| Доступность | 99% |

---

## Покрытие тестами

### Что должно быть покрыто

```
✓ Application Services (бизнес-логика)
✓ Domain Services
✓ Repositories
✓ API эндпоинты
✓ HTTP клиенты
✓ Валидация схем
✓ Обработка ошибок
```

### Что можно исключить

```
- __init__.py
- Конфигурационные файлы
- Абстрактные базовые классы
- Простые getters/setters
```

### Измерение покрытия

```bash
# Запуск с измерением
pytest --cov=src --cov-report=term --cov-report=html

# Проверка порога
pytest --cov=src --cov-fail-under=75
```

---

## Типы тестов

### Unit тесты

```python
"""Unit тесты — изолированные, с моками."""

import pytest
from unittest.mock import AsyncMock

from booking_api.application.services.user_service import UserService


class TestUserService:
    @pytest.mark.asyncio
    async def test_create_user_success(self):
        # Arrange
        mock_client = AsyncMock()
        mock_client.create_user.return_value = {"id": "...", "name": "Test"}

        service = UserService(mock_client)

        # Act
        result = await service.create_user(CreateUserDTO(name="Test"))

        # Assert
        assert result.name == "Test"
        mock_client.create_user.assert_called_once()
```

### Integration тесты

```python
"""Integration тесты — с реальными зависимостями."""

import pytest
from httpx import AsyncClient


class TestUserAPI:
    @pytest.mark.asyncio
    async def test_create_user_api(self, client: AsyncClient):
        # Act
        response = await client.post(
            "/api/v1/users",
            json={"name": "Test", "email": "test@example.com"},
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["name"] == "Test"
```

---

## Линтинг и форматирование

### Ruff конфигурация

```toml
# pyproject.toml

[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["booking_api"]
```

### Команды

```bash
# Проверка
ruff check src tests

# Автоисправление
ruff check --fix src tests

# Форматирование
ruff format src tests
```

---

## Типизация

### Требования

```python
# Все функции должны иметь type hints

# ХОРОШО
async def create_user(data: CreateUserDTO) -> UserDTO:
    """Создать пользователя."""
    pass

# ПЛОХО
async def create_user(data):  # Нет типов!
    pass
```

### Современные типы (Python 3.10+)

```python
# Использовать встроенные типы
users: list[User] = []           # НЕ List[User]
settings: dict[str, str] = {}    # НЕ Dict[str, str]
name: str | None = None          # НЕ Optional[str]

# Union для нескольких типов
result: User | None = None
value: int | str = 0
```

### Mypy конфигурация

```toml
# pyproject.toml

[tool.mypy]
python_version = "3.11"
strict = false
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

---

## Документация

### Docstrings (Google стиль)

```python
def create_order(
    customer_id: UUID,
    items: list[OrderItem],
    discount: Decimal | None = None,
) -> Order:
    """
    Создать новый заказ.

    Создаёт заказ с указанными товарами и опционально
    применяет скидку.

    Args:
        customer_id: ID покупателя.
        items: Список товаров в заказе.
        discount: Размер скидки (опционально).

    Returns:
        Созданный объект заказа.

    Raises:
        ValidationError: Если список товаров пуст.
        NotFoundError: Если покупатель не найден.

    Example:
        >>> order = create_order(
        ...     customer_id=UUID("..."),
        ...     items=[OrderItem(...)],
        ... )
    """
```

### Классы

```python
class OrderService:
    """
    Сервис для работы с заказами.

    Предоставляет методы для создания, получения и управления
    заказами через Data API.

    Attributes:
        data_client: HTTP клиент для Data API.

    Example:
        >>> service = OrderService(data_client)
        >>> order = await service.create_order(dto)
    """

    def __init__(self, data_client: DataApiClient):
        """
        Инициализация сервиса.

        Args:
            data_client: HTTP клиент для Data API.
        """
        self.data_client = data_client
```

---

## CI Pipeline

### Минимальный набор проверок

```yaml
# .github/workflows/ci.yml

name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt

      - name: Lint
        run: ruff check src tests

      - name: Format check
        run: ruff format --check src tests

      - name: Type check
        run: mypy src

      - name: Test
        run: pytest --cov=src --cov-fail-under=75
```

---

## Чек-лист качества

- [ ] Coverage ≥75%
- [ ] Все тесты проходят
- [ ] Ruff check: 0 ошибок
- [ ] Ruff format: соответствует
- [ ] Все функции типизированы
- [ ] Все публичные элементы документированы
- [ ] CI pipeline настроен и проходит
