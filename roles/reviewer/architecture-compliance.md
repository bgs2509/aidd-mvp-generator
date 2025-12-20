# Функция: Проверка архитектуры

> **Назначение**: Верификация соответствия кода архитектурным принципам.

---

## Цель

Проверить, что реализованный код соответствует
архитектурным принципам AIDD-MVP Framework.

---

## Входные данные

| Артефакт | Путь | Описание |
|----------|------|----------|
| Код | `services/` | Реализованные сервисы |
| Архитектура | `ai-docs/docs/architecture/` | Архитектурное решение |
| Ворота | IMPLEMENT_OK | Должны быть пройдены |

---

## Проверяемые принципы

### 1. HTTP-only доступ к данным

```
ПРАВИЛО: Business сервисы НЕ обращаются к БД напрямую.

Проверить:
- Business API использует HTTP клиент для Data API
- Нет импортов SQLAlchemy в business сервисах
- Нет прямых подключений к БД
```

**Команды проверки:**

```bash
# Поиск импортов SQLAlchemy в business сервисах
Grep: "from sqlalchemy" in services/{context}_api/
Grep: "import sqlalchemy" in services/{context}_api/

# Должно быть ПУСТО. Если найдено — НАРУШЕНИЕ.

# Поиск HTTP клиентов
Grep: "httpx" in services/{context}_api/
Grep: "DataApiClient" in services/{context}_api/

# Должны быть найдены. Если нет — НАРУШЕНИЕ.
```

### 2. DDD структура

```
ПРАВИЛО: Код организован по слоям DDD.

Проверить:
- api/ — только роуты и HTTP обработка
- application/ — сервисы приложения
- domain/ — бизнес-логика
- infrastructure/ — адаптеры
```

**Команды проверки:**

```bash
# Проверка структуры
ls services/{context}_api/src/{context}_api/
# Должны быть: api/, application/, domain/, infrastructure/

# Проверка зависимостей
# api/ НЕ должен импортировать из infrastructure/ напрямую
Grep: "from.*infrastructure" in services/{context}_api/src/{context}_api/api/

# domain/ НЕ должен импортировать из api/ или infrastructure/
Grep: "from.*api" in services/{context}_api/src/{context}_api/domain/
Grep: "from.*infrastructure" in services/{context}_api/src/{context}_api/domain/
```

### 3. Один Event Loop на сервис

```
ПРАВИЛО: Каждый сервис владеет одним event loop.

Проверить:
- Нет asyncio.run() внутри async функций
- Нет создания новых event loops
- Нет asyncio.get_event_loop().run_until_complete()
```

**Команды проверки:**

```bash
# Поиск проблемных паттернов
Grep: "asyncio.run(" in services/
Grep: "get_event_loop().run" in services/
Grep: "new_event_loop()" in services/

# Допустимо только в main.py на верхнем уровне
```

### 4. Разделение сервисов

```
ПРАВИЛО: Сервисы изолированы и общаются через HTTP.

Проверить:
- Каждый сервис — отдельная директория
- Нет общих импортов между сервисами
- Взаимодействие только через HTTP клиенты
```

**Команды проверки:**

```bash
# Проверка изоляции
# Сервис A не должен импортировать из сервиса B
Grep: "from {context}_data" in services/{context}_api/
Grep: "from {context}_api" in services/{context}_data/

# Должно быть ПУСТО
```

---

## Чек-лист проверки

### Архитектурные принципы

- [ ] **HTTP-only**: Business API использует только HTTP клиенты
- [ ] **Нет SQLAlchemy в business**: Импорты SQLAlchemy только в data сервисах
- [ ] **DDD структура**: Все слои присутствуют и правильно организованы
- [ ] **Разделение**: Сервисы не импортируют друг друга напрямую
- [ ] **Event Loop**: Один event loop на сервис

### Качество кода

- [ ] **DRY**: Нет дублирования кода
- [ ] **KISS**: Решения простые и понятные
- [ ] **YAGNI**: Нет избыточной функциональности

---

## Результат проверки

```markdown
## Проверка архитектуры

### Статус: PASSED / FAILED

### Проверенные принципы

| Принцип | Статус | Комментарий |
|---------|--------|-------------|
| HTTP-only | ✓/✗ | {Комментарий} |
| DDD структура | ✓/✗ | {Комментарий} |
| Один Event Loop | ✓/✗ | {Комментарий} |
| Разделение сервисов | ✓/✗ | {Комментарий} |

### Найденные нарушения

| # | Файл | Строка | Нарушение | Рекомендация |
|---|------|--------|-----------|--------------|
| 1 | {файл} | {строка} | {описание} | {как исправить} |

### Рекомендации

1. {Рекомендация 1}
2. {Рекомендация 2}
```

---

## Критерии прохождения

```
PASSED: Все принципы соблюдены, нет критических нарушений.

FAILED: Есть хотя бы одно нарушение:
- HTTP-only нарушен
- DDD структура нарушена
- Event Loop проблемы
- Сервисы не изолированы
```

---

## Источники

| Документ | Описание |
|----------|----------|
| `knowledge/architecture/improved-hybrid.md` | Гибридная архитектура |
| `knowledge/architecture/ddd-hexagonal.md` | DDD принципы |
| `knowledge/architecture/data-access.md` | HTTP-only доступ |
| `knowledge/quality/dry-kiss-yagni.md` | Принципы качества |
