# Функция: Создание Implementation Plan

> **Назначение**: Формирование плана реализации для Реализатора.

---

## Цель

Создать детальный план реализации, который Реализатор
может выполнить последовательно, этап за этапом.

---

## Структура Implementation Plan

```markdown
# Implementation Plan: {Название проекта}

**Версия**: 1.0
**Дата**: {YYYY-MM-DD}
**Автор**: AI Agent (Архитектор)
**Режим**: CREATE | FEATURE

---

## 1. Обзор

### 1.1 Цель реализации
{Что будет создано}

### 1.2 Компоненты
{Список компонентов для реализации}

### 1.3 Зависимости
{Внешние зависимости}

---

## 2. Этапы реализации

### Stage 4.1: Инфраструктура

| # | Задача | Файлы | Зависит от |
|---|--------|-------|------------|
| 4.1.1 | Создать структуру проекта | — | — |
| 4.1.2 | Создать docker-compose.yml | docker-compose.yml | 4.1.1 |
| 4.1.3 | Создать .env.example | .env.example | 4.1.1 |
| 4.1.4 | Создать Makefile | Makefile | 4.1.2 |
| 4.1.5 | Создать CI pipeline | .github/workflows/ci.yml | 4.1.1 |

### Stage 4.2: Data Service

| # | Задача | Файлы | Зависит от |
|---|--------|-------|------------|
| 4.2.1 | Создать структуру сервиса | services/{context}_data/ | 4.1.1 |
| 4.2.2 | Создать Dockerfile | Dockerfile | 4.2.1 |
| 4.2.3 | Создать модели | domain/entities/ | 4.2.1 |
| 4.2.4 | Создать репозитории | infrastructure/repositories/ | 4.2.3 |
| 4.2.5 | Создать API роуты | api/v1/ | 4.2.4 |
| 4.2.6 | Создать main.py | main.py | 4.2.5 |

### Stage 4.3: Business API

| # | Задача | Файлы | Зависит от |
|---|--------|-------|------------|
| 4.3.1 | Создать структуру сервиса | services/{context}_api/ | 4.1.1 |
| 4.3.2 | Создать Dockerfile | Dockerfile | 4.3.1 |
| 4.3.3 | Создать HTTP клиент | infrastructure/http/ | 4.3.1 |
| 4.3.4 | Создать сервисы | application/services/ | 4.3.3 |
| 4.3.5 | Создать схемы | schemas/ | 4.3.1 |
| 4.3.6 | Создать API роуты | api/v1/ | 4.3.4, 4.3.5 |
| 4.3.7 | Создать main.py | main.py | 4.3.6 |

### Stage 4.4: Telegram Bot (если нужен)

| # | Задача | Файлы | Зависит от |
|---|--------|-------|------------|
| 4.4.1 | Создать структуру сервиса | services/{context}_bot/ | 4.1.1 |
| 4.4.2 | Создать Dockerfile | Dockerfile | 4.4.1 |
| 4.4.3 | Создать HTTP клиент | infrastructure/http/ | 4.4.1 |
| 4.4.4 | Создать handlers | handlers/ | 4.4.3 |
| 4.4.5 | Создать keyboards | keyboards/ | 4.4.1 |
| 4.4.6 | Создать states | states/ | 4.4.1 |
| 4.4.7 | Создать main.py | main.py | 4.4.4, 4.4.5, 4.4.6 |

### Stage 4.5: Background Worker (если нужен)

| # | Задача | Файлы | Зависит от |
|---|--------|-------|------------|
| 4.5.1 | Создать структуру сервиса | services/{context}_worker/ | 4.1.1 |
| 4.5.2 | Создать Dockerfile | Dockerfile | 4.5.1 |
| 4.5.3 | Создать task handlers | tasks/ | 4.5.1 |
| 4.5.4 | Создать scheduler | scheduler.py | 4.5.3 |
| 4.5.5 | Создать main.py | main.py | 4.5.4 |

### Stage 4.6: Тестирование

| # | Задача | Файлы | Зависит от |
|---|--------|-------|------------|
| 4.6.1 | Создать conftest.py | tests/conftest.py | 4.2-4.5 |
| 4.6.2 | Unit тесты Data Service | tests/unit/ | 4.2.6 |
| 4.6.3 | Unit тесты Business API | tests/unit/ | 4.3.7 |
| 4.6.4 | Integration тесты | tests/integration/ | 4.6.2, 4.6.3 |

---

## 3. Трассировка требований

| Req ID | Описание | Этап | Файлы |
|--------|----------|------|-------|
| FR-001 | {Описание} | 4.3.6 | api/v1/routes.py |
| FR-002 | {Описание} | 4.2.5 | api/v1/routes.py |

---

## 4. Шаблоны для использования

| Компонент | Шаблон |
|-----------|--------|
| Business API | templates/services/fastapi_business_api/ |
| Data API | templates/services/postgres_data_api/ |
| Telegram Bot | templates/services/aiogram_bot/ |
| Worker | templates/services/asyncio_worker/ |

---

## 5. Переменные окружения

| Переменная | Сервис | Описание |
|------------|--------|----------|
| DATABASE_URL | Data API | Подключение к PostgreSQL |
| DATA_API_URL | Business API | URL Data API |
| BOT_TOKEN | Bot | Токен Telegram бота |

---

## Качественные ворота: PLAN_APPROVED

- [ ] Все этапы определены
- [ ] Зависимости между задачами указаны
- [ ] Все FR покрыты в трассировке
- [ ] Шаблоны указаны для всех компонентов
- [ ] Переменные окружения определены
```

---

## Правила формирования плана

### 1. Порядок этапов

```
ПРАВИЛО: Этапы выполняются строго последовательно.

4.1 Инфраструктура → всегда первый
4.2 Data Service → до Business API
4.3 Business API → после Data Service
4.4 Bot / 4.5 Worker → после Business API
4.6 Тесты → последний этап
```

### 2. Зависимости

```
ПРАВИЛО: Каждая задача указывает зависимости.

Пример:
- 4.2.5 (API роуты) зависит от 4.2.4 (репозитории)
- 4.3.4 (сервисы) зависит от 4.3.3 (HTTP клиент)
```

### 3. Трассировка

```
ПРАВИЛО: Каждое FR должно быть покрыто хотя бы одной задачей.

FR-001 → 4.3.6 (API роуты Business API)
FR-002 → 4.2.5 (API роуты Data API)
```

### 4. Шаблоны

```
ПРАВИЛО: Для каждого компонента указать шаблон.

Business API → templates/services/fastapi_business_api/
Data API PG → templates/services/postgres_data_api/
```

---

## Режим FEATURE

Для добавления функциональности план упрощается:

```markdown
# Feature Implementation Plan: {Название фичи}

## 1. Изменения в существующих сервисах

### Data Service

| # | Задача | Файлы |
|---|--------|-------|
| 1.1 | Добавить модель | domain/entities/new_entity.py |
| 1.2 | Добавить миграцию | migrations/ |
| 1.3 | Добавить репозиторий | infrastructure/repositories/ |
| 1.4 | Добавить эндпоинты | api/v1/new_routes.py |

### Business API

| # | Задача | Файлы |
|---|--------|-------|
| 2.1 | Обновить HTTP клиент | infrastructure/http/client.py |
| 2.2 | Добавить сервис | application/services/new_service.py |
| 2.3 | Добавить эндпоинты | api/v1/new_routes.py |

## 2. Новые тесты

| # | Задача | Файлы |
|---|--------|-------|
| 3.1 | Unit тесты | tests/unit/test_new_feature.py |
| 3.2 | Integration тесты | tests/integration/test_new_feature.py |
```

---

## Путь сохранения

```
ai-docs/docs/plans/{name}-implementation-plan.md

Примеры:
- ai-docs/docs/plans/booking-implementation-plan.md
- ai-docs/docs/plans/notifications-feature-plan.md
```

---

## Источники

| Документ | Описание |
|----------|----------|
| `workflow.md` | Описание этапов |
| `knowledge/architecture/project-structure.md` | Структура проекта |
| `roles/implementer/` | Инструкции Реализатора |
