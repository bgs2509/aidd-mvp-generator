# Разделение сервисов

> **Назначение**: Принципы разделения системы на независимые сервисы.

---

## Принцип

```
Каждый сервис — отдельная единица деплоя с чёткой ответственностью.
Сервисы общаются только через HTTP (REST API).
```

---

## Типы сервисов

### 1. Business API

```
Ответственность:
- Бизнес-логика
- Валидация бизнес-правил
- Оркестрация вызовов к Data API
- REST API для клиентов

Использует:
- HTTP клиент для Data API
- НЕ использует прямой доступ к БД
```

### 2. Data API

```
Ответственность:
- CRUD операции с БД
- Валидация схем данных
- Миграции базы данных

Использует:
- SQLAlchemy / Motor
- Прямое подключение к БД
- Alembic для миграций
```

### 3. Telegram Bot

```
Ответственность:
- UI для Telegram
- Обработка команд и сообщений
- FSM для сложных диалогов

Использует:
- HTTP клиент для Business API
- НЕ вызывает Data API напрямую
```

### 4. Background Worker

```
Ответственность:
- Фоновые задачи
- Периодические операции
- Обработка очередей

Использует:
- HTTP клиент для Business API
- Redis для очередей (опционально)
```

---

## Схема взаимодействия

```
                    ┌─────────────────┐
                    │   Telegram      │
                    │     User        │
                    └────────┬────────┘
                             │
                             ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  Web Client     │   │  Telegram Bot   │   │    Worker       │
└────────┬────────┘   └────────┬────────┘   └────────┬────────┘
         │                     │                     │
         │                     │ HTTP                │
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │  Business API   │
                    │   (FastAPI)     │
                    └────────┬────────┘
                             │
                             │ HTTP
                             │
                             ▼
                    ┌─────────────────┐
                    │    Data API     │
                    │   (FastAPI)     │
                    └────────┬────────┘
                             │
                             │ SQL
                             │
                             ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    └─────────────────┘
```

---

## Правила разделения

### 1. Изоляция кода

```
ПРАВИЛО: Сервисы НЕ импортируют код друг друга.

# ПЛОХО
from booking_data.models import Order  # ❌

# ХОРОШО
# Каждый сервис имеет свои модели/схемы
from booking_api.schemas import OrderResponse  # ✓
```

### 2. Изоляция данных

```
ПРАВИЛО: Только Data API имеет доступ к БД.

Business API:
- Не знает о SQLAlchemy
- Не имеет DATABASE_URL
- Работает через HTTP клиент

Data API:
- Единственный с доступом к БД
- Управляет миграциями
- Валидирует данные
```

### 3. Изоляция конфигурации

```
ПРАВИЛО: Каждый сервис имеет свою конфигурацию.

# Business API
DATA_API_URL=http://booking-data:8001
LOG_LEVEL=INFO

# Data API
DATABASE_URL=postgresql://...
LOG_LEVEL=INFO

# Bot
BOT_TOKEN=...
BUSINESS_API_URL=http://booking-api:8000
```

### 4. Изоляция деплоя

```
ПРАВИЛО: Каждый сервис — отдельный Docker контейнер.

docker-compose.yml:
- booking-api
- booking-data
- booking-bot
- booking-worker
- postgres
- redis
```

---

## Структура директорий

```
project/
├── services/
│   ├── booking_api/           # Business API
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       └── booking_api/
│   │
│   ├── booking_data/          # Data API
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       └── booking_data/
│   │
│   ├── booking_bot/           # Telegram Bot
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       └── booking_bot/
│   │
│   └── booking_worker/        # Background Worker
│       ├── Dockerfile
│       ├── requirements.txt
│       └── src/
│           └── booking_worker/
│
├── docker-compose.yml
├── docker-compose.dev.yml
└── Makefile
```

---

## Docker Compose

```yaml
version: "3.8"

services:
  # Business API
  booking-api:
    build: ./services/booking_api
    ports:
      - "8000:8000"
    environment:
      - DATA_API_URL=http://booking-data:8001
    depends_on:
      - booking-data

  # Data API
  booking-data:
    build: ./services/booking_data
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/booking
    depends_on:
      - postgres

  # Telegram Bot
  booking-bot:
    build: ./services/booking_bot
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - BUSINESS_API_URL=http://booking-api:8000
    depends_on:
      - booking-api

  # Background Worker
  booking-worker:
    build: ./services/booking_worker
    environment:
      - BUSINESS_API_URL=http://booking-api:8000
    depends_on:
      - booking-api

  # Database
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=booking
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Проверка изоляции

```bash
# Проверить, что сервисы не импортируют друг друга

# В booking_api не должно быть импортов booking_data
grep -r "from booking_data" services/booking_api/
grep -r "import booking_data" services/booking_api/

# В booking_bot не должно быть импортов booking_data
grep -r "from booking_data" services/booking_bot/

# Результат должен быть пустым!
```

---

## Связанные документы

| Документ | Описание |
|----------|----------|
| `improved-hybrid.md` | Общая архитектура |
| `data-access.md` | HTTP-only доступ |
