# {context}_bot — Telegram Bot Service

> **Type**: Telegram Bot (Aiogram 3.x)
> **Purpose**: Telegram bot for user interaction

---

## Description

Telegram bot on Aiogram 3.x with FSM for dialogs.
Operates on the HTTP-only data access principle through the Business API.

---

## Structure

```
{context}_bot/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── handlers/           # Message handlers
│   │   │   ├── __init__.py
│   │   │   ├── start.py        # /start, /help
│   │   │   ├── {domain}.py     # Domain handlers
│   │   │   └── errors.py       # Error handling
│   │   ├── middlewares/        # Middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # Authorization
│   │   │   ├── throttling.py   # Rate limiting
│   │   │   └── logging.py      # Logging
│   │   ├── keyboards/          # Keyboards
│   │   │   ├── __init__.py
│   │   │   ├── inline.py       # Inline keyboards
│   │   │   └── reply.py        # Reply keyboards
│   │   ├── states/             # FSM states
│   │   │   ├── __init__.py
│   │   │   └── {domain}.py     # Domain states
│   │   └── callbacks/          # Callback data
│   │       ├── __init__.py
│   │       └── {domain}.py     # Domain callbacks
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   └── http/
│   │       ├── __init__.py
│   │       └── api_client.py   # Business API client
│   └── core/
│       ├── __init__.py
│       ├── config.py           # Configuration
│       └── logging.py          # Logging setup
└── tests/
    ├── __init__.py
    └── conftest.py
```

---

## Replacement Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{context}` | Project context (snake_case) | `booking`, `ecommerce` |
| `{domain}` | Entity domain | `user`, `order`, `booking` |
| `{Domain}` | Entity domain (PascalCase) | `User`, `Order`, `Booking` |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python -m src.main

# Run tests
pytest tests/ -v
```

---

## Configuration

Environment variables (`.env`):

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# Business API
BUSINESS_API_URL=http://business-api:8000
BUSINESS_API_TIMEOUT=30

# Redis (for FSM)
REDIS_URL=redis://redis:6379/0

# Logging
LOG_LEVEL=INFO
```

---

## Dependencies

- aiogram>=3.2.0
- httpx
- pydantic-settings
- structlog
- redis (for FSM)

---

## Checklist

- [ ] Replace `{context}` with the project name
- [ ] Configure TELEGRAM_BOT_TOKEN
- [ ] Configure BUSINESS_API_URL
- [ ] Implement handlers in `handlers/`
- [ ] Configure FSM states
- [ ] Add tests
