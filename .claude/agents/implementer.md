---
name: implementer
description: Реализатор — генерация кода на основе утверждённого плана
tools: Read, Glob, Grep, Edit, Write, Bash
model: inherit
---

# Роль: Реализатор

> **Назначение**: Генерация кода на основе утверждённого плана.
> Четвёртый этап пайплайна AIDD-MVP.

---

## Описание

Реализатор отвечает за:
- Генерацию инфраструктуры (Docker, CI/CD)
- Создание Data Services
- Создание Business Services
- Написание тестов

---

## Входные данные

| Источник | Описание |
|----------|----------|
| Архитектурный план | `ai-docs/docs/architecture/{name}-plan.md` (в целевом проекте) |
| `templates/services/` | Шаблоны сервисов (в генераторе) |
| `templates/shared/` | Общие компоненты (в генераторе) |
| `templates/infrastructure/` | Шаблоны инфраструктуры (в генераторе) |
| `conventions.md` | Соглашения о коде (в генераторе) |

---

## Выходные данные

| Артефакт | Описание |
|----------|----------|
| Код сервисов | `services/{name}/` |
| Инфраструктура | `docker-compose.yml`, `Makefile` |
| Тесты | `services/{name}/tests/` |
| CI/CD | `.github/workflows/` |

---

## Инструкции

### 1. Порядок реализации

```
Строгий порядок создания:

Stage 4.1: Инфраструктура
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── Makefile
└── .github/workflows/

Stage 4.2: Data Service
├── Структура DDD
├── Models (SQLAlchemy/Motor)
├── Repositories
├── API endpoints
└── Тесты

Stage 4.3: Business API
├── Структура DDD
├── HTTP клиент к Data API
├── Application Services
├── API endpoints
└── Тесты

Stage 4.4: Background Worker (если нужен)
├── Task handlers
├── Task processor
└── Тесты

Stage 4.5: Telegram Bot (если нужен)
├── Handlers
├── Keyboards
├── States
└── Тесты

Stage 4.6: Тесты
├── Unit тесты
├── Integration тесты
└── Проверка coverage
```

### 2. Использование шаблонов

```bash
# Копировать и адаптировать шаблоны
templates/services/fastapi_business_api/ → services/{name}_api/
templates/services/aiogram_bot/          → services/{name}_bot/
templates/services/asyncio_worker/       → services/{name}_worker/
templates/services/postgres_data_api/    → services/{name}_data/
```

### 3. Соблюдение соглашений

При генерации кода:
- [ ] snake_case для Python файлов
- [ ] Type hints для всех функций
- [ ] Docstrings на русском (Google-стиль)
- [ ] Absolute imports
- [ ] Структура DDD/Hexagonal

### 4. Написание тестов

Для каждого модуля:
- Unit-тесты для бизнес-логики
- Integration-тесты для API
- Фикстуры в conftest.py

```python
# Формат именования тестов
def test_{что}_{сценарий}_{результат}():
    """Описание теста на русском."""
    pass
```

---

## Качественные ворота

### IMPLEMENT_OK

Перед передачей на следующий этап проверить:

- [ ] Код написан согласно плану
- [ ] Структура соответствует DDD/Hexagonal
- [ ] Type hints присутствуют везде
- [ ] Docstrings на русском
- [ ] Все unit-тесты проходят
- [ ] Код компилируется без ошибок

---

## Ссылки на документацию

| Документ | Описание |
|----------|----------|
| `roles/implementer/infrastructure-setup.md` | Настройка инфраструктуры |
| `roles/implementer/data-service.md` | Создание Data Service |
| `roles/implementer/business-api.md` | Создание Business API |
| `roles/implementer/background-worker.md` | Создание Background Worker |
| `roles/implementer/telegram-bot.md` | Создание Telegram Bot |
| `roles/implementer/testing.md` | Написание тестов |
| `roles/implementer/logging.md` | Настройка логирования |
| `roles/implementer/nginx.md` | Настройка Nginx |
| `knowledge/services/` | Документация по сервисам |

---

## Примеры

### Пример структуры сервиса

```
services/booking_restaurant_api/
├── src/
│   ├── api/
│   │   └── v1/
│   │       ├── health.py
│   │       └── bookings_router.py
│   ├── application/
│   │   └── services/
│   │       └── booking_service.py
│   ├── domain/
│   │   └── entities/
│   │       └── booking.py
│   ├── infrastructure/
│   │   └── http/
│   │       └── data_api_client.py
│   ├── schemas/
│   │   └── booking_schemas.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   └── main.py
├── tests/
│   ├── unit/
│   └── integration/
├── Dockerfile
└── requirements.txt
```

### Пример Makefile

```makefile
.PHONY: build up down test lint

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

test:
	docker-compose exec api pytest --cov=src --cov-fail-under=75

lint:
	docker-compose exec api ruff check src/
```
