# Function: Convention Compliance Check

> **Purpose**: Verifying code compliance with project conventions.

---

## Goal

Verify that the code complies with code conventions
defined in `conventions.md`.

---

## Verified Conventions

### 1. Naming

#### Python Code

| Element | Style | Example |
|---------|-------|---------|
| Package | snake_case | `booking_api` |
| Module | snake_case | `user_service.py` |
| Class | PascalCase | `UserService` |
| Function | snake_case | `create_user` |
| Variable | snake_case | `user_id` |
| Constant | UPPER_SNAKE | `MAX_RETRIES` |

**Verification commands:**

```bash
# Check class names (should be PascalCase)
Grep: "^class [a-z]" in services/
# If found — violation

# Check function names (should be snake_case)
Grep: "def [A-Z]" in services/
# If found — violation

# Check constants (should be UPPER_SNAKE)
Grep: "^[A-Z][a-z].*=" in services/*/src/*/core/
# May be a violation (manual check needed)
```

#### API and Database

| Element | Style | Example |
|---------|-------|---------|
| API path | kebab-case | `/api/v1/user-profiles` |
| Query parameter | snake_case | `?user_id=123` |
| JSON field | snake_case | `{"user_name": "..."}` |
| DB table | snake_case, plural | `users` |
| DB column | snake_case | `created_at` |

**Verification commands:**

```bash
# Check API paths
Grep: '@router\.(get|post|put|delete)\("[^"]*[A-Z]' in services/
# CamelCase in paths — violation

# Check tables
Grep: '__tablename__.*[A-Z]' in services/
# CamelCase in tables — violation
```

### 2. Type Hints

```
RULE: All functions must have type hints.

Check:
- All function parameters are typed
- Return values are typed
- Modern types are used (list instead of List)
```

**Verification commands:**

```bash
# Check for missing types
Grep: "def.*\):" in services/
# Functions without -> return type

# Check for deprecated types
Grep: "from typing import List" in services/
Grep: "from typing import Dict" in services/
# Should use list, dict (Python 3.9+)
```

### 3. Docstrings

```
RULE: All public functions and classes have docstrings.
FORMAT: Google style, in Russian.

Check:
- All classes have docstrings
- All public methods have docstrings
- Docstrings are in Russian
```

**Correct docstring example:**

```python
def create_user(name: str, email: str) -> User:
    """
    Создать нового пользователя.

    Args:
        name: Имя пользователя.
        email: Email адрес.

    Returns:
        Созданный объект пользователя.

    Raises:
        ValidationError: Если данные невалидны.
    """
```

**Verification commands:**

```bash
# Search for classes without docstrings
Grep: "^class.*:\s*$" in services/
# Class without docstring on the next line — violation

# Search for functions without docstrings
Grep: "def.*:\s*$" in services/
# Function without docstring — violation (for public ones)
```

### 4. Imports

```
RULE: Imports are organized and grouped.

Order:
1. Standard library
2. Third-party libraries
3. Local imports

Separation:
- Empty line between groups
- Absolute imports
```

**Correct imports example:**

```python
# Standard library
import asyncio
from datetime import datetime
from uuid import UUID

# Third-party libraries
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# Local imports
from booking_api.core.config import settings
from booking_api.application.services.user_service import UserService
```

### 5. Error Handling

```
RULE: Custom exceptions are used.

Check:
- Custom exceptions defined in core/exceptions.py
- Bare except is not used
- Exceptions are informative
```

**Verification commands:**

```bash
# Search for bare except
Grep: "except:" in services/
# Bare except — violation

# Search for custom exceptions
Grep: "class.*Error.*Exception" in services/*/src/*/core/
# Should be defined
```

---

## Verification Checklist

### Naming

- [ ] Classes in PascalCase
- [ ] Functions in snake_case
- [ ] Variables in snake_case
- [ ] Constants in UPPER_SNAKE_CASE
- [ ] API paths in kebab-case
- [ ] DB tables in snake_case, plural

### Type Hints

- [ ] All functions are typed
- [ ] Modern types are used
- [ ] Return types are specified

### Docstrings

- [ ] All classes have docstrings
- [ ] All public functions have docstrings
- [ ] Docstrings are in Russian
- [ ] Google style is used

### Imports

- [ ] Imports are grouped
- [ ] Empty lines between groups
- [ ] Absolute imports

### Errors

- [ ] Custom exceptions are defined
- [ ] No bare except
- [ ] Exceptions are informative

---

## Automated Tools

### Ruff (linter)

```bash
# Run check
ruff check services/

# Auto-fix
ruff check --fix services/
```

### Ruff (formatting)

```bash
# Check formatting
ruff format --check services/

# Auto-format
ruff format services/
```

### Mypy (types)

```bash
# Type checking
mypy services/
```

---

## Verification Result

```markdown
## Convention Check

### Status: PASSED / FAILED

### Automated Checks

| Tool | Status | Errors |
|------|--------|--------|
| ruff check | ✓/✗ | {N} |
| ruff format | ✓/✗ | {N} |
| mypy | ✓/✗ | {N} |

### Manual Checks

| Category | Status | Comment |
|----------|--------|---------|
| Naming | ✓/✗ | {Comment} |
| Type Hints | ✓/✗ | {Comment} |
| Docstrings | ✓/✗ | {Comment} |
| Imports | ✓/✗ | {Comment} |
| Errors | ✓/✗ | {Comment} |

### Violations Found

| # | File | Line | Violation | Recommendation |
|---|------|------|-----------|----------------|
| 1 | {file} | {line} | {description} | {how to fix} |
```

---

## Sources

| Document | Description |
|----------|-------------|
| `conventions.md` | Code conventions |
| `knowledge/architecture/naming/` | Naming rules |
