# Архитектурный план: {Название проекта}

**Версия**: 1.0
**Дата**: {YYYY-MM-DD}
**Автор**: AI Agent (Архитектор)
**Статус**: Draft | Review | Approved
**Связанный PRD**: {prd-name}-prd.md

---

## 1. Обзор архитектуры

### 1.1 Архитектурный стиль

- **Основной паттерн**: Hexagonal Architecture (Ports & Adapters)
- **Принцип доступа к данным**: HTTP-only (Data API)
- **Уровень зрелости**: Level 2 (MVP)

### 1.2 Высокоуровневая диаграмма

```
┌─────────────────────────────────────────────────────────────────┐
│                         Клиенты                                  │
│  [Web App]  [Mobile App]  [Telegram Bot]  [External Systems]    │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (Nginx)                         │
│              Rate Limiting, SSL Termination                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
│  {context}_api  │ │  {bot}_bot  │ │ {worker}_worker │
│  Business API   │ │ Telegram Bot│ │ Background Jobs │
│    (FastAPI)    │ │  (Aiogram)  │ │   (asyncio)     │
└────────┬────────┘ └──────┬──────┘ └────────┬────────┘
         │                 │                  │
         └─────────────────┼──────────────────┘
                           │ HTTP
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    {context}_data                                │
│                    Data API (FastAPI)                            │
│              Repository Pattern, CRUD Operations                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │ SQL
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       PostgreSQL                                 │
│                     Primary Database                             │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Ключевые решения

| Аспект | Решение | Обоснование |
|--------|---------|-------------|
| Доступ к данным | HTTP-only через Data API | Изоляция, независимый scaling |
| Аутентификация | JWT tokens | Stateless, масштабируемость |
| Коммуникация | Синхронная HTTP | Простота для MVP |
| Логирование | structlog JSON | Структурированность, ELK ready |

---

## 2. Компоненты системы

### 2.1 Сервисы

#### {context}_api — Business API

**Назначение**: Основной API для бизнес-логики

**Технологии**:
- FastAPI 0.100+
- Python 3.11+
- httpx (HTTP client)

**Структура**:
```
{context}_api/
├── src/
│   ├── api/                 # Endpoints
│   │   ├── v1/
│   │   │   ├── router.py
│   │   │   └── {domain}.py
│   │   └── dependencies.py
│   ├── application/         # Use cases
│   │   ├── services/
│   │   └── dtos/
│   ├── domain/              # Business logic
│   │   ├── entities/
│   │   ├── value_objects/
│   │   └── services/
│   ├── infrastructure/      # External adapters
│   │   └── http/
│   ├── core/                # Config, logging
│   └── main.py
└── tests/
```

**Endpoints**:

| Method | Path | Описание | Требование |
|--------|------|----------|------------|
| GET | /api/v1/{entities} | Список сущностей | FR-001 |
| POST | /api/v1/{entities} | Создание | FR-002 |
| GET | /api/v1/{entities}/{id} | Получение по ID | FR-001 |
| PUT | /api/v1/{entities}/{id} | Обновление | FR-003 |
| DELETE | /api/v1/{entities}/{id} | Удаление | FR-004 |

---

#### {context}_data — Data API

**Назначение**: Единая точка доступа к данным

**Технологии**:
- FastAPI 0.100+
- SQLAlchemy 2.0+ (async)
- Alembic (migrations)
- asyncpg

**Структура**:
```
{context}_data/
├── src/
│   ├── api/
│   │   └── v1/
│   ├── domain/
│   │   └── entities/       # SQLAlchemy models
│   ├── repositories/       # Data access
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   └── main.py
├── alembic/
│   └── versions/
└── tests/
```

---

### 2.2 Базы данных

#### PostgreSQL

**Версия**: 15+

**Схема данных**:

```sql
-- Пример таблицы
CREATE TABLE {entities} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    {field_1} VARCHAR(255) NOT NULL,
    {field_2} TEXT,
    {field_3} INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_{entities}_{field_1} ON {entities}({field_1});
CREATE INDEX idx_{entities}_created_at ON {entities}(created_at);
```

**ER-диаграмма**:

```
┌─────────────────┐       ┌─────────────────┐
│    {entity_1}   │       │    {entity_2}   │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │──┐    │ id (PK)         │
│ name            │  │    │ {entity_1}_id(FK)│──┐
│ ...             │  └────│ ...             │  │
│ created_at      │       │ created_at      │  │
└─────────────────┘       └─────────────────┘  │
                                               │
                          ┌─────────────────┐  │
                          │    {entity_3}   │  │
                          ├─────────────────┤  │
                          │ id (PK)         │  │
                          │ {entity_2}_id(FK)│◄─┘
                          │ ...             │
                          └─────────────────┘
```

---

### 2.3 Инфраструктура

| Компонент | Технология | Назначение |
|-----------|-----------|------------|
| Reverse Proxy | Nginx | SSL, Rate Limiting |
| Containerization | Docker | Изоляция сервисов |
| Orchestration | Docker Compose | Локальная разработка |
| CI/CD | GitHub Actions | Автоматизация |
| Registry | GHCR | Docker images |

---

## 3. API контракты

### 3.1 Общие соглашения

- **Формат**: JSON
- **Версионирование**: URL path (/api/v1/)
- **Аутентификация**: Bearer JWT token
- **Пагинация**: page + page_size
- **Сортировка**: sort_by + sort_order

### 3.2 Формат ответов

**Успешный ответ (единичный объект)**:
```json
{
  "id": "uuid",
  "field_1": "value",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Успешный ответ (список с пагинацией)**:
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

**Ответ с ошибкой**:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Ресурс не найден",
    "details": {}
  }
}
```

### 3.3 Коды ошибок

| HTTP | Code | Описание |
|------|------|----------|
| 400 | VALIDATION_ERROR | Ошибка валидации |
| 401 | UNAUTHORIZED | Не авторизован |
| 403 | FORBIDDEN | Доступ запрещён |
| 404 | NOT_FOUND | Не найден |
| 409 | CONFLICT | Конфликт |
| 429 | RATE_LIMIT_EXCEEDED | Слишком много запросов |
| 500 | INTERNAL_ERROR | Внутренняя ошибка |

---

## 4. Безопасность

### 4.1 Аутентификация

```
┌──────────┐        ┌──────────┐        ┌──────────┐
│  Client  │──(1)──▶│   API    │──(2)──▶│  Auth    │
│          │◀──(4)──│ Gateway  │◀──(3)──│ Service  │
└──────────┘        └──────────┘        └──────────┘

(1) POST /auth/login {credentials}
(2) Validate credentials
(3) Generate JWT
(4) Return {access_token, refresh_token}
```

### 4.2 Авторизация

- **Модель**: RBAC (Role-Based Access Control)
- **Роли**: admin, user, guest
- **Проверка**: Middleware + Dependencies

### 4.3 Защита данных

| Аспект | Мера |
|--------|------|
| Транспорт | TLS 1.3 |
| Хранение паролей | bcrypt/argon2 |
| Sensitive data | Encryption at rest |
| API keys | Vault/Secrets Manager |

---

## 5. Наблюдаемость

### 5.1 Логирование

- **Формат**: JSON (structlog)
- **Уровни**: DEBUG, INFO, WARNING, ERROR
- **Корреляция**: X-Request-ID

### 5.2 Метрики (Level 3+)

- Request rate
- Response time (p50, p95, p99)
- Error rate
- Database connections
- Cache hit ratio

### 5.3 Health Checks

| Endpoint | Проверки |
|----------|----------|
| /health | Сервис запущен |
| /health/ready | Все зависимости доступны |
| /health/live | Сервис отвечает |

---

## 6. Масштабирование

### 6.1 Стратегия

| Сервис | Тип | Метод |
|--------|-----|-------|
| API | Stateless | Horizontal (replicas) |
| Data API | Stateless | Horizontal (replicas) |
| PostgreSQL | Stateful | Vertical / Read replicas |
| Redis | Stateful | Cluster mode |

### 6.2 Узкие места

| Компонент | Риск | Митигация |
|-----------|------|-----------|
| PostgreSQL | Connection limit | Connection pooling |
| API | CPU bound | Horizontal scaling |
| External API | Rate limits | Caching, queuing |

---

## 7. Deployment

### 7.1 Окружения

| Окружение | Назначение | URL |
|-----------|-----------|-----|
| Development | Локальная разработка | localhost |
| Staging | Тестирование | staging.domain.com |
| Production | Боевой | domain.com |

### 7.2 Конфигурация

Все настройки через переменные окружения:

| Variable | Development | Production |
|----------|-------------|------------|
| DEBUG | true | false |
| LOG_LEVEL | DEBUG | INFO |
| DATABASE_URL | localhost | {secret} |

---

## 8. Трассировка требований

| Требование | Компонент | API | Таблица |
|------------|-----------|-----|---------|
| FR-001 | {context}_api | GET /entities | {entities} |
| FR-002 | {context}_api | POST /entities | {entities} |
| FR-003 | {context}_api | PUT /entities/{id} | {entities} |
| NF-001 | All | — | — |

---

## Качественные ворота

### PLAN_APPROVED Checklist

- [ ] Архитектура соответствует принципам фреймворка
- [ ] Все компоненты определены
- [ ] API контракты специфицированы
- [ ] Схема БД спроектирована
- [ ] Требования к безопасности покрыты
- [ ] Стратегия масштабирования определена
- [ ] Требования трассируются к компонентам
