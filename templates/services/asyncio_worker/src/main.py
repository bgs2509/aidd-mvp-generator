"""
Точка входа {context}_worker.

Запуск Background Worker.
"""

import asyncio
import signal
from typing import Set

import structlog

from src.core.config import settings
from src.core.logging import setup_logging
from src.core.scheduler import Scheduler
from src.tasks.base import BaseTask


logger = structlog.get_logger()


class Worker:
    """Background Worker с graceful shutdown."""

    def __init__(self):
        """Инициализация воркера."""
        self.scheduler = Scheduler()
        self.running = True
        self.tasks: Set[asyncio.Task] = set()

    def _setup_signals(self) -> None:
        """Настройка обработчиков сигналов."""
        loop = asyncio.get_running_loop()

        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self._shutdown(s)),
            )

    async def _shutdown(self, sig: signal.Signals) -> None:
        """
        Graceful shutdown.

        Args:
            sig: Полученный сигнал.
        """
        logger.info(
            "Получен сигнал остановки",
            signal=sig.name,
        )

        self.running = False

        # Ожидание завершения текущих задач
        if self.tasks:
            logger.info(
                "Ожидание завершения задач",
                count=len(self.tasks),
            )
            await asyncio.gather(*self.tasks, return_exceptions=True)

        logger.info("Воркер остановлен")

    def register_task(self, task_class: type[BaseTask]) -> None:
        """
        Зарегистрировать задачу.

        Args:
            task_class: Класс задачи.
        """
        self.scheduler.register(task_class)

    async def run(self) -> None:
        """Запуск воркера."""
        self._setup_signals()

        logger.info(
            "Воркер запущен",
            task_count=len(self.scheduler.tasks),
        )

        while self.running:
            try:
                # Запуск задач по расписанию
                pending = self.scheduler.get_pending_tasks()

                for task in pending:
                    asyncio_task = asyncio.create_task(
                        self._run_task(task)
                    )
                    self.tasks.add(asyncio_task)
                    asyncio_task.add_done_callback(self.tasks.discard)

                await asyncio.sleep(1)

            except asyncio.CancelledError:
                break

    async def _run_task(self, task: BaseTask) -> None:
        """
        Выполнить задачу.

        Args:
            task: Экземпляр задачи.
        """
        try:
            logger.info(
                "Запуск задачи",
                task_name=task.name,
            )

            await task.run()

            logger.info(
                "Задача завершена",
                task_name=task.name,
            )

        except Exception as e:
            logger.exception(
                "Ошибка выполнения задачи",
                task_name=task.name,
                error=str(e),
            )


async def main() -> None:
    """Главная функция."""
    # Настройка логирования
    setup_logging(log_level=settings.log_level)

    logger.info("Запуск {context}_worker")

    worker = Worker()

    # Регистрация задач
    # from src.tasks.{domain}_tasks import {Domain}Task
    # worker.register_task({Domain}Task)

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
