# {context}_worker — Background Worker Service

> **Type**: Background Worker (asyncio)
> **Purpose**: Background tasks and periodic operations

---

## Description

Background Worker on asyncio for executing background tasks.
Supports periodic tasks and graceful shutdown.

---

## Structure

```
{context}_worker/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── tasks/                  # Tasks
│   │   ├── __init__.py
│   │   ├── base.py             # Base task class
│   │   └── {domain}_tasks.py   # Domain tasks
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   └── http/
│   │       └── api_client.py   # Business API client
│   └── core/
│       ├── __init__.py
│       ├── config.py           # Configuration
│       ├── logging.py          # Logging setup
│       └── scheduler.py        # Task scheduler
└── tests/
    ├── __init__.py
    └── conftest.py
```

---

## Replacement Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{context}` | Project context | `booking`, `ecommerce` |
| `{domain}` | Task domain | `notification`, `sync` |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run worker
python -m src.main

# Run tests
pytest tests/ -v
```

---

## Configuration

Environment variables (`.env`):

```bash
# Business API
BUSINESS_API_URL=http://business-api:8000
BUSINESS_API_TIMEOUT=30

# Tasks
TASK_INTERVAL_SECONDS=60

# Logging
LOG_LEVEL=INFO
```

---

## Dependencies

- httpx
- pydantic-settings
- structlog

---

## Checklist

- [ ] Replace `{context}` with the project name
- [ ] Implement tasks in `tasks/`
- [ ] Configure execution intervals
- [ ] Add graceful shutdown
- [ ] Add tests
