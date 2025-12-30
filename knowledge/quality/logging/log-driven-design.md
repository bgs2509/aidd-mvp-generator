# Log-Driven Design для AI-агентного кодинга

> **Назначение**: Руководство по структурированному логированию для AI-агентов.

---

## Философия

Log-Driven Design — подход к логированию, при котором логи являются
**первичным источником информации** для понимания поведения системы.

AI-агент должен иметь возможность:
1. Понять ЧТО произошло (событие)
2. Понять ПОЧЕМУ это произошло (решение, причина)
3. Восстановить последовательность событий (трассировка)
4. Диагностировать проблемы (контекст ошибок)

---

## 11 принципов (без Kafka)

| # | Принцип | Файлы реализации |
|---|---------|-----------------|
| 1 | Уровни логирования | `shared/utils/logger.py` |
| 2 | Сквозная идентификация | `shared/utils/request_id.py` |
| 3 | JSON-формат | `shared/utils/logger.py` |
| 4 | Логирование решений | `shared/utils/log_helpers.py` |
| 5 | State Machine | `shared/utils/state_machine.py` |
| 6 | Входящие API | `middlewares/request_logging.py` |
| 7 | Исходящие HTTP | `infrastructure/http/base_client.py` |
| 8 | Telegram | `bot/middlewares/logging.py` |
| 9 | Database | `repositories/base.py` |
| 10 | Контекст при старте | `main.py` |
| 11 | ContextVars | `shared/utils/request_id.py` |

---

## Принцип 1: Уровни логирования

```
DEBUG — Детальная отладочная информация
  • Промежуточные значения вычислений
  • Cache hit/miss
  • Детали SQL запросов

INFO — Нормальное выполнение операций
  • Начало/конец запроса
  • Бизнес-операции (order_created, user_registered)
  • Успешные переходы состояний

WARNING — Потенциальные проблемы
  • Fallback на значения по умолчанию
  • Retry операций
  • Приближение к лимитам
  • Медленные запросы

ERROR — Ошибки, требующие внимания
  • Неуспешные операции
  • Недоступность внешних сервисов
  • Невалидные данные от внешних источников

CRITICAL — Система неработоспособна
  • Невозможно подключиться к БД
  • Критические конфигурационные ошибки
```

---

## Принцип 2: Сквозная идентификация

### Четыре типа ID

```
request_id     — уникальный ID текущей операции в сервисе
correlation_id — ID изначального запроса от клиента (не меняется)
causation_id   — ID события, которое вызвало текущее действие
user_id        — ID аутентифицированного пользователя (если есть)
```

### Использование

```python
from shared.utils.request_id import (
    setup_tracing_context,
    create_tracing_headers,
    extract_tracing_from_headers,
    set_user_id,
    get_user_id,
)

# В middleware при получении запроса:
tracing = extract_tracing_from_headers(dict(request.headers))
setup_tracing_context(**tracing)

# После аутентификации пользователя:
set_user_id(str(current_user.id))  # Добавляет user_id во все логи

# При исходящем вызове:
headers = create_tracing_headers()  # Включает request_id, correlation_id, causation_id
response = await client.get("/api/v1/users", headers=headers)
```

### HTTP заголовки

```
X-Request-ID     — request_id
X-Correlation-ID — correlation_id
X-Causation-ID   — causation_id
```

---

## Принцип 4: Логирование решений

AI-агент должен понимать ПОЧЕМУ код пошёл по определённому пути.

```python
from shared.utils.log_helpers import log_decision

# При принятии решения:
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

### Типы решений

```
ACCEPT   — Операция принята
REJECT   — Операция отклонена
RETRY    — Повторная попытка
SKIP     — Пропуск операции
FALLBACK — Использование запасного варианта
```

---

## Принцип 5: State Machine

Логирование переходов состояний сущностей.

```python
from shared.utils.state_machine import LoggedStateMachine

# Создание машины состояний для заказа
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

# Переход с автоматическим логированием
order_sm.transition("CONFIRMED", reason="payment_received")
```

### Лог перехода

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

## Принцип 6: Входящие API запросы

Middleware автоматически логирует все HTTP запросы.

```python
from src.middlewares import RequestLoggingMiddleware

app.add_middleware(
    RequestLoggingMiddleware,
    skip_paths={"/health", "/metrics"},
)
```

### Логируемые поля

```
request_started:
  • method, path
  • query_params, path_params (извлекаются из роутинга)
  • request_body_size
  • client_ip, user_agent
  • api_version (из пути /api/v1/...)

request_completed:
  • status_code
  • duration_ms
  • response_body_size
  • auth_context (user_id, roles, permissions — если аутентифицирован)
  • rate_limit_remaining, rate_limit_limit (из заголовков ответа)
  • error_code, error_message (для 4xx/5xx ответов)
```

### Контекст аутентификации

Для логирования auth_context установите в auth dependency:

```python
# В auth dependency:
request.state.auth_context = {
    "user_id": str(current_user.id),
    "roles": current_user.roles,
    "permissions": current_user.permissions,
}

# Middleware автоматически:
# 1. Читает auth_context из request.state
# 2. Устанавливает user_id в ContextVars
# 3. Добавляет auth_context в лог request_completed
```

### Стандартные error_code

```
VALIDATION_ERROR      — 400 Bad Request (невалидные данные)
AUTHENTICATION_ERROR  — 401 Unauthorized (не аутентифицирован)
AUTHORIZATION_ERROR   — 403 Forbidden (нет прав)
NOT_FOUND            — 404 Not Found (ресурс не найден)
CONFLICT             — 409 Conflict (конфликт данных)
RATE_LIMITED         — 429 Too Many Requests (превышен лимит)
INTERNAL_ERROR       — 500 Internal Server Error
SERVICE_UNAVAILABLE  — 503 Service Unavailable
EXTERNAL_SERVICE_ERROR — ошибка внешнего сервиса
DATABASE_ERROR       — ошибка БД
TIMEOUT_ERROR        — таймаут
```

Для кастомных error_code установите в exception handler:

```python
# В exception handler:
request.state.error_code = "ORDER_ALREADY_CANCELLED"
request.state.error_message = "Cannot process cancelled order"
```

---

## Принцип 7: Исходящие HTTP вызовы

BaseHttpClient автоматически логирует все исходящие запросы.

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

## Принцип 9: Database операции

BaseRepository автоматически логирует все операции с БД.

```python
from shared.utils.log_helpers import log_db_operation, log_slow_query

# Автоматически в BaseRepository:
log_db_operation(
    logger,
    operation="get_by_id",
    table="users",
    query_type="SELECT",
    duration_ms=5.23,
    found=True,
    entity_id="abc-123",
)

# При превышении порога:
log_slow_query(
    logger,
    operation="get_all",
    table="orders",
    duration_ms=150.5,
    threshold_ms=100.0,
)
```

---

## Принцип 10: Контекст при старте

При запуске сервиса логируется полный контекст.

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

## Чек-лист Log-Driven Design

### Общее

- [ ] Все логи в JSON формате (production)
- [ ] Используются стандартные уровни логирования
- [ ] Нет логирования секретных данных (пароли, токены)
- [ ] Нет логирования PII без необходимости

### Трассировка

- [ ] request_id генерируется на входе
- [ ] correlation_id передаётся между сервисами
- [ ] causation_id устанавливается для вызовов
- [ ] user_id устанавливается после аутентификации
- [ ] Все логи содержат request_id

### API

- [ ] Входящие запросы логируются (request_started)
- [ ] path_params извлекаются и логируются
- [ ] Ответы логируются с duration_ms (request_completed)
- [ ] auth_context логируется для аутентифицированных запросов
- [ ] rate_limit_remaining и rate_limit_limit из заголовков
- [ ] error_code и error_message для 4xx/5xx ответов
- [ ] Ошибки логируются с контекстом

### Исходящие вызовы

- [ ] Все HTTP вызовы логируются
- [ ] duration_ms замеряется
- [ ] error_type и is_retryable для ошибок

### Бизнес-логика

- [ ] Решения логируются с причиной
- [ ] Переходы состояний логируются
- [ ] evaluated_conditions для решений

### Database

- [ ] CRUD операции логируются
- [ ] duration_ms для всех запросов
- [ ] Медленные запросы — WARNING

### Telegram (если применимо)

- [ ] update_type, chat_id, user_id
- [ ] Команды и callback_data
- [ ] FSM состояния
- [ ] Ошибки Telegram API

---

## Пример полной трассировки

```json
// Business API — начало запроса (request_id: abc-123, correlation_id: abc-123)
{"event": "request_started", "request_id": "abc-123", "method": "POST", "path": "/api/v1/orders", "path_params": {}}
{"event": "decision_made", "request_id": "abc-123", "user_id": "user-42", "decision": "ACCEPT", "reason": "all_checks_passed"}
{"event": "external_call_started", "request_id": "abc-123", "service": "data-api", "operation": "create_order"}

// Data API (request_id: def-456, correlation_id: abc-123, causation_id: abc-123)
{"event": "request_started", "request_id": "def-456", "correlation_id": "abc-123", "causation_id": "abc-123"}
{"event": "db_operation", "request_id": "def-456", "operation": "create", "table": "orders", "duration_ms": 15.3}
{"event": "request_completed", "request_id": "def-456", "status_code": 201, "duration_ms": 20.1}

// Business API — завершение запроса
{"event": "external_call_completed", "request_id": "abc-123", "service": "data-api", "status_code": 201, "duration_ms": 25.5}
{"event": "state_changed", "request_id": "abc-123", "entity_type": "Order", "from_state": "PENDING", "to_state": "CONFIRMED"}
{"event": "request_completed", "request_id": "abc-123", "user_id": "user-42", "status_code": 201, "duration_ms": 35.2, "auth_context": {"user_id": "user-42", "roles": ["customer"]}}

// Пример ошибки с error_code
{"event": "request_completed", "request_id": "xyz-789", "status_code": 404, "duration_ms": 5.1, "error_code": "NOT_FOUND", "error_message": "Order not found"}
{"event": "request_completed", "request_id": "xyz-790", "status_code": 429, "duration_ms": 2.3, "error_code": "RATE_LIMITED", "rate_limit_remaining": 0, "rate_limit_limit": 100}
```

AI-агент может по correlation_id восстановить всю цепочку вызовов и по user_id отследить все действия пользователя.

---

## Источники

| Файл | Описание |
|------|----------|
| `shared/utils/logger.py` | Настройка structlog |
| `shared/utils/request_id.py` | Трассировка |
| `shared/utils/log_helpers.py` | Хелперы логирования |
| `shared/utils/state_machine.py` | State Machine |
| `knowledge/quality/logging/structured.md` | Структурированные логи |
| `knowledge/quality/logging/correlation.md` | Корреляция логов |
