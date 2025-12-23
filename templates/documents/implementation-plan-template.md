---
# === YAML Frontmatter (машиночитаемые метаданные) ===
feature_id: "{FID}"
feature_name: "{slug}"
title: "Implementation Plan: {Название фичи/проекта}"
created: "{YYYY-MM-DD}"
author: "AI (Architect)"
type: "plan"
status: "PLAN_APPROVED"
version: 1
mode: "CREATE"

# Ссылки на связанные артефакты
prd_ref: "prd/{YYYY-MM-DD}_{FID}_{slug}-prd.md"
research_ref: "research/{YYYY-MM-DD}_{FID}_{slug}-research.md"
architecture_ref: "architecture/{YYYY-MM-DD}_{FID}_{slug}-architecture.md"

# Сервисы для создания
services:
  - "{context}_api"
  - "{context}_data"

# Опционально
approved_by: null
approved_at: null
stages_count: 0
tasks_count: 0
---

# План реализации: {Название фичи/проекта}

**Feature ID**: {FID}
**Версия**: 1.0
**Дата**: {YYYY-MM-DD}
**Автор**: AI Agent (Архитектор)
**Статус**: Draft | Review | Approved
**Связанный PRD**: {prd-name}-prd.md
**Архитектура**: {architecture-name}.md

---

## 1. Обзор

### 1.1 Цель

{Краткое описание что будет реализовано}

### 1.2 Scope

**В scope:**
- {Что включено 1}
- {Что включено 2}
- {Что включено 3}

**Вне scope:**
- {Что исключено 1}
- {Что исключено 2}

### 1.3 Зависимости

| Зависимость | Тип | Статус |
|-------------|-----|--------|
| {Зависимость 1} | Блокирующая | Ready/Pending |
| {Зависимость 2} | Желательная | Ready/Pending |

---

## 2. Этапы реализации

### Stage 4.1: Инфраструктура

**Цель**: Подготовить базовую инфраструктуру проекта

**Задачи**:

| # | Задача | Файлы | Требование |
|---|--------|-------|------------|
| 4.1.1 | Создать структуру проекта | Все директории | — |
| 4.1.2 | Настроить docker-compose.yml | docker-compose.yml | — |
| 4.1.3 | Создать .env.example | .env.example | — |
| 4.1.4 | Настроить CI pipeline | .github/workflows/ci.yml | — |
| 4.1.5 | Создать Makefile | Makefile | — |

**Критерии завершения**:
- [ ] `docker compose up` запускается без ошибок
- [ ] Все сервисы проходят health check
- [ ] CI pipeline проходит

---

### Stage 4.2: Data API

**Цель**: Реализовать доступ к данным через HTTP API

**Задачи**:

| # | Задача | Файлы | Требование |
|---|--------|-------|------------|
| 4.2.1 | Создать SQLAlchemy модели | domain/entities/*.py | FR-001 |
| 4.2.2 | Настроить Alembic миграции | alembic/versions/*.py | — |
| 4.2.3 | Реализовать репозитории | repositories/*.py | — |
| 4.2.4 | Создать CRUD endpoints | api/v1/*.py | FR-001-004 |
| 4.2.5 | Написать тесты | tests/unit/*.py | — |

**Модели данных**:

```python
# {Entity} модель
class {Entity}(Base):
    __tablename__ = "{entities}"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    {field_1}: Mapped[str] = mapped_column(String(255))
    {field_2}: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())
```

**Endpoints**:

```
GET    /api/v1/{entities}           → List с пагинацией
POST   /api/v1/{entities}           → Create
GET    /api/v1/{entities}/{id}      → Get by ID
PUT    /api/v1/{entities}/{id}      → Update
DELETE /api/v1/{entities}/{id}      → Delete
```

**Критерии завершения**:
- [ ] Миграции применяются успешно
- [ ] Все CRUD операции работают
- [ ] Тесты проходят с coverage ≥ 75%

---

### Stage 4.3: Business API

**Цель**: Реализовать бизнес-логику

**Задачи**:

| # | Задача | Файлы | Требование |
|---|--------|-------|------------|
| 4.3.1 | Создать HTTP клиент для Data API | infrastructure/http/data_client.py | — |
| 4.3.2 | Реализовать доменные сервисы | domain/services/*.py | FR-* |
| 4.3.3 | Реализовать application services | application/services/*.py | FR-* |
| 4.3.4 | Создать API endpoints | api/v1/*.py | FR-* |
| 4.3.5 | Добавить валидацию | schemas/*.py | — |
| 4.3.6 | Написать тесты | tests/*.py | — |

**Бизнес-логика**:

```python
# {UseCase} use case
class {UseCase}Service:
    def __init__(self, data_client: DataAPIClient):
        self._data_client = data_client

    async def execute(self, request: {UseCase}Request) -> {UseCase}Response:
        # 1. Валидация бизнес-правил
        # 2. Выполнение операции
        # 3. Возврат результата
        pass
```

**Критерии завершения**:
- [ ] Business API взаимодействует с Data API
- [ ] Бизнес-правила реализованы
- [ ] API документация сгенерирована (OpenAPI)
- [ ] Тесты проходят

---

### Stage 4.4: Background Worker (если требуется)

**Цель**: Реализовать фоновые задачи

**Задачи**:

| # | Задача | Файлы | Требование |
|---|--------|-------|------------|
| 4.4.1 | Создать базовый воркер | main.py, scheduler.py | — |
| 4.4.2 | Реализовать задачи | tasks/*.py | FR-* |
| 4.4.3 | Настроить graceful shutdown | — | — |

**Критерии завершения**:
- [ ] Воркер запускается и останавливается корректно
- [ ] Задачи выполняются по расписанию

---

### Stage 4.5: Telegram Bot (если требуется)

**Цель**: Реализовать Telegram интерфейс

**Задачи**:

| # | Задача | Файлы | Требование |
|---|--------|-------|------------|
| 4.5.1 | Настроить бота | main.py, bot/ | — |
| 4.5.2 | Реализовать handlers | handlers/*.py | UI-* |
| 4.5.3 | Добавить FSM (если нужно) | states/*.py | — |
| 4.5.4 | Создать клавиатуры | keyboards/*.py | UI-* |

**Критерии завершения**:
- [ ] Бот отвечает на /start
- [ ] Основные сценарии работают

---

### Stage 4.6: Тестирование

**Цель**: Обеспечить качество кода

**Задачи**:

| # | Задача | Файлы | Покрытие |
|---|--------|-------|----------|
| 4.6.1 | Unit тесты Data API | tests/unit/*.py | ≥ 75% |
| 4.6.2 | Unit тесты Business API | tests/unit/*.py | ≥ 75% |
| 4.6.3 | Integration тесты | tests/integration/*.py | Key flows |
| 4.6.4 | E2E тесты (опционально) | tests/e2e/*.py | Happy path |

**Критерии завершения**:
- [ ] Coverage ≥ 75% для каждого сервиса
- [ ] Все тесты проходят в CI
- [ ] Критические пути покрыты

---

## 3. Порядок выполнения

```
Stage 4.1 (Инфраструктура)
    │
    ▼
Stage 4.2 (Data API)
    │
    ├──────────────────┐
    ▼                  ▼
Stage 4.3          Stage 4.4/4.5
(Business API)     (Worker/Bot)
    │                  │
    └────────┬─────────┘
             ▼
      Stage 4.6 (Тесты)
```

---

## 4. Файлы для создания

### 4.1 Data API ({context}_data)

```
services/{context}_data/
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 001_initial.py
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       └── {entities}.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── logging.py
│   ├── domain/
│   │   ├── __init__.py
│   │   └── entities/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       └── {entity}.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── {entity}_repository.py
│   └── schemas/
│       ├── __init__.py
│       └── {entity}.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── unit/
        └── test_{entity}_repository.py
```

### 4.2 Business API ({context}_api)

```
services/{context}_api/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       └── {domain}.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   └── {use_case}_service.py
│   │   └── dtos/
│   │       └── {domain}.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   ├── value_objects/
│   │   └── services/
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   └── http/
│   │       ├── __init__.py
│   │       └── data_client.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   └── schemas/
│       └── {domain}.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── unit/
        └── test_{use_case}_service.py
```

---

## 5. Трассировка требований

| Требование | Stage | Задача | Файл | Тест |
|------------|-------|--------|------|------|
| FR-001 | 4.2 | 4.2.1, 4.2.4 | entities.py | test_*.py |
| FR-002 | 4.3 | 4.3.3, 4.3.4 | service.py | test_*.py |
| NF-001 | 4.6 | 4.6.3 | — | integration |

---

## 6. Риски реализации

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| {Риск 1} | Medium | High | {Действие} |
| {Риск 2} | Low | Medium | {Действие} |

---

## Качественные ворота

### IMPLEMENTATION_READY Checklist

- [ ] Все этапы определены
- [ ] Задачи детализированы
- [ ] Файлы для создания перечислены
- [ ] Требования трассируются к задачам
- [ ] Порядок выполнения определён
- [ ] Критерии завершения каждого этапа ясны
