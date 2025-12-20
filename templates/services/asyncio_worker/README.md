# {context}_worker — Background Worker сервис

> **Тип**: Background Worker (asyncio)
> **Назначение**: Фоновые задачи и периодические операции

---

## Описание

Background Worker на asyncio для выполнения фоновых задач.
Поддерживает периодические задачи и graceful shutdown.

---

## Структура

```
{context}_worker/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py                 # Точка входа
│   ├── tasks/                  # Задачи
│   │   ├── __init__.py
│   │   ├── base.py             # Базовый класс задачи
│   │   └── {domain}_tasks.py   # Задачи домена
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   └── http/
│   │       └── api_client.py   # Клиент Business API
│   └── core/
│       ├── __init__.py
│       ├── config.py           # Конфигурация
│       ├── logging.py          # Настройка логирования
│       └── scheduler.py        # Планировщик задач
└── tests/
    ├── __init__.py
    └── conftest.py
```

---

## Переменные для замены

| Переменная | Описание | Пример |
|------------|----------|--------|
| `{context}` | Контекст проекта | `booking`, `ecommerce` |
| `{domain}` | Домен задачи | `notification`, `sync` |

---

## Быстрый старт

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск воркера
python -m src.main

# Запуск тестов
pytest tests/ -v
```

---

## Конфигурация

Переменные окружения (`.env`):

```bash
# Business API
BUSINESS_API_URL=http://business-api:8000
BUSINESS_API_TIMEOUT=30

# Задачи
TASK_INTERVAL_SECONDS=60

# Логирование
LOG_LEVEL=INFO
```

---

## Зависимости

- httpx
- pydantic-settings
- structlog

---

## Чек-лист

- [ ] Заменить `{context}` на название проекта
- [ ] Реализовать задачи в `tasks/`
- [ ] Настроить интервалы выполнения
- [ ] Добавить graceful shutdown
- [ ] Добавить тесты
