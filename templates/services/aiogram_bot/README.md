# {context}_bot — Telegram Bot сервис

> **Тип**: Telegram Bot (Aiogram 3.x)
> **Назначение**: Telegram бот для взаимодействия с пользователями

---

## Описание

Telegram бот на Aiogram 3.x с FSM для диалогов.
Работает по принципу HTTP-only доступа к данным через Business API.

---

## Структура

```
{context}_bot/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py                 # Точка входа
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── handlers/           # Обработчики сообщений
│   │   │   ├── __init__.py
│   │   │   ├── start.py        # /start, /help
│   │   │   ├── {domain}.py     # Обработчики домена
│   │   │   └── errors.py       # Обработка ошибок
│   │   ├── middlewares/        # Middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # Авторизация
│   │   │   ├── throttling.py   # Rate limiting
│   │   │   └── logging.py      # Логирование
│   │   ├── keyboards/          # Клавиатуры
│   │   │   ├── __init__.py
│   │   │   ├── inline.py       # Inline клавиатуры
│   │   │   └── reply.py        # Reply клавиатуры
│   │   ├── states/             # FSM состояния
│   │   │   ├── __init__.py
│   │   │   └── {domain}.py     # Состояния домена
│   │   └── callbacks/          # Callback данные
│   │       ├── __init__.py
│   │       └── {domain}.py     # Callback домена
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   └── http/
│   │       ├── __init__.py
│   │       └── api_client.py   # Клиент Business API
│   └── core/
│       ├── __init__.py
│       ├── config.py           # Конфигурация
│       └── logging.py          # Настройка логирования
└── tests/
    ├── __init__.py
    └── conftest.py
```

---

## Переменные для замены

| Переменная | Описание | Пример |
|------------|----------|--------|
| `{context}` | Контекст проекта (snake_case) | `booking`, `ecommerce` |
| `{domain}` | Домен сущности | `user`, `order`, `booking` |
| `{Domain}` | Домен сущности (PascalCase) | `User`, `Order`, `Booking` |

---

## Быстрый старт

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск бота
python -m src.main

# Запуск тестов
pytest tests/ -v
```

---

## Конфигурация

Переменные окружения (`.env`):

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# Business API
BUSINESS_API_URL=http://business-api:8000
BUSINESS_API_TIMEOUT=30

# Redis (для FSM)
REDIS_URL=redis://redis:6379/0

# Логирование
LOG_LEVEL=INFO
```

---

## Зависимости

- aiogram>=3.2.0
- httpx
- pydantic-settings
- structlog
- redis (для FSM)

---

## Чек-лист

- [ ] Заменить `{context}` на название проекта
- [ ] Настроить TELEGRAM_BOT_TOKEN
- [ ] Настроить BUSINESS_API_URL
- [ ] Реализовать обработчики в `handlers/`
- [ ] Настроить FSM состояния
- [ ] Добавить тесты
