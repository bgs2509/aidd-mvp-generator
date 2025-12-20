# Принципы DRY/KISS/YAGNI

> **Назначение**: Руководство по применению базовых принципов разработки.

---

## DRY — Don't Repeat Yourself

### Суть

Каждая часть знания должна иметь единственное, однозначное представление в системе.

### Примеры

```python
# ❌ ПЛОХО: Дублирование логики
class UserService:
    async def create_user(self, data):
        if len(data.email) < 5 or "@" not in data.email:
            raise ValidationError("Invalid email")
        ...

    async def update_user(self, user_id, data):
        if len(data.email) < 5 or "@" not in data.email:
            raise ValidationError("Invalid email")
        ...


# ✅ ХОРОШО: Вынесение в общую функцию
def validate_email(email: str) -> None:
    """Валидировать email."""
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

### Исключения

DRY НЕ означает, что нужно абстрагировать всё:
- Похожий код с разной бизнес-логикой — это нормально
- Случайное сходство — не дублирование
- Преждевременная абстракция хуже дублирования

---

## KISS — Keep It Simple, Stupid

### Суть

Простые решения предпочтительнее сложных. Сложность должна быть обоснована.

### Примеры

```python
# ❌ ПЛОХО: Переусложнение
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

# Использование
user = UserFactory.create_user_builder() \
    .with_name("John") \
    .with_email("john@example.com") \
    .build()


# ✅ ХОРОШО: Простое решение
user = User(name="John", email="john@example.com")
```

### Рекомендации

- Выбирайте самое простое решение, которое работает
- Если код требует комментариев — он слишком сложный
- Явное лучше неявного
- Плоское лучше вложенного

---

## YAGNI — You Ain't Gonna Need It

### Суть

Не добавляйте функциональность, пока она не понадобится.

### Примеры

```python
# ❌ ПЛОХО: Преждевременная универсальность
class DataExporter:
    """Экспортер данных в разные форматы."""

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
        # 5 форматов, используется только JSON


# ✅ ХОРОШО: Только то, что нужно сейчас
class DataExporter:
    """Экспортер данных в JSON."""

    def export(self, data) -> str:
        """Экспортировать в JSON."""
        return json.dumps(data)
```

### Рекомендации

- Реализуйте только текущие требования
- Не проектируйте "на будущее"
- Добавить функцию позже проще, чем поддерживать лишнюю
- Feature flags — исключение, они нужны для управления релизами

---

## Применение в MVP

### Что допустимо в MVP

```
✓ Простые решения без абстракций
✓ Прямые вызовы без "умных" паттернов
✓ Минимальная конфигурируемость
✓ Hardcoded значения для констант
✓ Отсутствие плагинной архитектуры
```

### Что недопустимо в MVP

```
✗ Универсальные фреймворки "для всего"
✗ Абстракции ради абстракций
✗ Паттерны без необходимости
✗ Преждевременная оптимизация
✗ "Красивая" архитектура без бизнес-ценности
```

---

## Баланс принципов

```
Дублирование     ◄─────────────────────► Абстракция
(копи-паст)                              (DRY)
         │                                    │
         │         ОПТИМУМ                   │
         │            ↓                       │
         │    2-3 повторения →               │
         │    рассмотреть абстракцию         │
         └────────────────────────────────────┘


Простота         ◄─────────────────────► Расширяемость
(KISS)                                   (архитектура)
         │                                    │
         │         ОПТИМУМ                   │
         │            ↓                       │
         │    Простое решение,              │
         │    готовое к изменению           │
         └────────────────────────────────────┘


Минимализм       ◄─────────────────────► Функциональность
(YAGNI)                                  (фичи)
         │                                    │
         │         ОПТИМУМ                   │
         │            ↓                       │
         │    Только необходимое            │
         │    для текущего этапа            │
         └────────────────────────────────────┘
```

---

## Чек-лист при ревью

**DRY:**
- [ ] Нет копи-паста бизнес-логики?
- [ ] Общие функции вынесены в утилиты?
- [ ] Но не создано лишних абстракций?

**KISS:**
- [ ] Решение максимально простое?
- [ ] Код читается без комментариев?
- [ ] Нет overengineering?

**YAGNI:**
- [ ] Реализовано только необходимое?
- [ ] Нет "на будущее" функций?
- [ ] Нет мёртвого кода?
