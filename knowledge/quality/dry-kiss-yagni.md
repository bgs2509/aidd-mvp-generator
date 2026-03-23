# DRY/KISS/YAGNI Principles

> **Purpose**: Guide to applying fundamental development principles.

---

## DRY -- Don't Repeat Yourself

### Essence

Every piece of knowledge must have a single, unambiguous representation in the system.

### Examples

```python
# ❌ BAD: Duplicated logic
class UserService:
    async def create_user(self, data):
        if len(data.email) < 5 or "@" not in data.email:
            raise ValidationError("Invalid email")
        ...

    async def update_user(self, user_id, data):
        if len(data.email) < 5 or "@" not in data.email:
            raise ValidationError("Invalid email")
        ...


# ✅ GOOD: Extracted to a shared function
def validate_email(email: str) -> None:
    """Validate email."""
    if len(email) < 5 or "@" not in email:
        raise ValidationError("Invalid email")


class UserService:
    async def create_user(self, data):
        validate_email(data.email)
        ...

    async def update_user(self, user_id, data):
        validate_email(data.email)
        ...
```

### Exceptions

DRY does NOT mean you should abstract everything:
- Similar code with different business logic is fine
- Accidental similarity is not duplication
- Premature abstraction is worse than duplication

---

## KISS -- Keep It Simple, Stupid

### Essence

Simple solutions are preferred over complex ones. Complexity must be justified.

### Examples

```python
# ❌ BAD: Over-engineering
class UserFactory:
    @staticmethod
    def create_user_builder():
        return UserBuilder()

class UserBuilder:
    def __init__(self):
        self._user = {}

    def with_name(self, name):
        self._user["name"] = name
        return self

    def with_email(self, email):
        self._user["email"] = email
        return self

    def build(self):
        return User(**self._user)

# Usage
user = UserFactory.create_user_builder() \
    .with_name("John") \
    .with_email("john@example.com") \
    .build()


# ✅ GOOD: Simple solution
user = User(name="John", email="john@example.com")
```

### Recommendations

- Choose the simplest solution that works
- If code requires comments -- it's too complex
- Explicit is better than implicit
- Flat is better than nested

---

## YAGNI -- You Ain't Gonna Need It

### Essence

Don't add functionality until it is needed.

### Examples

```python
# ❌ BAD: Premature universality
class DataExporter:
    """Data exporter to different formats."""

    def export(self, data, format: str = "json"):
        if format == "json":
            return self._to_json(data)
        elif format == "xml":
            return self._to_xml(data)
        elif format == "csv":
            return self._to_csv(data)
        elif format == "yaml":
            return self._to_yaml(data)
        elif format == "excel":
            return self._to_excel(data)
        # 5 formats, only JSON is used


# ✅ GOOD: Only what is needed now
class DataExporter:
    """Data exporter to JSON."""

    def export(self, data) -> str:
        """Export to JSON."""
        return json.dumps(data)
```

### Recommendations

- Implement only current requirements
- Don't design "for the future"
- Adding a feature later is easier than maintaining an unnecessary one
- Feature flags are an exception -- they are needed for release management

---

## Application in MVP

### What Is Acceptable in MVP

```
✓ Simple solutions without abstractions
✓ Direct calls without "smart" patterns
✓ Minimal configurability
✓ Hardcoded values for constants
✓ Absence of plugin architecture
```

### What Is Not Acceptable in MVP

```
✗ Universal frameworks "for everything"
✗ Abstractions for the sake of abstractions
✗ Patterns without necessity
✗ Premature optimization
✗ "Beautiful" architecture without business value
```

---

## Balancing Principles

```
Duplication       <--------------------> Abstraction
(copy-paste)                              (DRY)
         |                                    |
         |         OPTIMUM                   |
         |            ↓                       |
         |    2-3 repetitions ->             |
         |    consider abstraction           |
         └────────────────────────────────────┘


Simplicity        <--------------------> Extensibility
(KISS)                                   (architecture)
         |                                    |
         |         OPTIMUM                   |
         |            ↓                       |
         |    Simple solution,              |
         |    ready for change              |
         └────────────────────────────────────┘


Minimalism        <--------------------> Functionality
(YAGNI)                                  (features)
         |                                    |
         |         OPTIMUM                   |
         |            ↓                       |
         |    Only what is necessary        |
         |    for the current stage         |
         └────────────────────────────────────┘
```

---

## Review Checklist

**DRY:**
- [ ] No copy-paste of business logic?
- [ ] Shared functions extracted to utilities?
- [ ] But no unnecessary abstractions created?

**KISS:**
- [ ] Solution is as simple as possible?
- [ ] Code is readable without comments?
- [ ] No overengineering?

**YAGNI:**
- [ ] Only the necessary is implemented?
- [ ] No "for the future" functions?
- [ ] No dead code?
