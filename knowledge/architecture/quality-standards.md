# Quality Standards

> **Purpose**: Code quality requirements by maturity level.

---

## Level 2 (MVP) — Primary Level

### Mandatory Requirements

| Category | Requirement | Threshold |
|-----------|------------|-------|
| Test Coverage | Code coverage | >=75% |
| Testing | Unit tests | Required |
| Testing | Integration tests | Required |
| Linting | Ruff check | 0 errors |
| Formatting | Ruff format | Compliant |
| Typing | Type hints | All functions |
| Documentation | Docstrings | All public |
| CI | Pipeline | Configured |

### Performance Metrics

| Metric | Threshold |
|---------|-------|
| API response time | <500ms (p95) |
| Availability | 99% |

---

## Test Coverage

### What Should Be Covered

```
✓ Application Services (business logic)
✓ Domain Services
✓ Repositories
✓ API endpoints
✓ HTTP clients
✓ Schema validation
✓ Error handling
```

### What Can Be Excluded

```
- __init__.py
- Configuration files
- Abstract base classes
- Simple getters/setters
```

### Measuring Coverage

```bash
# Run with measurement
pytest --cov=src --cov-report=term --cov-report=html

# Check threshold
pytest --cov=src --cov-fail-under=75
```

---

## Test Types

### Unit Tests

```python
"""Unit tests -- isolated, with mocks."""

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

### Integration Tests

```python
"""Integration tests -- with real dependencies."""

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

## Linting and Formatting

### Ruff Configuration

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

### Commands

```bash
# Check
ruff check src tests

# Auto-fix
ruff check --fix src tests

# Format
ruff format src tests
```

---

## Typing

### Requirements

```python
# All functions must have type hints

# GOOD
async def create_user(data: CreateUserDTO) -> UserDTO:
    """Create a user."""
    pass

# BAD
async def create_user(data):  # No types!
    pass
```

### Modern Types (Python 3.10+)

```python
# Use built-in types
users: list[User] = []           # NOT List[User]
settings: dict[str, str] = {}    # NOT Dict[str, str]
name: str | None = None          # NOT Optional[str]

# Union for multiple types
result: User | None = None
value: int | str = 0
```

### Mypy Configuration

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

## Documentation

### Docstrings (Google Style)

```python
def create_order(
    customer_id: UUID,
    items: list[OrderItem],
    discount: Decimal | None = None,
) -> Order:
    """
    Create a new order.

    Creates an order with the specified items and optionally
    applies a discount.

    Args:
        customer_id: Customer ID.
        items: List of items in the order.
        discount: Discount amount (optional).

    Returns:
        The created order object.

    Raises:
        ValidationError: If the item list is empty.
        NotFoundError: If the customer is not found.

    Example:
        >>> order = create_order(
        ...     customer_id=UUID("..."),
        ...     items=[OrderItem(...)],
        ... )
    """
```

### Classes

```python
class OrderService:
    """
    Service for working with orders.

    Provides methods for creating, retrieving, and managing
    orders through Data API.

    Attributes:
        data_client: HTTP client for Data API.

    Example:
        >>> service = OrderService(data_client)
        >>> order = await service.create_order(dto)
    """

    def __init__(self, data_client: DataApiClient):
        """
        Initialize service.

        Args:
            data_client: HTTP client for Data API.
        """
        self.data_client = data_client
```

---

## CI Pipeline

### Minimum Set of Checks

```bash
pip install -r requirements.txt -r requirements-dev.txt
ruff check src tests
ruff format --check src tests
mypy src
pytest --cov=src --cov-fail-under=75
```

---

## Quality Checklist

- [ ] Coverage >=75%
- [ ] All tests pass
- [ ] Ruff check: 0 errors
- [ ] Ruff format: compliant
- [ ] All functions are typed
- [ ] All public elements are documented
- [ ] CI pipeline is configured and passes
