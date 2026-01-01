# Отчёт: Реализация Reverse Proxy + root_path Best Practice

> **Статус**: ВЫПОЛНЕНО
> **Дата выполнения**: 2026-01-01
> **Тип**: Enhancement (улучшение фреймворка)
> **Источник**: `contributors/2025-12-31-aidd-enhancement-reverse-proxy-root-path.md`

---

## Описание задачи

Внедрение поддержки работы FastAPI сервисов за nginx reverse proxy с путевыми
префиксами (multi-service deployment на одном IP).

### Проблема

При развёртывании нескольких сервисов на одном IP с разными путевыми префиксами
(`/service-a/`, `/service-b/`) nginx с rewrite ломал StaticFiles mounts в FastAPI.

### Решение

**Best Practice:** nginx БЕЗ rewrite + FastAPI с `root_path` из env переменной.

---

## Выполненные изменения

### 1. Создан новый файл

| Файл | Описание |
|------|----------|
| `templates/infrastructure/nginx/conf.d/service-location.conf.template` | Шаблон nginx location БЕЗ rewrite с поддержкой X-Forwarded-Prefix и WebSocket |

### 2. Модифицированы шаблоны FastAPI сервисов

#### Business API
| Файл | Изменение |
|------|-----------|
| `templates/services/fastapi_business_api/src/core/config.py` | Добавлено поле `root_path: str = ""` в класс Settings |
| `templates/services/fastapi_business_api/src/main.py` | Добавлено `root_path=settings.root_path` в конструктор FastAPI() |

#### PostgreSQL Data API
| Файл | Изменение |
|------|-----------|
| `templates/services/postgres_data_api/src/core/config.py` | Добавлено поле `root_path: str = ""` в класс Settings |
| `templates/services/postgres_data_api/src/main.py` | Добавлено `root_path=settings.root_path` в конструктор FastAPI() |

#### MongoDB Data API
| Файл | Изменение |
|------|-----------|
| `templates/services/mongo_data_api/src/core/config.py` | Добавлено поле `root_path: str = ""` в класс Settings |
| `templates/services/mongo_data_api/src/main.py` | Добавлено `root_path=settings.root_path` в конструктор FastAPI() |

### 3. Обновлена конфигурация проекта

| Файл | Изменение |
|------|-----------|
| `templates/project/.env.example.template` | Добавлена секция REVERSE PROXY CONFIGURATION с переменной ROOT_PATH |

### 4. Обновлена документация

| Файл | Изменение |
|------|-----------|
| `knowledge/infrastructure/nginx.md` | Добавлена секция "Работа с путевыми префиксами (Multi-Service на одном IP)" с примерами и диаграммой |
| `conventions.md` | Добавлена секция 9.3 "Reverse Proxy (root_path)" с правилами и примерами кода |

### 5. Обновлён исходный документ enhancement

| Файл | Изменение |
|------|-----------|
| `contributors/2025-12-31-aidd-enhancement-reverse-proxy-root-path.md` | Статус всех файлов обновлён на ✅ Done, статус "Реализация в фреймворке" = ✅ Завершено |

---

## Сводная таблица изменений

| # | Файл | Действие | Статус |
|---|------|----------|--------|
| 1 | `templates/infrastructure/nginx/conf.d/service-location.conf.template` | Создан | ✅ |
| 2 | `templates/services/fastapi_business_api/src/core/config.py` | Изменён | ✅ |
| 3 | `templates/services/fastapi_business_api/src/main.py` | Изменён | ✅ |
| 4 | `templates/services/postgres_data_api/src/core/config.py` | Изменён | ✅ |
| 5 | `templates/services/postgres_data_api/src/main.py` | Изменён | ✅ |
| 6 | `templates/services/mongo_data_api/src/core/config.py` | Изменён | ✅ |
| 7 | `templates/services/mongo_data_api/src/main.py` | Изменён | ✅ |
| 8 | `templates/project/.env.example.template` | Изменён | ✅ |
| 9 | `knowledge/infrastructure/nginx.md` | Изменён | ✅ |
| 10 | `conventions.md` | Изменён | ✅ |
| 11 | `contributors/2025-12-31-aidd-enhancement-reverse-proxy-root-path.md` | Изменён | ✅ |
| 12 | `templates/infrastructure/nginx/nginx.conf` | Рефакторинг | ✅ |
| 13 | `templates/infrastructure/nginx/conf.d/upstream.conf` | Рефакторинг | ✅ |
| 14 | `templates/infrastructure/nginx/conf.d/api-gateway.conf` | Рефакторинг | ✅ |

**Итого:** 1 новый файл, 13 изменённых файлов

---

## Обратная совместимость

- `ROOT_PATH=""` по умолчанию — существующие проекты работают без изменений
- Для активации: установить `ROOT_PATH=/my-service` в `.env`

---

## Дополнительные изменения: Рефакторинг nginx (Strategy B)

После внедрения reverse proxy поддержки был проведён рефакторинг nginx конфигурации
для устранения конфликтов и дублирования.

### Проблемы до рефакторинга

| Проблема | Описание |
|----------|----------|
| Дублирование upstream | nginx.conf и upstream.conf оба определяли upstream |
| Разное именование | `{context}-api` vs `{context}_api` (dash vs underscore) |
| Location вне server | api-gateway.conf содержал locations без server block |
| Дублирование rate limit zones | Определены в nginx.conf и api-gateway.conf |

### Выбранная стратегия: B (Модульная архитектура)

```
nginx.conf (base)
    ├── include upstream.conf     (определения backend-серверов)
    └── include api-gateway.conf  (server block с locations)
```

### Выполненные изменения

| Файл | Изменение |
|------|-----------|
| `nginx.conf` | Оставлены только базовые настройки http, добавлены include |
| `upstream.conf` | Унифицированы имена контейнеров: `{context}-api` (дефисы) |
| `api-gateway.conf` | Добавлен server block, locations обёрнуты в server |

### Результат

- **Единый источник upstream** — только в upstream.conf
- **Единый источник rate limits** — только в api-gateway.conf
- **Консистентное именование** — везде `{context}-api` с дефисами
- **Правильная структура** — locations внутри server block

---

## Следующие шаги (не входят в этот отчёт)

| Задача | Статус |
|--------|--------|
| Миграция free-ai-selector | ⏳ Ожидает |
| Миграция других существующих сервисов | ⏳ Ожидает |

---

## Ссылки

- Исходный документ: `contributors/2025-12-31-aidd-enhancement-reverse-proxy-root-path.md`
- Документация: `knowledge/infrastructure/nginx.md` (секция "Работа с путевыми префиксами")
- Соглашения: `conventions.md` (секция 9.3)

---

*Отчёт сгенерирован: 2026-01-01*
*Обновлён: 2026-01-01 (добавлен рефакторинг nginx)*
*Исполнитель: AI Agent (Claude Code)*
