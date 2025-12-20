"""
Планировщик задач.

Управление расписанием выполнения задач.
"""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.tasks.base import BaseTask


class Scheduler:
    """Планировщик периодических задач."""

    def __init__(self):
        """Инициализация планировщика."""
        self.tasks: list[type["BaseTask"]] = []
        self.last_run: dict[str, datetime] = {}

    def register(self, task_class: type["BaseTask"]) -> None:
        """
        Зарегистрировать задачу.

        Args:
            task_class: Класс задачи.
        """
        self.tasks.append(task_class)
        self.last_run[task_class.name] = datetime.min

    def get_pending_tasks(self) -> list["BaseTask"]:
        """
        Получить задачи, готовые к выполнению.

        Returns:
            Список экземпляров задач.
        """
        now = datetime.now()
        pending = []

        for task_class in self.tasks:
            last = self.last_run[task_class.name]
            interval = task_class.interval_seconds

            if (now - last).total_seconds() >= interval:
                pending.append(task_class())
                self.last_run[task_class.name] = now

        return pending
