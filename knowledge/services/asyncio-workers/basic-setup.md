# Базовая настройка Asyncio Worker

> **Назначение**: Настройка фонового сервиса на asyncio.

---

## Точка входа

```python
"""Точка входа Background Worker."""

import asyncio
import logging
import signal

from {context}_worker.core.config import settings
from {context}_worker.core.logging import setup_logging
from {context}_worker.scheduler.scheduler import Scheduler
from {context}_worker.tasks import cleanup, notifications, sync


async def main() -> None:
    """Запустить воркер."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting worker...")

    # Создание планировщика
    scheduler = Scheduler()

    # Регистрация задач
    scheduler.register_task(
        cleanup.cleanup_old_orders,
        interval_seconds=3600,  # каждый час
    )
    scheduler.register_task(
        notifications.send_reminders,
        interval_seconds=300,  # каждые 5 минут
    )
    scheduler.register_task(
        sync.sync_external_data,
        interval_seconds=1800,  # каждые 30 минут
    )

    # Обработка сигналов завершения
    stop_event = asyncio.Event()

    def handle_signal():
        logger.info("Received shutdown signal")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_signal)

    # Запуск планировщика
    try:
        await scheduler.start(stop_event)
    finally:
        await scheduler.shutdown()
        logger.info("Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Конфигурация

```python
"""Конфигурация воркера."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Background Worker."""

    service_name: str = "{Context} Worker"

    # API URLs
    business_api_url: str = "http://localhost:8000"
    data_api_url: str = "http://localhost:8001"

    # Настройки
    debug: bool = False
    log_level: str = "INFO"

    # Интервалы (секунды)
    cleanup_interval: int = 3600
    sync_interval: int = 1800

    class Config:
        env_file = ".env"


settings = Settings()
```

---

## Структура проекта

```
{context}_worker/
├── __init__.py
├── main.py                  # Точка входа
│
├── tasks/                   # Задачи
│   ├── __init__.py
│   ├── base.py             # Базовый класс задачи
│   ├── cleanup.py          # Очистка данных
│   ├── notifications.py    # Уведомления
│   └── sync.py             # Синхронизация
│
├── scheduler/              # Планировщик
│   ├── __init__.py
│   └── scheduler.py        # Реализация планировщика
│
├── infrastructure/         # Внешние сервисы
│   ├── __init__.py
│   └── http/
│       ├── __init__.py
│       └── api_client.py
│
└── core/                   # Конфигурация
    ├── __init__.py
    ├── config.py
    └── logging.py
```

---

## Планировщик

```python
"""Планировщик задач."""

import asyncio
import logging
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)


class ScheduledTask:
    """Запланированная задача."""

    def __init__(
        self,
        func: Callable[[], Awaitable[None]],
        interval_seconds: int,
        name: str | None = None,
    ):
        """
        Инициализация задачи.

        Args:
            func: Асинхронная функция задачи.
            interval_seconds: Интервал выполнения.
            name: Имя задачи.
        """
        self.func = func
        self.interval = interval_seconds
        self.name = name or func.__name__


class Scheduler:
    """Планировщик задач."""

    def __init__(self):
        """Инициализация планировщика."""
        self.tasks: list[ScheduledTask] = []
        self._running_tasks: list[asyncio.Task] = []

    def register_task(
        self,
        func: Callable[[], Awaitable[None]],
        interval_seconds: int,
        name: str | None = None,
    ) -> None:
        """
        Зарегистрировать задачу.

        Args:
            func: Асинхронная функция.
            interval_seconds: Интервал выполнения.
            name: Имя задачи.
        """
        task = ScheduledTask(func, interval_seconds, name)
        self.tasks.append(task)
        logger.info(f"Registered task: {task.name}")

    async def _run_task_loop(
        self,
        task: ScheduledTask,
        stop_event: asyncio.Event,
    ) -> None:
        """
        Цикл выполнения задачи.

        Args:
            task: Задача для выполнения.
            stop_event: Событие остановки.
        """
        while not stop_event.is_set():
            try:
                logger.info(f"Running task: {task.name}")
                await task.func()
                logger.info(f"Task completed: {task.name}")
            except Exception as e:
                logger.exception(f"Task failed: {task.name} - {e}")

            # Ожидание с проверкой stop_event
            try:
                await asyncio.wait_for(
                    stop_event.wait(),
                    timeout=task.interval,
                )
            except asyncio.TimeoutError:
                pass  # Таймаут — нормально, продолжаем

    async def start(self, stop_event: asyncio.Event) -> None:
        """
        Запустить планировщик.

        Args:
            stop_event: Событие остановки.
        """
        logger.info(f"Starting scheduler with {len(self.tasks)} tasks")

        # Запуск всех задач
        for task in self.tasks:
            asyncio_task = asyncio.create_task(
                self._run_task_loop(task, stop_event)
            )
            self._running_tasks.append(asyncio_task)

        # Ожидание сигнала остановки
        await stop_event.wait()

    async def shutdown(self) -> None:
        """Остановить планировщик."""
        logger.info("Shutting down scheduler...")

        # Отмена всех задач
        for task in self._running_tasks:
            task.cancel()

        # Ожидание завершения
        await asyncio.gather(*self._running_tasks, return_exceptions=True)

        logger.info("Scheduler stopped")
```

---

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["python", "-m", "src.{context}_worker.main"]
```

---

## Healthcheck

```python
"""Healthcheck для воркера."""

import asyncio
from aiohttp import web


async def run_health_server(port: int = 8080) -> None:
    """
    Запустить HTTP сервер для healthcheck.

    Args:
        port: Порт сервера.
    """
    async def health(request):
        return web.Response(text="OK")

    app = web.Application()
    app.router.add_get("/health", health)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


# В main.py добавить:
# asyncio.create_task(run_health_server())
```

---

## Чек-лист

- [ ] Точка входа с asyncio.run()
- [ ] Сигналы SIGTERM/SIGINT обрабатываются
- [ ] Планировщик создан
- [ ] Задачи зарегистрированы
- [ ] Graceful shutdown настроен
- [ ] Healthcheck endpoint есть
