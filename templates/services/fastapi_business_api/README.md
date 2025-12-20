# {context}_api — Business API сервис

> **Тип**: Business API (FastAPI)
> **Назначение**: HTTP API для бизнес-логики

---

## Описание

Business API сервис на FastAPI, реализующий бизнес-логику приложения.
Работает по принципу HTTP-only доступа к данным через Data API.

---

## Структура

```
{context}_api/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py                 # Точка входа
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # Главный роутер v1
│   │   │   ├── health.py       # Health check
│   │   │   └── {domain}/       # Домен (users, orders, etc.)
│   │   │       ├── __init__.py
│   │   │       ├── router.py
│   │   │       └── schemas.py
│   │   └── dependencies.py     # DI зависимости
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services/           # Сервисы приложения
│   │   │   └── {domain}_service.py
│   │   └── dtos/               # Data Transfer Objects
│   │       └── {domain}_dto.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/           # Доменные сущности
│   │   ├── value_objects/      # Value Objects
│   │   └── services/           # Доменные сервисы
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── http/               # HTTP клиенты
│   │   │   ├── __init__.py
│   │   │   ├── base_client.py
│   │   │   └── data_api_client.py
│   │   └── cache/              # Кэширование
│   │       └── redis_client.py
│   └── core/
│       ├── __init__.py
│       ├── config.py           # Конфигурация
│       ├── logging.py          # Настройка логирования
│       └── exceptions.py       # Кастомные исключения
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    └── integration/
```

---

## Переменные для замены

| Переменная | Описание | Пример |
|------------|----------|--------|
| `{context}` | Контекст проекта (snake_case) | `booking`, `ecommerce` |
| `{domain}` | Домен сущности | `user`, `order`, `product` |
| `{Domain}` | Домен сущности (PascalCase) | `User`, `Order`, `Product` |
| `{CONTEXT}` | Контекст (UPPER_CASE) | `BOOKING`, `ECOMMERCE` |

---

## Быстрый старт

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск в dev режиме
uvicorn src.main:app --reload --port 8000

# Запуск тестов
pytest tests/ -v
```

---

## Конфигурация

Переменные окружения (`.env`):

```bash
# Приложение
APP_NAME={context}_api
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Data API
DATA_API_URL=http://data-api:8001
DATA_API_TIMEOUT=30

# Redis (опционально)
REDIS_URL=redis://redis:6379/0
```

---

## API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Health check |
| GET | `/api/v1/{domain}s` | Список сущностей |
| POST | `/api/v1/{domain}s` | Создание сущности |
| GET | `/api/v1/{domain}s/{id}` | Получение по ID |
| PUT | `/api/v1/{domain}s/{id}` | Обновление |
| DELETE | `/api/v1/{domain}s/{id}` | Удаление |

---

## Зависимости

- FastAPI 0.100+
- httpx (HTTP клиент)
- pydantic-settings
- structlog
- redis (опционально)

---

## Чек-лист

- [ ] Заменить `{context}` на название проекта
- [ ] Заменить `{domain}` на название домена
- [ ] Настроить `.env`
- [ ] Реализовать бизнес-логику в `application/services/`
- [ ] Добавить тесты
