"""
Базовый класс задачи.

Абстрактный класс для всех фоновых задач.
"""

from abc import ABC, abstractmethod

import structlog

from src.core.config import settings


logger = structlog.get_logger()


class BaseTask(ABC):
    """Базовый класс для фоновых задач."""

    # Название задачи
    name: str = "base_task"

    # Интервал выполнения в секундах
    interval_seconds: int = settings.task_interval_seconds

    # Максимальное количество попыток при ошибке
    max_retries: int = 3

    # Задержка между попытками (секунды)
    retry_delay: float = 5.0

    def __init__(self):
        """Инициализация задачи."""
        self.logger = logger.bind(task_name=self.name)

    @abstractmethod
    async def execute(self) -> None:
        """
        Выполнить задачу.

        Этот метод должен быть реализован в наследниках.
        """
        pass

    async def run(self) -> None:
        """Запуск задачи с retry логикой."""
        for attempt in range(1, self.max_retries + 1):
            try:
                await self.execute()
                return

            except Exception as e:
                self.logger.warning(
                    "Ошибка выполнения задачи",
                    attempt=attempt,
                    max_retries=self.max_retries,
                    error=str(e),
                )

                if attempt < self.max_retries:
                    import asyncio
                    await asyncio.sleep(self.retry_delay)
                else:
                    raise


# === Пример задачи ===
# class NotificationTask(BaseTask):
#     """Задача отправки уведомлений."""
#
#     name = "notification_task"
#     interval_seconds = 60
#
#     async def execute(self) -> None:
#         """Выполнить отправку уведомлений."""
#         self.logger.info("Проверка уведомлений")
#
#         # Получить уведомления из API
#         # Отправить уведомления
#
#         self.logger.info("Уведомления отправлены")
