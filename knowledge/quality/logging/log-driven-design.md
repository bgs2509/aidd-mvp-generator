# Log-Driven Design for AI-Agent Coding

> **Purpose**: Guide to structured logging for AI agents.

---

## Philosophy

Log-Driven Design is an approach to logging where logs are
the **primary source of information** for understanding system behavior.

An AI agent should be able to:
1. Understand WHAT happened (event)
2. Understand WHY it happened (decision, reason)
3. Reconstruct the sequence of events (tracing)
4. Diagnose problems (error context)

---

## 11 Principles (without Kafka)

| # | Principle | Implementation Files |
|---|---------|-----------------|
| 1 | Log levels | `shared/utils/logger.py` |
| 2 | Cross-cutting identification | `shared/utils/request_id.py` |
| 3 | JSON format | `shared/utils/logger.py` |
| 4 | Decision logging | `shared/utils/log_helpers.py` |
| 5 | State Machine | `shared/utils/state_machine.py` |
| 6 | Incoming API | `middlewares/request_logging.py` |
| 7 | Outgoing HTTP | `infrastructure/http/base_client.py` |
| 8 | Telegram | `bot/middlewares/logging.py` |
| 9 | Database | `repositories/base.py` |
| 10 | Startup context | `main.py` |
| 11 | ContextVars | `shared/utils/request_id.py` |

---

## Principle 1: Log Levels

```
DEBUG — Detailed debugging information
  • Intermediate calculation values
  • Cache hit/miss
  • SQL query details

INFO — Normal operation execution
  • Request start/end
  • Business operations (order_created, user_registered)
  • Successful state transitions

WARNING — Potential problems
  • Fallback to default values
  • Operation retries
  • Approaching limits
  • Slow requests

ERROR — Errors requiring attention
  • Failed operations
  • Unavailable external services
  • Invalid data from external sources

CRITICAL — System is inoperable
  • Cannot connect to DB
  • Critical configuration errors
```

---

## Principle 2: Cross-Cutting Identification

### Four ID Types

```
request_id     — unique ID of current operation in the service
correlation_id — ID of the original client request (does not change)
causation_id   — ID of the event that caused the current action
user_id        — ID of the authenticated user (if any)
```

### Usage

```python
from shared.utils.request_id import (
    setup_tracing_context,
    create_tracing_headers,
    extract_tracing_from_headers,
    set_user_id,
    get_user_id,
)

# In middleware when receiving a request:
tracing = extract_tracing_from_headers(dict(request.headers))
setup_tracing_context(**tracing)

# After user authentication:
set_user_id(str(current_user.id))  # Adds user_id to all logs

# On outgoing call:
headers = create_tracing_headers()  # Includes request_id, correlation_id, causation_id
response = await client.get("/api/v1/users", headers=headers)
```

### HTTP Headers

```
X-Request-ID     — request_id
X-Correlation-ID — correlation_id
X-Causation-ID   — causation_id
```

---

## Principle 4: Decision Logging

An AI agent should understand WHY code took a particular path.

```python
from shared.utils.log_helpers import log_decision

# When making a decision:
if order.fraud_score > settings.fraud_threshold:
    log_decision(
        logger,
        decision="REJECT",
        reason="fraud_score_exceeded",
        evaluated_conditions={
            "fraud_check": True,
            "inventory_check": False,
        },
        threshold_values={
            "fraud_threshold": settings.fraud_threshold,
        },
        actual_values={
            "fraud_score": order.fraud_score,
        },
        order_id=str(order.id),
    )
    raise FraudDetectedError(...)

log_decision(
    logger,
    decision="ACCEPT",
    reason="all_checks_passed",
    evaluated_conditions={...},
)
```

### Decision Types

```
ACCEPT   — Operation accepted
REJECT   — Operation rejected
RETRY    — Retry attempt
SKIP     — Operation skipped
FALLBACK — Using fallback option
```

---

## Principle 5: State Machine

Logging entity state transitions.

```python
from shared.utils.state_machine import LoggedStateMachine

# Create state machine for an order
order_sm = LoggedStateMachine(
    entity_type="Order",
    entity_id=str(order.id),
    initial_state="PENDING",
    transitions={
        "PENDING": ["CONFIRMED", "CANCELLED"],
        "CONFIRMED": ["PROCESSING", "CANCELLED"],
        "PROCESSING": ["SHIPPED", "CANCELLED"],
        "SHIPPED": ["DELIVERED", "RETURNED"],
        "DELIVERED": [],
        "CANCELLED": [],
    },
    terminal_states={"DELIVERED", "CANCELLED"},
)

# Transition with automatic logging
order_sm.transition("CONFIRMED", reason="payment_received")
```

### Transition Log

```json
{
  "event": "state_changed",
  "entity_type": "Order",
  "entity_id": "abc-123",
  "from_state": "PENDING",
  "to_state": "CONFIRMED",
  "transition_reason": "payment_received",
  "valid_next_states": ["PROCESSING", "CANCELLED"],
  "is_terminal_state": false
}
```

---

## Principle 6: Incoming API Requests

Middleware automatically logs all HTTP requests.

```python
from src.middlewares import RequestLoggingMiddleware

app.add_middleware(
    RequestLoggingMiddleware,
    skip_paths={"/health", "/metrics"},
)
```

### Logged Fields

```
request_started:
  • method, path
  • query_params, path_params (extracted from routing)
  • request_body_size
  • client_ip, user_agent
  • api_version (from path /api/v1/...)

request_completed:
  • status_code
  • duration_ms
  • response_body_size
  • auth_context (user_id, roles, permissions -- if authenticated)
  • rate_limit_remaining, rate_limit_limit (from response headers)
  • error_code, error_message (for 4xx/5xx responses)
```

### Authentication Context

To log auth_context, set it in the auth dependency:

```python
# In auth dependency:
request.state.auth_context = {
    "user_id": str(current_user.id),
    "roles": current_user.roles,
    "permissions": current_user.permissions,
}

# Middleware automatically:
# 1. Reads auth_context from request.state
# 2. Sets user_id in ContextVars
# 3. Adds auth_context to request_completed log
```

### Standard error_code

```
VALIDATION_ERROR      — 400 Bad Request (invalid data)
AUTHENTICATION_ERROR  — 401 Unauthorized (not authenticated)
AUTHORIZATION_ERROR   — 403 Forbidden (no permissions)
NOT_FOUND            — 404 Not Found (resource not found)
CONFLICT             — 409 Conflict (data conflict)
RATE_LIMITED         — 429 Too Many Requests (rate limit exceeded)
INTERNAL_ERROR       — 500 Internal Server Error
SERVICE_UNAVAILABLE  — 503 Service Unavailable
EXTERNAL_SERVICE_ERROR — external service error
DATABASE_ERROR       — DB error
TIMEOUT_ERROR        — timeout
```

For custom error_code, set it in the exception handler:

```python
# In exception handler:
request.state.error_code = "ORDER_ALREADY_CANCELLED"
request.state.error_message = "Cannot process cancelled order"
```

---

## Principle 7: Outgoing HTTP Calls

BaseHttpClient automatically logs all outgoing requests.

```python
from shared.utils.log_helpers import (
    log_external_call_start,
    log_external_call_end,
)

start_time = log_external_call_start(
    logger,
    service="payment-gateway",
    operation="process_payment",
    method="POST",
    endpoint="/api/v1/payments",
)

try:
    response = await client.post(...)
    log_external_call_end(
        logger,
        service="payment-gateway",
        operation="process_payment",
        start_time=start_time,
        status_code=response.status_code,
    )
except httpx.TimeoutException:
    log_external_call_end(
        logger,
        service="payment-gateway",
        operation="process_payment",
        start_time=start_time,
        error_type="timeout",
        is_retryable=True,
    )
```

---

## Principle 9: Database Operations

BaseRepository automatically logs all DB operations.

```python
from shared.utils.log_helpers import log_db_operation, log_slow_query

# Automatically in BaseRepository:
log_db_operation(
    logger,
    operation="get_by_id",
    table="users",
    query_type="SELECT",
    duration_ms=5.23,
    found=True,
    entity_id="abc-123",
)

# When threshold exceeded:
log_slow_query(
    logger,
    operation="get_all",
    table="orders",
    duration_ms=150.5,
    threshold_ms=100.0,
)
```

---

## Principle 10: Startup Context

Full context is logged at service startup.

```python
from shared.utils.log_helpers import log_service_started

log_service_started(
    logger,
    service_name=settings.app_name,
    service_version="1.0.0",
    environment=settings.app_env,
    python_version=sys.version.split()[0],
    feature_flags={
        "debug": settings.debug,
        "new_auth": True,
    },
    dependencies={
        "database": "postgres:5432",
        "redis": "redis:6379",
    },
    config_hash="a1b2c3d4",
)
```

---

## Log-Driven Design Checklist

### General

- [ ] All logs in JSON format (production)
- [ ] Standard log levels used
- [ ] No logging of secret data (passwords, tokens)
- [ ] No logging of PII without necessity

### Tracing

- [ ] request_id generated on entry
- [ ] correlation_id passed between services
- [ ] causation_id set for calls
- [ ] user_id set after authentication
- [ ] All logs contain request_id

### API

- [ ] Incoming requests logged (request_started)
- [ ] path_params extracted and logged
- [ ] Responses logged with duration_ms (request_completed)
- [ ] auth_context logged for authenticated requests
- [ ] rate_limit_remaining and rate_limit_limit from headers
- [ ] error_code and error_message for 4xx/5xx responses
- [ ] Errors logged with context

### Outgoing Calls

- [ ] All HTTP calls logged
- [ ] duration_ms measured
- [ ] error_type and is_retryable for errors

### Business Logic

- [ ] Decisions logged with reason
- [ ] State transitions logged
- [ ] evaluated_conditions for decisions

### Database

- [ ] CRUD operations logged
- [ ] duration_ms for all queries
- [ ] Slow queries -- WARNING

### Telegram (if applicable)

- [ ] update_type, chat_id, user_id
- [ ] Commands and callback_data
- [ ] FSM states
- [ ] Telegram API errors

---

## Full Trace Example

```json
// Business API -- request start (request_id: abc-123, correlation_id: abc-123)
{"event": "request_started", "request_id": "abc-123", "method": "POST", "path": "/api/v1/orders", "path_params": {}}
{"event": "decision_made", "request_id": "abc-123", "user_id": "user-42", "decision": "ACCEPT", "reason": "all_checks_passed"}
{"event": "external_call_started", "request_id": "abc-123", "service": "data-api", "operation": "create_order"}

// Data API (request_id: def-456, correlation_id: abc-123, causation_id: abc-123)
{"event": "request_started", "request_id": "def-456", "correlation_id": "abc-123", "causation_id": "abc-123"}
{"event": "db_operation", "request_id": "def-456", "operation": "create", "table": "orders", "duration_ms": 15.3}
{"event": "request_completed", "request_id": "def-456", "status_code": 201, "duration_ms": 20.1}

// Business API -- request completion
{"event": "external_call_completed", "request_id": "abc-123", "service": "data-api", "status_code": 201, "duration_ms": 25.5}
{"event": "state_changed", "request_id": "abc-123", "entity_type": "Order", "from_state": "PENDING", "to_state": "CONFIRMED"}
{"event": "request_completed", "request_id": "abc-123", "user_id": "user-42", "status_code": 201, "duration_ms": 35.2, "auth_context": {"user_id": "user-42", "roles": ["customer"]}}

// Error example with error_code
{"event": "request_completed", "request_id": "xyz-789", "status_code": 404, "duration_ms": 5.1, "error_code": "NOT_FOUND", "error_message": "Order not found"}
{"event": "request_completed", "request_id": "xyz-790", "status_code": 429, "duration_ms": 2.3, "error_code": "RATE_LIMITED", "rate_limit_remaining": 0, "rate_limit_limit": 100}
```

An AI agent can use correlation_id to reconstruct the entire call chain and use user_id to track all user actions.

---

## Sources

| File | Description |
|------|----------|
| `shared/utils/logger.py` | structlog setup |
| `shared/utils/request_id.py` | Tracing |
| `shared/utils/log_helpers.py` | Logging helpers |
| `shared/utils/state_machine.py` | State Machine |
| `knowledge/quality/logging/structured.md` | Structured logs |
| `knowledge/quality/logging/correlation.md` | Log correlation |
