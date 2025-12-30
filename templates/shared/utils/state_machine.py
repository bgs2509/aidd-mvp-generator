"""
State Machine с автоматическим логированием по Log-Driven Design.

Обеспечивает:
- Валидацию переходов состояний
- Автоматическое логирование всех переходов
- Отслеживание терминальных состояний
- Полную трассировку жизненного цикла сущностей
"""

from typing import Any

import structlog

from shared.utils.log_helpers import log_state_change, log_invalid_state_transition


logger = structlog.get_logger()


class InvalidStateTransitionError(Exception):
    """Ошибка невалидного перехода состояния."""

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        from_state: str,
        to_state: str,
        allowed_transitions: list[str],
    ):
        """
        Инициализация ошибки.

        Args:
            entity_type: Тип сущности.
            entity_id: ID сущности.
            from_state: Текущее состояние.
            to_state: Запрошенное состояние.
            allowed_transitions: Допустимые переходы.
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.from_state = from_state
        self.to_state = to_state
        self.allowed_transitions = allowed_transitions

        message = (
            f"Invalid transition for {entity_type}[{entity_id}]: "
            f"{from_state} -> {to_state}. "
            f"Allowed: {allowed_transitions}"
        )
        super().__init__(message)


class LoggedStateMachine:
    """
    State Machine с автоматическим логированием переходов.

    AI-агент может полностью восстановить историю изменений
    состояния сущности по логам.

    Attributes:
        entity_type: Тип сущности (Order, Payment, User).
        entity_id: Уникальный идентификатор сущности.
        current_state: Текущее состояние.
        transitions: Граф допустимых переходов.
        terminal_states: Множество конечных состояний.

    Example:
        ```python
        # Определение машины состояний для заказа
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
                "RETURNED": [],
            },
            terminal_states={"DELIVERED", "CANCELLED", "RETURNED"},
        )

        # Переход состояния
        order_sm.transition("CONFIRMED", reason="payment_received")
        ```
    """

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        initial_state: str,
        transitions: dict[str, list[str]],
        terminal_states: set[str] | None = None,
        log_on_init: bool = True,
    ):
        """
        Инициализация State Machine.

        Args:
            entity_type: Тип сущности.
            entity_id: ID сущности.
            initial_state: Начальное состояние.
            transitions: Словарь допустимых переходов {state: [next_states]}.
            terminal_states: Множество конечных состояний.
            log_on_init: Логировать инициализацию.
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.current_state = initial_state
        self.transitions = transitions
        self.terminal_states = terminal_states or set()

        # Валидация начального состояния
        if initial_state not in transitions:
            raise ValueError(
                f"Initial state '{initial_state}' not in transitions graph"
            )

        if log_on_init:
            logger.info(
                "state_machine_initialized",
                entity_type=entity_type,
                entity_id=entity_id,
                initial_state=initial_state,
                terminal_states=list(self.terminal_states),
            )

    @property
    def is_terminal(self) -> bool:
        """Проверить, находится ли машина в терминальном состоянии."""
        return self.current_state in self.terminal_states

    @property
    def valid_next_states(self) -> list[str]:
        """Получить список допустимых следующих состояний."""
        return self.transitions.get(self.current_state, [])

    def can_transition_to(self, target_state: str) -> bool:
        """
        Проверить, возможен ли переход в указанное состояние.

        Args:
            target_state: Целевое состояние.

        Returns:
            True если переход допустим.
        """
        return target_state in self.valid_next_states

    def transition(
        self,
        to_state: str,
        reason: str,
        **kwargs: Any,
    ) -> None:
        """
        Выполнить переход состояния с логированием.

        Args:
            to_state: Целевое состояние.
            reason: Причина перехода (машиночитаемая).
            **kwargs: Дополнительные поля для лога.

        Raises:
            InvalidStateTransitionError: При невалидном переходе.
        """
        from_state = self.current_state

        # Проверка терминального состояния
        if self.is_terminal:
            log_invalid_state_transition(
                logger,
                entity_type=self.entity_type,
                entity_id=self.entity_id,
                from_state=from_state,
                attempted_state=to_state,
                allowed_transitions=[],
                reason="already_in_terminal_state",
                **kwargs,
            )
            raise InvalidStateTransitionError(
                entity_type=self.entity_type,
                entity_id=self.entity_id,
                from_state=from_state,
                to_state=to_state,
                allowed_transitions=[],
            )

        # Проверка допустимости перехода
        if not self.can_transition_to(to_state):
            log_invalid_state_transition(
                logger,
                entity_type=self.entity_type,
                entity_id=self.entity_id,
                from_state=from_state,
                attempted_state=to_state,
                allowed_transitions=self.valid_next_states,
                **kwargs,
            )
            raise InvalidStateTransitionError(
                entity_type=self.entity_type,
                entity_id=self.entity_id,
                from_state=from_state,
                to_state=to_state,
                allowed_transitions=self.valid_next_states,
            )

        # Выполнение перехода
        self.current_state = to_state

        # Логирование успешного перехода
        log_state_change(
            logger,
            entity_type=self.entity_type,
            entity_id=self.entity_id,
            from_state=from_state,
            to_state=to_state,
            transition_reason=reason,
            valid_next_states=self.transitions.get(to_state, []),
            is_terminal_state=to_state in self.terminal_states,
            **kwargs,
        )

    def force_state(
        self,
        state: str,
        reason: str,
        **kwargs: Any,
    ) -> None:
        """
        Принудительно установить состояние (для восстановления из БД).

        ВНИМАНИЕ: Используйте только для восстановления состояния,
        не для обхода валидации!

        Args:
            state: Состояние для установки.
            reason: Причина принудительной установки.
            **kwargs: Дополнительные поля для лога.
        """
        if state not in self.transitions:
            raise ValueError(f"State '{state}' not in transitions graph")

        old_state = self.current_state
        self.current_state = state

        logger.warning(
            "state_forced",
            entity_type=self.entity_type,
            entity_id=self.entity_id,
            from_state=old_state,
            to_state=state,
            reason=reason,
            **kwargs,
        )


# === Пресеты для типичных сущностей ===


def create_order_state_machine(
    order_id: str,
    initial_state: str = "PENDING",
) -> LoggedStateMachine:
    """
    Создать State Machine для заказа.

    Args:
        order_id: ID заказа.
        initial_state: Начальное состояние.

    Returns:
        Настроенная State Machine.
    """
    return LoggedStateMachine(
        entity_type="Order",
        entity_id=order_id,
        initial_state=initial_state,
        transitions={
            "PENDING": ["CONFIRMED", "CANCELLED"],
            "CONFIRMED": ["PROCESSING", "CANCELLED"],
            "PROCESSING": ["SHIPPED", "CANCELLED"],
            "SHIPPED": ["DELIVERED", "RETURNED"],
            "DELIVERED": ["RETURNED"],
            "CANCELLED": [],
            "RETURNED": [],
        },
        terminal_states={"CANCELLED"},
    )


def create_payment_state_machine(
    payment_id: str,
    initial_state: str = "PENDING",
) -> LoggedStateMachine:
    """
    Создать State Machine для платежа.

    Args:
        payment_id: ID платежа.
        initial_state: Начальное состояние.

    Returns:
        Настроенная State Machine.
    """
    return LoggedStateMachine(
        entity_type="Payment",
        entity_id=payment_id,
        initial_state=initial_state,
        transitions={
            "PENDING": ["PROCESSING", "FAILED", "CANCELLED"],
            "PROCESSING": ["COMPLETED", "FAILED"],
            "COMPLETED": ["REFUNDED"],
            "FAILED": ["PENDING"],  # Retry
            "CANCELLED": [],
            "REFUNDED": [],
        },
        terminal_states={"CANCELLED", "REFUNDED"},
    )


def create_user_state_machine(
    user_id: str,
    initial_state: str = "PENDING_VERIFICATION",
) -> LoggedStateMachine:
    """
    Создать State Machine для пользователя.

    Args:
        user_id: ID пользователя.
        initial_state: Начальное состояние.

    Returns:
        Настроенная State Machine.
    """
    return LoggedStateMachine(
        entity_type="User",
        entity_id=user_id,
        initial_state=initial_state,
        transitions={
            "PENDING_VERIFICATION": ["ACTIVE", "REJECTED"],
            "ACTIVE": ["SUSPENDED", "DELETED"],
            "SUSPENDED": ["ACTIVE", "DELETED"],
            "REJECTED": [],
            "DELETED": [],
        },
        terminal_states={"DELETED"},
    )
