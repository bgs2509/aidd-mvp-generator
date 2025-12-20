# {context}_data — MongoDB Data API сервис

> **Тип**: Data API (FastAPI + Motor)
> **Назначение**: HTTP API для работы с MongoDB базой данных

---

## Описание

Data API сервис для работы с MongoDB.
Предоставляет CRUD операции через HTTP API.
Используется Business API сервисами по HTTP-only принципу.

---

## Структура

```
{context}_data/
├── Dockerfile
├── requirements.txt
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
│   │   └── models/             # Pydantic модели
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
│       ├── database.py         # Подключение к MongoDB
│       └── logging.py
└── tests/
    ├── __init__.py
    └── conftest.py
```

---

## Переменные для замены

| Переменная | Описание | Пример |
|------------|----------|--------|
| `{context}` | Контекст проекта | `booking`, `analytics` |
| `{domain}` | Домен сущности | `event`, `log`, `metric` |
| `{Domain}` | Домен (PascalCase) | `Event`, `Log`, `Metric` |

---

## Быстрый старт

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск в dev режиме
uvicorn src.main:app --reload --port 8001

# Запуск тестов
pytest tests/ -v
```

---

## Конфигурация

Переменные окружения (`.env`):

```bash
# MongoDB
MONGODB_URL=mongodb://user:pass@localhost:27017
MONGODB_DATABASE={context}_db

# Приложение
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
```

---

## Зависимости

- FastAPI 0.100+
- motor (async MongoDB driver)
- pydantic-settings
- structlog

---

## Чек-лист

- [ ] Заменить `{context}` на название проекта
- [ ] Создать модели в `domain/models/`
- [ ] Создать репозитории в `repositories/`
- [ ] Настроить индексы в `core/database.py`
- [ ] Добавить тесты
