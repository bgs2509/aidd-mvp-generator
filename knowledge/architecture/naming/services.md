# Service Naming

> **Purpose**: Naming rules for services and components.

---

## Naming Patterns

### Python Packages (snake_case)

| Service Type | Pattern | Example |
|-------------|---------|--------|
| Business API | `{context}_api` | `booking_api` |
| Data API (PG) | `{context}_data` | `booking_data` |
| Data API (Mongo) | `{context}_docs` | `booking_docs` |
| Telegram Bot | `{context}_bot` | `booking_bot` |
| Background Worker | `{context}_worker` | `booking_worker` |

### Docker Services (kebab-case)

| Service Type | Pattern | Example |
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

## Directory Structure

```
project/
├── services/
│   ├── {context}_api/           # Business API
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       └── {context}_api/   # Python package
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
  # Services use kebab-case
  booking-api:
    build:
      context: ./services/booking_api  # Path to snake_case directory
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

## Environment Variables

```bash
# Common
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Services (use _URL suffix)
DATA_API_URL=http://booking-data:8001
BUSINESS_API_URL=http://booking-api:8000

# Database
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

## Ports

| Service | Default Port |
|--------|-------------------|
| Business API | 8000 |
| Data API (PG) | 8001 |
| Data API (Mongo) | 8002 |
| PostgreSQL | 5432 |
| MongoDB | 27017 |
| Redis | 6379 |
| Nginx | 80, 443 |

---

## Examples

### Project: Restaurant Booking

```
context = booking
domain = restaurant

Services:
- booking_api (Python) / booking-api (Docker)
- booking_data (Python) / booking-data (Docker)
- booking_bot (Python) / booking-bot (Docker)

Variables:
- DATA_API_URL=http://booking-data:8001
- DATABASE_URL=postgresql://...@booking-postgres:5432/booking
```

### Project: Personal Finance

```
context = finance
domain = transaction

Services:
- finance_api (Python) / finance-api (Docker)
- finance_data (Python) / finance-data (Docker)
- finance_worker (Python) / finance-worker (Docker)

Variables:
- DATA_API_URL=http://finance-data:8001
- DATABASE_URL=postgresql://...@finance-postgres:5432/finance
```

---

## Checklist

- [ ] Context defined (2-15 characters)
- [ ] Python packages in snake_case
- [ ] Docker services in kebab-case
- [ ] Environment variables in UPPER_SNAKE_CASE
- [ ] Ports do not conflict
- [ ] Directory structure is followed
