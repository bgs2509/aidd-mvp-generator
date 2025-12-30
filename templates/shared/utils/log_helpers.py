"""
Хелперы для структурированного логирования по Log-Driven Design.

Функции для единообразного логирования типовых операций:
- Бизнес-решения (ACCEPT/REJECT/RETRY/SKIP)
- Переходы состояний (State Machine)
- Внешние вызовы (HTTP, gRPC)
- Операции с БД
- Ошибки валидации
- Rate limiting
- Контекст авторизации
"""

import time
from typing import Any, Literal

import structlog

# === Типы решений ===

DecisionType = Literal["ACCEPT", "REJECT", "RETRY", "SKIP", "FALLBACK"]

# === Стандартные коды ошибок ===

ErrorCode = Literal[
    # Клиентские ошибки (4xx)
    "VALIDATION_ERROR",      # 400/422 - Невалидные данные
    "AUTHENTICATION_ERROR",  # 401 - Не аутентифицирован
    "AUTHORIZATION_ERROR",   # 403 - Нет прав доступа
    "NOT_FOUND",             # 404 - Ресурс не найден
    "CONFLICT",              # 409 - Конфликт (дубликат, race condition)
    "RATE_LIMITED",          # 429 - Превышен лимит запросов
    # Серверные ошибки (5xx)
    "INTERNAL_ERROR",        # 500 - Внутренняя ошибка
    "SERVICE_UNAVAILABLE",   # 503 - Сервис недоступен
    "EXTERNAL_SERVICE_ERROR",# 502/504 - Ошибка внешнего сервиса
    "DATABASE_ERROR",        # 500 - Ошибка БД
    "TIMEOUT_ERROR",         # 504 - Таймаут операции
]


def get_error_code_from_status(status_code: int, error_type: str | None = None) -> str:
    """
    Определить стандартный error_code по HTTP статусу и типу ошибки.

    Args:
        status_code: HTTP код ответа.
        error_type: Тип ошибки (опционально, для уточнения).

    Returns:
        Стандартный error_code.

    Example:
        ```python
        error_code = get_error_code_from_status(422, "validation")
        # Returns: "VALIDATION_ERROR"

        error_code = get_error_code_from_status(500)
        # Returns: "INTERNAL_ERROR"
        ```
    """
    # Проверка по типу ошибки (более точно)
    if error_type:
        error_type_lower = error_type.lower()
        if "validation" in error_type_lower:
            return "VALIDATION_ERROR"
        if "auth" in error_type_lower and "orization" in error_type_lower:
            return "AUTHORIZATION_ERROR"
        if "auth" in error_type_lower:
            return "AUTHENTICATION_ERROR"
        if "rate" in error_type_lower or "limit" in error_type_lower:
            return "RATE_LIMITED"
        if "timeout" in error_type_lower:
            return "TIMEOUT_ERROR"
        if "database" in error_type_lower or "db" in error_type_lower:
            return "DATABASE_ERROR"
        if "external" in error_type_lower or "service" in error_type_lower:
            return "EXTERNAL_SERVICE_ERROR"

    # Маппинг по HTTP статусу
    status_mapping = {
        400: "VALIDATION_ERROR",
        401: "AUTHENTICATION_ERROR",
        403: "AUTHORIZATION_ERROR",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
        500: "INTERNAL_ERROR",
        502: "EXTERNAL_SERVICE_ERROR",
        503: "SERVICE_UNAVAILABLE",
        504: "TIMEOUT_ERROR",
    }

    return status_mapping.get(status_code, "INTERNAL_ERROR")


# === Логирование ошибок валидации ===


def log_validation_errors(
    logger: structlog.BoundLogger,
    errors: list[dict[str, Any]] | dict[str, list[str]],
    source: str = "request",
    **kwargs: Any,
) -> None:
    """
    Залогировать ошибки валидации БЕЗ значений полей.

    AI-агент видит КАКИЕ поля невалидны и ПОЧЕМУ, но не видит
    конкретные значения (могут содержать PII).

    Args:
        logger: Логгер structlog.
        errors: Ошибки валидации в одном из форматов:
            - Pydantic V2: [{"loc": ["field"], "msg": "...", "type": "..."}]
            - Простой dict: {"field": ["error1", "error2"]}
        source: Источник валидации (request, response, config).
        **kwargs: Дополнительные поля для лога.

    Example:
        ```python
        # Pydantic ValidationError
        try:
            UserCreate(**data)
        except ValidationError as e:
            log_validation_errors(
                logger,
                errors=e.errors(),
                source="request",
                endpoint="/api/v1/users",
            )
            raise HTTPException(status_code=422, detail=e.errors())

        # Ручная валидация
        errors = {"email": ["invalid format"], "age": ["must be positive"]}
        log_validation_errors(logger, errors, source="business_logic")
        ```
    """
    # Нормализация формата ошибок
    if isinstance(errors, list):
        # Pydantic format: [{"loc": [...], "msg": "...", "type": "..."}]
        invalid_fields = []
        error_types = []
        for err in errors:
            loc = err.get("loc", [])
            field_path = ".".join(str(x) for x in loc) if loc else "unknown"
            invalid_fields.append(field_path)
            if err.get("type"):
                error_types.append(err["type"])

        log_data: dict[str, Any] = {
            "invalid_fields": invalid_fields,
            "error_count": len(errors),
            "source": source,
        }
        if error_types:
            log_data["error_types"] = list(set(error_types))
    else:
        # Simple dict format: {"field": ["error1", "error2"]}
        log_data = {
            "invalid_fields": list(errors.keys()),
            "error_count": sum(len(v) if isinstance(v, list) else 1 for v in errors.values()),
            "source": source,
        }

    log_data.update(kwargs)

    logger.warning("validation_failed", **log_data)


# === Логирование rate limiting ===


def log_rate_limit_status(
    logger: structlog.BoundLogger,
    limit: int,
    remaining: int,
    reset_at: str | None = None,
    identifier: str | None = None,
    **kwargs: Any,
) -> None:
    """
    Залогировать статус rate limiting.

    Вызывается при приближении к лимиту (remaining < 20% от limit).

    Args:
        logger: Логгер structlog.
        limit: Максимальное количество запросов.
        remaining: Оставшееся количество запросов.
        reset_at: Время сброса лимита (ISO format).
        identifier: Идентификатор клиента (IP, user_id, API key).
        **kwargs: Дополнительные поля для лога.

    Example:
        ```python
        # В rate limit middleware
        if remaining < limit * 0.2:  # < 20%
            log_rate_limit_status(
                logger,
                limit=100,
                remaining=15,
                reset_at="2024-01-15T10:35:00Z",
                identifier=client_ip,
            )
        ```
    """
    usage_percent = round((1 - remaining / limit) * 100, 1) if limit > 0 else 100

    log_data: dict[str, Any] = {
        "limit": limit,
        "remaining": remaining,
        "usage_percent": usage_percent,
    }

    if reset_at:
        log_data["reset_at"] = reset_at

    if identifier:
        log_data["identifier"] = identifier

    log_data.update(kwargs)

    # WARNING если использовано > 80%, INFO если > 50%
    if usage_percent >= 80:
        logger.warning("rate_limit_approaching", **log_data)
    else:
        logger.info("rate_limit_status", **log_data)


def log_rate_limit_exceeded(
    logger: structlog.BoundLogger,
    limit: int,
    reset_at: str | None = None,
    identifier: str | None = None,
    retry_after: int | None = None,
    **kwargs: Any,
) -> None:
    """
    Залогировать превышение rate limit.

    Args:
        logger: Логгер structlog.
        limit: Лимит запросов.
        reset_at: Время сброса лимита.
        identifier: Идентификатор клиента.
        retry_after: Секунд до повтора.
        **kwargs: Дополнительные поля для лога.
    """
    log_data: dict[str, Any] = {
        "limit": limit,
    }

    if reset_at:
        log_data["reset_at"] = reset_at

    if identifier:
        log_data["identifier"] = identifier

    if retry_after is not None:
        log_data["retry_after"] = retry_after

    log_data.update(kwargs)

    logger.warning("rate_limit_exceeded", **log_data)


# === Логирование контекста авторизации ===


def log_auth_context(
    logger: structlog.BoundLogger,
    user_id: str | None = None,
    roles: list[str] | None = None,
    permissions: list[str] | None = None,
    auth_method: str | None = None,
    **kwargs: Any,
) -> None:
    """
    Залогировать контекст авторизации.

    Используется после успешной аутентификации для добавления
    контекста авторизации в логи запроса.

    Args:
        logger: Логгер structlog.
        user_id: ID пользователя.
        roles: Роли пользователя.
        permissions: Разрешения пользователя.
        auth_method: Метод аутентификации (jwt, api_key, session).
        **kwargs: Дополнительные поля для лога.

    Example:
        ```python
        # В auth dependency
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
    """
    log_data: dict[str, Any] = {}

    if user_id:
        log_data["user_id"] = user_id

    if roles:
        log_data["roles"] = roles

    if permissions:
        log_data["permissions"] = permissions

    if auth_method:
        log_data["auth_method"] = auth_method

    log_data.update(kwargs)

    if log_data:
        logger.debug("auth_context_set", **log_data)


# === Логирование решений ===


def log_decision(
    logger: structlog.BoundLogger,
    decision: DecisionType,
    reason: str,
    evaluated_conditions: dict[str, Any] | None = None,
    threshold_values: dict[str, Any] | None = None,
    actual_values: dict[str, Any] | None = None,
    **kwargs: Any,
) -> None:
    """
    Залогировать бизнес-решение.

    Используется когда код принимает решение на основе условий.
    AI-агент может понять ПОЧЕМУ код пошёл по определённому пути.

    Args:
        logger: Логгер structlog.
        decision: Тип решения (ACCEPT/REJECT/RETRY/SKIP/FALLBACK).
        reason: Причина решения (машиночитаемая строка).
        evaluated_conditions: Какие условия проверялись.
        threshold_values: Пороговые значения для сравнения.
        actual_values: Фактические значения.
        **kwargs: Дополнительные поля для лога.

    Example:
        ```python
        if order.fraud_score > settings.fraud_threshold:
            log_decision(
                logger,
                decision="REJECT",
                reason="fraud_score_exceeded",
                evaluated_conditions={"fraud_check": True, "inventory_check": False},
                threshold_values={"fraud_threshold": settings.fraud_threshold},
                actual_values={"fraud_score": order.fraud_score},
                order_id=str(order.id),
            )
            raise FraudDetectedError(...)
        ```
    """
    log_data: dict[str, Any] = {
        "decision": decision,
        "reason": reason,
    }

    if evaluated_conditions:
        log_data["evaluated_conditions"] = evaluated_conditions

    if threshold_values:
        log_data["threshold_values"] = threshold_values

    if actual_values:
        log_data["actual_values"] = actual_values

    log_data.update(kwargs)

    # Уровень логирования зависит от решения
    if decision == "REJECT":
        logger.warning("decision_made", **log_data)
    elif decision in ("RETRY", "FALLBACK"):
        logger.warning("decision_made", **log_data)
    else:
        logger.info("decision_made", **log_data)


# === Логирование переходов состояний ===


def log_state_change(
    logger: structlog.BoundLogger,
    entity_type: str,
    entity_id: str,
    from_state: str,
    to_state: str,
    transition_reason: str,
    valid_next_states: list[str] | None = None,
    is_terminal_state: bool = False,
    **kwargs: Any,
) -> None:
    """
    Залогировать переход состояния сущности.

    Используется для отслеживания жизненного цикла сущностей.
    AI-агент видит все переходы и может восстановить историю.

    Args:
        logger: Логгер structlog.
        entity_type: Тип сущности (Order, User, Payment).
        entity_id: Идентификатор сущности.
        from_state: Предыдущее состояние.
        to_state: Новое состояние.
        transition_reason: Причина перехода.
        valid_next_states: Допустимые следующие состояния (опционально).
        is_terminal_state: Является ли новое состояние конечным.
        **kwargs: Дополнительные поля для лога.

    Example:
        ```python
        log_state_change(
            logger,
            entity_type="Order",
            entity_id=str(order.id),
            from_state="PENDING",
            to_state="CONFIRMED",
            transition_reason="payment_received",
            valid_next_states=["PROCESSING", "CANCELLED"],
            is_terminal_state=False,
            payment_id=str(payment.id),
        )
        ```
    """
    log_data: dict[str, Any] = {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "from_state": from_state,
        "to_state": to_state,
        "transition_reason": transition_reason,
        "is_terminal_state": is_terminal_state,
    }

    if valid_next_states is not None:
        log_data["valid_next_states"] = valid_next_states

    log_data.update(kwargs)

    logger.info("state_changed", **log_data)


def log_invalid_state_transition(
    logger: structlog.BoundLogger,
    entity_type: str,
    entity_id: str,
    from_state: str,
    attempted_state: str,
    allowed_transitions: list[str],
    **kwargs: Any,
) -> None:
    """
    Залогировать попытку невалидного перехода состояния.

    Args:
        logger: Логгер structlog.
        entity_type: Тип сущности.
        entity_id: Идентификатор сущности.
        from_state: Текущее состояние.
        attempted_state: Состояние, в которое пытались перейти.
        allowed_transitions: Допустимые переходы из текущего состояния.
        **kwargs: Дополнительные поля для лога.
    """
    logger.error(
        "invalid_state_transition",
        entity_type=entity_type,
        entity_id=entity_id,
        from_state=from_state,
        attempted_state=attempted_state,
        allowed_transitions=allowed_transitions,
        **kwargs,
    )


# === Логирование внешних вызовов ===


def log_external_call_start(
    logger: structlog.BoundLogger,
    service: str,
    operation: str,
    method: str,
    endpoint: str,
    **kwargs: Any,
) -> float:
    """
    Залогировать начало внешнего вызова.

    Args:
        logger: Логгер structlog.
        service: Имя вызываемого сервиса.
        operation: Название операции (get_user, create_order).
        method: HTTP метод (GET, POST, etc).
        endpoint: URL или путь.
        **kwargs: Дополнительные поля для лога.

    Returns:
        Время начала для расчёта duration_ms.

    Example:
        ```python
        start_time = log_external_call_start(
            logger,
            service="payment-gateway",
            operation="process_payment",
            method="POST",
            endpoint="/api/v1/payments",
            payment_id=str(payment.id),
        )

        try:
            response = await client.post(...)
            log_external_call_end(
                logger, service="payment-gateway", operation="process_payment",
                start_time=start_time, status_code=response.status_code,
            )
        except TimeoutError:
            log_external_call_end(
                logger, service="payment-gateway", operation="process_payment",
                start_time=start_time, error_type="timeout", is_retryable=True,
            )
        ```
    """
    logger.debug(
        "external_call_started",
        service=service,
        operation=operation,
        method=method,
        endpoint=endpoint,
        **kwargs,
    )
    return time.perf_counter()


def log_external_call_end(
    logger: structlog.BoundLogger,
    service: str,
    operation: str,
    start_time: float,
    status_code: int | None = None,
    error_type: str | None = None,
    is_retryable: bool = False,
    **kwargs: Any,
) -> None:
    """
    Залогировать завершение внешнего вызова.

    Args:
        logger: Логгер structlog.
        service: Имя вызываемого сервиса.
        operation: Название операции.
        start_time: Время начала (от log_external_call_start).
        status_code: HTTP код ответа (если успешно).
        error_type: Тип ошибки (timeout, connection_error, etc).
        is_retryable: Можно ли повторить запрос.
        **kwargs: Дополнительные поля для лога.
    """
    duration_ms = (time.perf_counter() - start_time) * 1000

    log_data: dict[str, Any] = {
        "service": service,
        "operation": operation,
        "duration_ms": round(duration_ms, 2),
    }

    if status_code is not None:
        log_data["status_code"] = status_code

    if error_type is not None:
        log_data["error_type"] = error_type
        log_data["is_retryable"] = is_retryable

    log_data.update(kwargs)

    # Уровень логирования зависит от результата
    # Log-Driven Design: успешные вызовы логируются на INFO для полной трассировки
    if error_type:
        logger.warning("external_call_failed", **log_data)
    elif status_code and status_code >= 400:
        logger.warning("external_call_completed", **log_data)
    else:
        logger.info("external_call_completed", **log_data)


# === Логирование операций с БД ===


def log_db_operation(
    logger: structlog.BoundLogger,
    operation: str,
    table: str,
    query_type: Literal["SELECT", "INSERT", "UPDATE", "DELETE", "UPSERT"],
    duration_ms: float,
    affected_rows: int | None = None,
    found: bool | None = None,
    **kwargs: Any,
) -> None:
    """
    Залогировать операцию с базой данных.

    Args:
        logger: Логгер structlog.
        operation: Название операции (get_user_by_id, create_order).
        table: Имя таблицы/коллекции.
        query_type: Тип запроса (SELECT/INSERT/UPDATE/DELETE/UPSERT).
        duration_ms: Время выполнения в миллисекундах.
        affected_rows: Количество затронутых строк (для INSERT/UPDATE/DELETE).
        found: Найдена ли запись (для SELECT одной записи).
        **kwargs: Дополнительные поля для лога.

    Example:
        ```python
        start = time.perf_counter()
        user = await session.get(User, user_id)
        duration_ms = (time.perf_counter() - start) * 1000

        log_db_operation(
            logger,
            operation="get_user_by_id",
            table="users",
            query_type="SELECT",
            duration_ms=duration_ms,
            found=user is not None,
            user_id=str(user_id),
        )
        ```
    """
    log_data: dict[str, Any] = {
        "operation": operation,
        "table": table,
        "query_type": query_type,
        "duration_ms": round(duration_ms, 2),
    }

    if affected_rows is not None:
        log_data["affected_rows"] = affected_rows

    if found is not None:
        log_data["found"] = found

    log_data.update(kwargs)

    logger.debug("db_operation", **log_data)


def log_slow_query(
    logger: structlog.BoundLogger,
    operation: str,
    table: str,
    duration_ms: float,
    threshold_ms: float,
    **kwargs: Any,
) -> None:
    """
    Залогировать медленный запрос к БД.

    Вызывается когда duration_ms превышает threshold_ms.

    Args:
        logger: Логгер structlog.
        operation: Название операции.
        table: Имя таблицы/коллекции.
        duration_ms: Фактическое время выполнения.
        threshold_ms: Пороговое значение.
        **kwargs: Дополнительные поля для лога.
    """
    logger.warning(
        "slow_query_detected",
        operation=operation,
        table=table,
        duration_ms=round(duration_ms, 2),
        threshold_ms=threshold_ms,
        **kwargs,
    )


# === Логирование запуска сервиса ===


def log_service_started(
    logger: structlog.BoundLogger,
    service_name: str,
    service_version: str,
    environment: str,
    python_version: str | None = None,
    feature_flags: dict[str, bool] | None = None,
    dependencies: dict[str, str | None] | None = None,
    config_hash: str | None = None,
    **kwargs: Any,
) -> None:
    """
    Залогировать запуск сервиса с полным контекстом.

    Args:
        logger: Логгер structlog.
        service_name: Название сервиса.
        service_version: Версия сервиса.
        environment: Окружение (dev/staging/prod).
        python_version: Версия Python.
        feature_flags: Активные feature flags.
        dependencies: Адреса зависимостей (БД, Redis и т.д.).
        config_hash: Хэш конфигурации для отслеживания изменений.
        **kwargs: Дополнительные поля для лога.

    Example:
        ```python
        import sys
        import hashlib

        log_service_started(
            logger,
            service_name=settings.app_name,
            service_version=settings.app_version,
            environment=settings.app_env,
            python_version=sys.version,
            feature_flags={"debug": settings.debug, "new_auth": True},
            dependencies={
                "database": settings.database_url.split("@")[-1],
                "redis": settings.redis_url.split("@")[-1],
            },
            config_hash=hashlib.md5(settings.json().encode()).hexdigest()[:8],
        )
        ```
    """
    log_data: dict[str, Any] = {
        "service_name": service_name,
        "service_version": service_version,
        "environment": environment,
    }

    if python_version:
        log_data["python_version"] = python_version

    if feature_flags:
        log_data["feature_flags"] = feature_flags

    if dependencies:
        log_data["dependencies"] = dependencies

    if config_hash:
        log_data["config_hash"] = config_hash

    log_data.update(kwargs)

    logger.info("service_started", **log_data)


def log_service_stopped(
    logger: structlog.BoundLogger,
    service_name: str,
    reason: str = "shutdown",
    uptime_seconds: float | None = None,
    **kwargs: Any,
) -> None:
    """
    Залогировать остановку сервиса.

    Args:
        logger: Логгер structlog.
        service_name: Название сервиса.
        reason: Причина остановки (shutdown, error, sigterm).
        uptime_seconds: Время работы в секундах.
        **kwargs: Дополнительные поля для лога.
    """
    log_data: dict[str, Any] = {
        "service_name": service_name,
        "reason": reason,
    }

    if uptime_seconds is not None:
        log_data["uptime_seconds"] = round(uptime_seconds, 2)

    log_data.update(kwargs)

    logger.info("service_stopped", **log_data)


# === Логирование HTTP запросов (для middleware) ===


def log_request_started(
    logger: structlog.BoundLogger,
    method: str,
    path: str,
    query_params: dict[str, Any] | None = None,
    path_params: dict[str, Any] | None = None,
    request_body_size: int | None = None,
    client_ip: str | None = None,
    user_agent: str | None = None,
    api_version: str | None = None,
    auth_context: dict[str, Any] | None = None,
    rate_limit_remaining: int | None = None,
    rate_limit_limit: int | None = None,
    **kwargs: Any,
) -> float:
    """
    Залогировать начало HTTP запроса.

    Args:
        logger: Логгер structlog.
        method: HTTP метод.
        path: Путь запроса.
        query_params: Query параметры.
        path_params: Path параметры (из URL, например {order_id}).
        request_body_size: Размер тела запроса в байтах.
        client_ip: IP клиента.
        user_agent: User-Agent заголовок.
        api_version: Версия API (извлечённая из пути).
        auth_context: Контекст авторизации {user_id, roles, permissions}.
        rate_limit_remaining: Оставшееся количество запросов.
        rate_limit_limit: Максимальное количество запросов.
        **kwargs: Дополнительные поля для лога.

    Returns:
        Время начала для расчёта duration_ms.

    Example:
        ```python
        start_time = log_request_started(
            logger,
            method="POST",
            path="/api/v1/orders",
            path_params={"order_id": "abc-123"},
            auth_context={"user_id": "user-456", "roles": ["admin"]},
            rate_limit_remaining=95,
            rate_limit_limit=100,
        )
        ```
    """
    log_data: dict[str, Any] = {
        "method": method,
        "path": path,
    }

    if query_params:
        log_data["query_params"] = query_params

    if path_params:
        log_data["path_params"] = path_params

    if request_body_size is not None:
        log_data["request_body_size"] = request_body_size

    if client_ip:
        log_data["client_ip"] = client_ip

    if user_agent:
        log_data["user_agent"] = user_agent

    if api_version:
        log_data["api_version"] = api_version

    # auth_context: {user_id, roles, permissions}
    if auth_context:
        log_data["auth_context"] = auth_context

    # Rate limit информация (если приближается к лимиту)
    if rate_limit_remaining is not None and rate_limit_limit is not None:
        log_data["rate_limit_remaining"] = rate_limit_remaining
        log_data["rate_limit_limit"] = rate_limit_limit

    log_data.update(kwargs)

    logger.info("request_started", **log_data)
    return time.perf_counter()


def log_request_completed(
    logger: structlog.BoundLogger,
    method: str,
    path: str,
    start_time: float,
    status_code: int,
    response_body_size: int | None = None,
    error_code: str | None = None,
    error_message: str | None = None,
    **kwargs: Any,
) -> None:
    """
    Залогировать завершение HTTP запроса.

    Args:
        logger: Логгер structlog.
        method: HTTP метод.
        path: Путь запроса.
        start_time: Время начала (от log_request_started).
        status_code: HTTP код ответа.
        response_body_size: Размер тела ответа в байтах.
        error_code: Стандартный код ошибки (для 4xx/5xx).
        error_message: Сообщение об ошибке (без sensitive данных).
        **kwargs: Дополнительные поля для лога.

    Example:
        ```python
        log_request_completed(
            logger,
            method="POST",
            path="/api/v1/orders",
            start_time=start_time,
            status_code=422,
            error_code="VALIDATION_ERROR",
            error_message="Invalid order data",
        )
        ```
    """
    duration_ms = (time.perf_counter() - start_time) * 1000

    log_data: dict[str, Any] = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }

    if response_body_size is not None:
        log_data["response_body_size"] = response_body_size

    # Добавляем error_code для 4xx/5xx ответов
    if status_code >= 400:
        if error_code:
            log_data["error_code"] = error_code
        else:
            # Автоматически определяем error_code по статусу
            log_data["error_code"] = get_error_code_from_status(status_code)

        if error_message:
            log_data["error_message"] = error_message

    log_data.update(kwargs)

    if status_code >= 500:
        logger.error("request_completed", **log_data)
    elif status_code >= 400:
        logger.warning("request_completed", **log_data)
    else:
        logger.info("request_completed", **log_data)
