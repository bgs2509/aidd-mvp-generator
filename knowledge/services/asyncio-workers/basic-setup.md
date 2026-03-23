# Asyncio Worker Basic Setup

> **Purpose**: Setting up a background service on asyncio.

---

## Entry Point

```python
"""Background Worker entry point."""

import asyncio
import logging
import signal

from {context}_worker.core.config import settings
from {context}_worker.core.logging import setup_logging
from {context}_worker.scheduler.scheduler import Scheduler
from {context}_worker.tasks import cleanup, notifications, sync


async def main() -> None:
    """Start the worker."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting worker...")

    # Create scheduler
    scheduler = Scheduler()

    # Register tasks
    scheduler.register_task(
        cleanup.cleanup_old_orders,
        interval_seconds=3600,  # every hour
    )
    scheduler.register_task(
        notifications.send_reminders,
        interval_seconds=300,  # every 5 minutes
    )
    scheduler.register_task(
        sync.sync_external_data,
        interval_seconds=1800,  # every 30 minutes
    )

    # Handle shutdown signals
    stop_event = asyncio.Event()

    def handle_signal():
        logger.info("Received shutdown signal")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_signal)

    # Start scheduler
    try:
        await scheduler.start(stop_event)
    finally:
        await scheduler.shutdown()
        logger.info("Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Configuration

```python
"""Worker configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Background Worker settings."""

    service_name: str = "{Context} Worker"

    # API URLs
    business_api_url: str = "http://localhost:8000"
    data_api_url: str = "http://localhost:8001"

    # Settings
    debug: bool = False
    log_level: str = "INFO"

    # Intervals (seconds)
    cleanup_interval: int = 3600
    sync_interval: int = 1800

    class Config:
        env_file = ".env"


settings = Settings()
```

---

## Project Structure

```
{context}_worker/
├── __init__.py
├── main.py                  # Entry point
│
├── tasks/                   # Tasks
│   ├── __init__.py
│   ├── base.py             # Base task class
│   ├── cleanup.py          # Data cleanup
│   ├── notifications.py    # Notifications
│   └── sync.py             # Synchronization
│
├── scheduler/              # Scheduler
│   ├── __init__.py
│   └── scheduler.py        # Scheduler implementation
│
├── infrastructure/         # External services
│   ├── __init__.py
│   └── http/
│       ├── __init__.py
│       └── api_client.py
│
└── core/                   # Configuration
    ├── __init__.py
    ├── config.py
    └── logging.py
```

---

## Scheduler

```python
"""Task scheduler."""

import asyncio
import logging
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)


class ScheduledTask:
    """Scheduled task."""

    def __init__(
        self,
        func: Callable[[], Awaitable[None]],
        interval_seconds: int,
        name: str | None = None,
    ):
        """
        Initialize task.

        Args:
            func: Async task function.
            interval_seconds: Execution interval.
            name: Task name.
        """
        self.func = func
        self.interval = interval_seconds
        self.name = name or func.__name__


class Scheduler:
    """Task scheduler."""

    def __init__(self):
        """Initialize scheduler."""
        self.tasks: list[ScheduledTask] = []
        self._running_tasks: list[asyncio.Task] = []

    def register_task(
        self,
        func: Callable[[], Awaitable[None]],
        interval_seconds: int,
        name: str | None = None,
    ) -> None:
        """
        Register a task.

        Args:
            func: Async function.
            interval_seconds: Execution interval.
            name: Task name.
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
        Task execution loop.

        Args:
            task: Task to execute.
            stop_event: Stop event.
        """
        while not stop_event.is_set():
            try:
                logger.info(f"Running task: {task.name}")
                await task.func()
                logger.info(f"Task completed: {task.name}")
            except Exception as e:
                logger.exception(f"Task failed: {task.name} - {e}")

            # Wait with stop_event check
            try:
                await asyncio.wait_for(
                    stop_event.wait(),
                    timeout=task.interval,
                )
            except asyncio.TimeoutError:
                pass  # Timeout is normal, continue

    async def start(self, stop_event: asyncio.Event) -> None:
        """
        Start the scheduler.

        Args:
            stop_event: Stop event.
        """
        logger.info(f"Starting scheduler with {len(self.tasks)} tasks")

        # Start all tasks
        for task in self.tasks:
            asyncio_task = asyncio.create_task(
                self._run_task_loop(task, stop_event)
            )
            self._running_tasks.append(asyncio_task)

        # Wait for stop signal
        await stop_event.wait()

    async def shutdown(self) -> None:
        """Stop the scheduler."""
        logger.info("Shutting down scheduler...")

        # Cancel all tasks
        for task in self._running_tasks:
            task.cancel()

        # Wait for completion
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
"""Worker healthcheck."""

import asyncio
from aiohttp import web


async def run_health_server(port: int = 8080) -> None:
    """
    Start HTTP server for healthcheck.

    Args:
        port: Server port.
    """
    async def health(request):
        return web.Response(text="OK")

    app = web.Application()
    app.router.add_get("/health", health)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


# Add to main.py:
# asyncio.create_task(run_health_server())
```

---

## Checklist

- [ ] Entry point with asyncio.run()
- [ ] SIGTERM/SIGINT signals handled
- [ ] Scheduler created
- [ ] Tasks registered
- [ ] Graceful shutdown configured
- [ ] Healthcheck endpoint present
