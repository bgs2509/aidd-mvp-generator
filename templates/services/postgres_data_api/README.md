# {context}_data — PostgreSQL Data API сервис

> **Тип**: Data API (FastAPI + SQLAlchemy)
> **Назначение**: HTTP API для работы с PostgreSQL базой данных

---

## Описание

Data API сервис для работы с PostgreSQL.
Предоставляет CRUD операции через HTTP API.
Используется Business API сервисами по HTTP-only принципу.

---

## Структура

```
{context}_data/
├── Dockerfile
├── requirements.txt
├── alembic.ini                 # Конфигурация Alembic
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/               # Миграции
├── src/
│   ├── __init__.py
│   ├── main.py                 # Точка входа
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   └── {domain}/       # CRUD роутер домена
│   │   └── dependencies.py
│   ├── domain/
│   │   ├── __init__.py
│   │   └── entities/           # SQLAlchemy модели
│   │       ├── __init__.py
│   │       ├── base.py         # Базовая модель
│   │       └── {domain}.py     # Модель домена
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py             # Базовый репозиторий
│   │   └── {domain}_repository.py
│   └── core/
│       ├── __init__.py
│       ├── config.py
│       ├── database.py         # Подключение к БД
│       └── logging.py
└── tests/
    ├── __init__.py
    └── conftest.py
```

---

## Переменные для замены

| Переменная | Описание | Пример |
|------------|----------|--------|
| `{context}` | Контекст проекта | `booking`, `ecommerce` |
| `{domain}` | Домен сущности | `user`, `order` |
| `{Domain}` | Домен (PascalCase) | `User`, `Order` |

---

## Быстрый старт

```bash
# Установка зависимостей
pip install -r requirements.txt

# Миграции
alembic upgrade head

# Запуск в dev режиме
uvicorn src.main:app --reload --port 8001

# Запуск тестов
pytest tests/ -v
```

---

## Конфигурация

Переменные окружения (`.env`):

```bash
# База данных
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/{context}_db

# Приложение
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
```

---

## API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Health check |
| GET | `/api/v1/{domain}s` | Список с пагинацией |
| POST | `/api/v1/{domain}s` | Создание |
| GET | `/api/v1/{domain}s/{id}` | Получение по ID |
| PUT | `/api/v1/{domain}s/{id}` | Обновление |
| DELETE | `/api/v1/{domain}s/{id}` | Удаление |

---

## Зависимости

- FastAPI 0.100+
- SQLAlchemy 2.0+ (async)
- asyncpg
- alembic
- pydantic-settings
- structlog

---

## Чек-лист

- [ ] Заменить `{context}` на название проекта
- [ ] Создать модели в `domain/entities/`
- [ ] Создать репозитории в `repositories/`
- [ ] Создать миграции: `alembic revision --autogenerate`
- [ ] Применить миграции: `alembic upgrade head`
- [ ] Добавить тесты
