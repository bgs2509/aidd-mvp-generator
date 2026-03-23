# Function: Logging (Level >= 2)

> **Purpose**: Setting up structured logging.

---

## Goal

Set up structured logging using structlog
for all project services.

---

## Logging Requirements (Level 2)

```
REQUIRED:
✓ Structured logs (JSON)
✓ Log levels (DEBUG, INFO, WARNING, ERROR)
✓ Request ID for tracing
✓ Contextual information

NOT REQUIRED (Level 3+):
✗ Centralized logging (ELK)
✗ Log aggregation
✗ Alerting
```

---

## Components

### 1. structlog Setup (core/logging.py)

```python
"""Structured logging setup."""

import logging
import sys
from typing import Any

import structlog

from {context}_{service}.core.config import settings


def setup_logging() -> None:
    """Set up logging for the service."""

    # Log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # structlog processors
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.debug:
        # Pretty output for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # JSON for production
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

    # structlog configuration
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Standard logging configuration
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Log level for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a logger with the given name."""
    return structlog.get_logger(name)
```

### 2. Request ID Middleware (middlewares/request_id.py)

```python
"""Middleware for generating and tracking Request ID."""

import uuid
from typing import Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware for adding a Request ID to each request."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request with Request ID."""
        # Get or generate Request ID
        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4()),
        )

        # Add to structlog context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
        )

        # Save in state for use in handlers
        request.state.request_id = request_id

        # Execute request
        response = await call_next(request)

        # Add Request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
```

### 3. Logging Middleware (middlewares/logging.py)

```python
"""Middleware for HTTP request logging."""

import time
from typing import Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""

    def __init__(self, app, logger_name: str = "http"):
        """Initialize middleware."""
        super().__init__(app)
        self.logger = structlog.get_logger(logger_name)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Log request and response."""
        start_time = time.perf_counter()

        # Log incoming request
        self.logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query=str(request.query_params),
            client_ip=request.client.host if request.client else None,
        )

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log successful response
            self.logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log error
            self.logger.exception(
                "request_failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=round(duration_ms, 2),
            )
            raise
```

### 4. Middleware Connection (main.py)

```python
"""Entry point with configured logging."""

from fastapi import FastAPI

from {context}_{service}.core.logging import setup_logging
from {context}_{service}.middlewares.request_id import RequestIDMiddleware
from {context}_{service}.middlewares.logging import LoggingMiddleware


def create_app() -> FastAPI:
    """Application factory."""
    setup_logging()

    app = FastAPI(
        title="{Service Name}",
        version="1.0.0",
    )

    # Middleware (order matters!)
    # Request ID must be first
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)

    # ... routers ...

    return app
```

### 5. Usage in Code

```python
"""Logging usage example."""

import structlog

logger = structlog.get_logger(__name__)


class {Entity}Service:
    """Service with logging."""

    async def create_{entity}(self, data: dict) -> dict:
        """Create {entity} with logging."""
        logger.info(
            "{entity}_creation_started",
            name=data.get("name"),
        )

        try:
            result = await self._do_create(data)

            logger.info(
                "{entity}_created",
                {entity}_id=str(result["id"]),
                name=result["name"],
            )

            return result

        except ValueError as e:
            logger.warning(
                "{entity}_creation_validation_error",
                error=str(e),
                data=data,
            )
            raise

        except Exception as e:
            logger.exception(
                "{entity}_creation_failed",
                error=str(e),
            )
            raise

    async def get_{entity}(self, {entity}_id: str) -> dict | None:
        """Get {entity}."""
        logger.debug(
            "{entity}_fetch_started",
            {entity}_id={entity}_id,
        )

        result = await self._do_get({entity}_id)

        if result is None:
            logger.warning(
                "{entity}_not_found",
                {entity}_id={entity}_id,
            )
        else:
            logger.debug(
                "{entity}_fetched",
                {entity}_id={entity}_id,
            )

        return result
```

---

## Log Format

### Development (console)

```
2024-01-15T10:30:45.123456+00:00 [info     ] request_started            method=GET path=/api/v1/entities request_id=abc-123
2024-01-15T10:30:45.125000+00:00 [info     ] entity_fetched             entity_id=xyz-789 request_id=abc-123
2024-01-15T10:30:45.130000+00:00 [info     ] request_completed          duration_ms=6.54 method=GET path=/api/v1/entities request_id=abc-123 status_code=200
```

### Production (JSON)

```json
{"timestamp": "2024-01-15T10:30:45.123456+00:00", "level": "info", "event": "request_started", "method": "GET", "path": "/api/v1/entities", "request_id": "abc-123"}
{"timestamp": "2024-01-15T10:30:45.125000+00:00", "level": "info", "event": "entity_fetched", "entity_id": "xyz-789", "request_id": "abc-123"}
{"timestamp": "2024-01-15T10:30:45.130000+00:00", "level": "info", "event": "request_completed", "duration_ms": 6.54, "method": "GET", "path": "/api/v1/entities", "request_id": "abc-123", "status_code": 200}
```

---

## Log Levels

| Level | When to Use |
|-------|-------------|
| DEBUG | Detailed debug information |
| INFO | Normal operation execution |
| WARNING | Potential issues (non-critical) |
| ERROR | Errors requiring attention |
| CRITICAL | Critical errors (service is down) |

---

## What to Log

### MUST log

```python
# Incoming requests
logger.info("request_started", method="GET", path="/api/v1/users")

# Outgoing calls
logger.info("external_call_started", service="data_api", endpoint="/users")

# Important business events
logger.info("order_created", order_id="123", user_id="456")

# Errors
logger.error("payment_failed", order_id="123", error="Insufficient funds")

# Performance metrics
logger.info("database_query", query="SELECT", duration_ms=5.2)
```

### MUST NOT log

```python
# Secret data
logger.info("user_login", password="secret")  # BAD!

# PII without necessity
logger.info("user_data", email="user@example.com", phone="+1234567890")  # BAD!

# Large data volumes
logger.info("response", body=large_json_object)  # BAD!
```

---

## Logging Anti-patterns

### NEVER do this

```python
# 1. Useless function entry/exit
def process_order(order):
    logger.debug("Entering process_order")  # BAD!
    result = do_work(order)
    logger.debug("Exiting process_order")   # BAD!
    return result

# 2. Logging every loop iteration
for item in items:
    logger.debug(f"Processing item {item.id}")  # BAD!
    process(item)

# 3. Trivial checks without context
if user is not None:
    logger.debug("User exists")  # BAD! Obvious and useless

# 4. Duplicating already logged information
logger.info("request_started", path="/api/users")
# ... code ...
logger.info("processing request", path="/api/users")  # BAD! path already logged

# 5. Obvious messages
logger.info("Starting to process request...")  # BAD!
logger.info("About to call database...")       # BAD!
logger.info("Going to validate input...")      # BAD!

# 6. Logging successful trivial checks
if len(name) > 0:
    logger.debug("Name is not empty")  # BAD!

# 7. Logging contents of large objects
logger.info("User data", user=user.__dict__)  # BAD!
logger.info("Response", body=response.json()) # BAD!
```

### Do this instead

```python
# 1. Log meaningful business events
logger.info("order_created", order_id=order.id, user_id=user.id)

# 2. For loops — log totals or batches
logger.info("items_processed", count=len(items), duration_ms=elapsed)

# 3. Log decisions with context
if user is None:
    logger.warning("user_not_found", user_id=user_id)
    raise UserNotFoundError(user_id)

# 4. Use request_id to link logs
# Middleware automatically adds request_id

# 5. Use standard events
logger.info("request_started", method="GET", path="/api/users")

# 6. Log only deviations from normal
if not is_valid:
    log_validation_errors(logger, errors, endpoint="/api/users")

# 7. Log only size, not content
logger.info("response_sent", response_size=len(body), status_code=200)
```

### Criteria: when to log?

| Question | Yes → Log | No → Don't log |
|----------|-----------|----------------|
| Will an AI agent understand WHAT happened? | ✅ | ❌ |
| Will an AI agent understand WHY? | ✅ | ❌ |
| Is the information unique? | ✅ | ❌ |
| Does it help with debugging? | ✅ | ❌ |
| Does it affect business logic? | ✅ | ❌ |

### Three-question Rule

Before each `logger.*` ask yourself:

1. **What new does this message add?**
   - If nothing → don't log

2. **Who will read this and why?**
   - DEBUG: developer during debugging
   - INFO: AI agent for understanding the flow
   - WARNING/ERROR: on-call engineer for diagnostics

3. **Can this information be recovered from other logs?**
   - If yes → don't duplicate

---

## Quality Gates

### LOGGING_READY

- [ ] structlog configured
- [ ] Request ID middleware connected
- [ ] Logging middleware connected
- [ ] JSON format in production
- [ ] All services log requests
- [ ] Errors are logged with traceback
- [ ] No logging of secret data

---

## Log-Driven Design

For AI-agent coding, use the extended Log-Driven Design approach.

### Additional Components

| Component | File | Description |
|-----------|------|-------------|
| Logging helpers | `shared/utils/log_helpers.py` | `log_decision`, `log_state_change`, `log_db_operation`, `log_validation_errors`, `log_auth_context`, `log_rate_limit_status` |
| State Machine | `shared/utils/state_machine.py` | Automatic state transition logging |
| Full tracing | `shared/utils/request_id.py` | `correlation_id`, `causation_id` |
| Telegram logging | `bot/middlewares/logging.py` | `update_id`, FSM before/after, detailed Telegram errors |

### Decision Logging Example

```python
from shared.utils.log_helpers import log_decision

if order.fraud_score > settings.fraud_threshold:
    log_decision(
        logger,
        decision="REJECT",
        reason="fraud_score_exceeded",
        threshold_values={"fraud_threshold": settings.fraud_threshold},
        actual_values={"fraud_score": order.fraud_score},
    )
    raise FraudDetectedError(...)
```

### Validation Error Logging Example

```python
from pydantic import ValidationError
from shared.utils.log_helpers import log_validation_errors

try:
    user = UserCreate(**request_data)
except ValidationError as e:
    log_validation_errors(
        logger,
        errors=e.errors(),
        source="request",
        endpoint="/api/v1/users",
    )
    raise HTTPException(status_code=422, detail=e.errors())
```

### Auth Context Logging Example

```python
from shared.utils.log_helpers import log_auth_context

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    log_auth_context(
        logger,
        user_id=str(user.id),
        roles=user.roles,
        auth_method="jwt",
    )
    return user
```

### Rate Limit Logging Example

```python
from shared.utils.log_helpers import log_rate_limit_status, log_rate_limit_exceeded

# When approaching the limit (< 20%)
if remaining < limit * 0.2:
    log_rate_limit_status(logger, limit=100, remaining=15, identifier=client_ip)

# When limit is exceeded
if remaining <= 0:
    log_rate_limit_exceeded(logger, limit=100, retry_after=60, identifier=client_ip)
    raise HTTPException(status_code=429, detail="Rate limit exceeded")
```

---

## References

| Document | Description |
|----------|-------------|
| `knowledge/quality/logging/log-driven-design.md` | **Full Log-Driven Design guide** |
| `knowledge/quality/logging/structured.md` | Structured logging |
| `knowledge/quality/logging/correlation.md` | Log correlation |
