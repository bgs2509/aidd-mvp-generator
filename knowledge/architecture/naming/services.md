# Именование сервисов

> **Назначение**: Правила именования сервисов и компонентов.

---

## Паттерны именования

### Python пакеты (snake_case)

| Тип сервиса | Паттерн | Пример |
|-------------|---------|--------|
| Business API | `{context}_api` | `booking_api` |
| Data API (PG) | `{context}_data` | `booking_data` |
| Data API (Mongo) | `{context}_docs` | `booking_docs` |
| Telegram Bot | `{context}_bot` | `booking_bot` |
| Background Worker | `{context}_worker` | `booking_worker` |

### Docker сервисы (kebab-case)

| Тип сервиса | Паттерн | Пример |
|-------------|---------|--------|
| Business API | `{context}-api` | `booking-api` |
| Data API | `{context}-data` | `booking-data` |
| PostgreSQL | `{context}-postgres` | `booking-postgres` |
| MongoDB | `{context}-mongo` | `booking-mongo` |
| Redis | `{context}-redis` | `booking-redis` |
| Telegram Bot | `{context}-bot` | `booking-bot` |
| Worker | `{context}-worker` | `booking-worker` |
| Nginx | `{context}-nginx` | `booking-nginx` |

---

## Структура директорий

```
project/
├── services/
│   ├── {context}_api/           # Business API
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       └── {context}_api/   # Python пакет
│   │           ├── __init__.py
│   │           ├── main.py
│   │           └── ...
│   │
│   ├── {context}_data/          # Data API
│   │   └── src/
│   │       └── {context}_data/
│   │
│   ├── {context}_bot/           # Telegram Bot
│   │   └── src/
│   │       └── {context}_bot/
│   │
│   └── {context}_worker/        # Background Worker
│       └── src/
│           └── {context}_worker/
```

---

## Docker Compose

```yaml
# docker-compose.yml

services:
  # Сервисы используют kebab-case
  booking-api:
    build:
      context: ./services/booking_api  # Путь к snake_case директории
    container_name: booking-api
    ports:
      - "8000:8000"

  booking-data:
    build:
      context: ./services/booking_data
    container_name: booking-data
    ports:
      - "8001:8001"

  booking-postgres:
    image: postgres:15-alpine
    container_name: booking-postgres
    ports:
      - "5432:5432"
```

---

## Переменные окружения

```bash
# Общие
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Сервисы (используют _URL суффикс)
DATA_API_URL=http://booking-data:8001
BUSINESS_API_URL=http://booking-api:8000

# База данных
DATABASE_URL=postgresql://postgres:postgres@booking-postgres:5432/booking
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=booking

# Redis
REDIS_URL=redis://booking-redis:6379/0

# Telegram
BOT_TOKEN=your_token_here
```

---

## Порты

| Сервис | Порт по умолчанию |
|--------|-------------------|
| Business API | 8000 |
| Data API (PG) | 8001 |
| Data API (Mongo) | 8002 |
| PostgreSQL | 5432 |
| MongoDB | 27017 |
| Redis | 6379 |
| Nginx | 80, 443 |

---

## Примеры

### Проект: Бронирование ресторанов

```
context = booking
domain = restaurant

Сервисы:
- booking_api (Python) / booking-api (Docker)
- booking_data (Python) / booking-data (Docker)
- booking_bot (Python) / booking-bot (Docker)

Переменные:
- DATA_API_URL=http://booking-data:8001
- DATABASE_URL=postgresql://...@booking-postgres:5432/booking
```

### Проект: Личные финансы

```
context = finance
domain = transaction

Сервисы:
- finance_api (Python) / finance-api (Docker)
- finance_data (Python) / finance-data (Docker)
- finance_worker (Python) / finance-worker (Docker)

Переменные:
- DATA_API_URL=http://finance-data:8001
- DATABASE_URL=postgresql://...@finance-postgres:5432/finance
```

---

## Чек-лист

- [ ] Контекст определён (2-15 символов)
- [ ] Python пакеты в snake_case
- [ ] Docker сервисы в kebab-case
- [ ] Переменные окружения в UPPER_SNAKE_CASE
- [ ] Порты не конфликтуют
- [ ] Структура директорий соблюдена
