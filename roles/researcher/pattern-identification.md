# Функция: Выявление паттернов

> **Назначение**: Идентификация архитектурных и кодовых паттернов.

---

## Цель

Определить используемые паттерны для обеспечения консистентности
при добавлении нового кода.

---

## Архитектурные паттерны

### DDD (Domain-Driven Design)

```bash
# Признаки DDD
Grep: "domain/"
Grep: "application/"
Grep: "infrastructure/"
Grep: "Entity"
Grep: "ValueObject"
Grep: "AggregateRoot"
```

**Чек-лист DDD**:
- [ ] Выделен domain слой
- [ ] Есть entities и value objects
- [ ] Application services отделены от domain
- [ ] Infrastructure содержит адаптеры

### Hexagonal Architecture

```bash
# Признаки Hexagonal
Grep: "ports/"
Grep: "adapters/"
Grep: "Port"
Grep: "Adapter"
```

**Чек-лист Hexagonal**:
- [ ] Определены порты (интерфейсы)
- [ ] Есть входящие адаптеры (API, CLI)
- [ ] Есть исходящие адаптеры (DB, HTTP)
- [ ] Domain не зависит от infrastructure

### HTTP-only доступ к данным

```bash
# Признаки HTTP-only
Grep: "httpx"
Grep: "DataApiClient"
Grep: "async def.*get.*http"
```

**Чек-лист HTTP-only**:
- [ ] Бизнес-сервисы используют HTTP клиенты
- [ ] Нет прямого импорта SQLAlchemy в бизнес-слое
- [ ] Data API отдельный сервис

---

## Кодовые паттерны

### Repository Pattern

```bash
Grep: "class.*Repository"
Grep: "def get_by_id"
Grep: "def create"
Grep: "def update"
Grep: "def delete"
```

### Service Pattern

```bash
Grep: "class.*Service"
Grep: "def __init__.*repository"
Grep: "def __init__.*client"
```

### Factory Pattern

```bash
Grep: "def create_app"
Grep: "def get_.*factory"
Grep: "Factory"
```

### Dependency Injection

```bash
Grep: "Depends("
Grep: "@inject"
Grep: "def get_.*service"
```

---

## Паттерны именования

### Файлы

```bash
# Проверить стиль
ls -la src/**/*.py

# snake_case? kebab-case?
```

### Классы

```bash
Grep: "^class "
# PascalCase?
```

### Функции

```bash
Grep: "^def "
Grep: "async def "
# snake_case?
```

---

## Результат анализа

```markdown
## Архитектурные паттерны

| Паттерн | Используется | Комментарий |
|---------|--------------|-------------|
| DDD | Да/Нет | |
| Hexagonal | Да/Нет | |
| HTTP-only | Да/Нет | |

## Кодовые паттерны

| Паттерн | Используется | Пример |
|---------|--------------|--------|
| Repository | Да | UserRepository |
| Service | Да | OrderService |
| Factory | Да | create_app() |
| DI | Да | Depends() |

## Стиль именования

| Элемент | Стиль |
|---------|-------|
| Файлы | snake_case |
| Классы | PascalCase |
| Функции | snake_case |
```

---

## Источники

| Документ | Описание |
|----------|----------|
| `.ai-framework/docs/atomic/architecture/ddd-hexagonal-principles.md` | DDD и Hexagonal |
| `.ai-framework/docs/atomic/architecture/service-separation-principles.md` | Разделение сервисов |
