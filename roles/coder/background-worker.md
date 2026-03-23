# Function: Stage 4.4 — Background Worker

> **Purpose**: Creating a background worker for asynchronous tasks.

---

## Goal

Create a Background Worker to execute background and
periodic tasks without blocking the main services.

---

## When to Apply

```
if "background" in FR or "periodically" in FR or "scheduled" in FR:
    → Create Background Worker service
else:
    → Skip this stage
```

---

## Architectural Principle

```
RULE: Worker uses the Business API for business operations,
      and does not access the database directly.

Scheduler ──▶ Task Handler ──HTTP──▶ Business API

Worker contains scheduling and task execution logic,
but business logic resides in the Business API.
```

---

## Background Worker Structure

```
services/{context}_worker/
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── src/
│   └── {context}_worker/
│       ├── __init__.py
│       ├── main.py
│       ├── tasks/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── {task_name}_task.py
│       ├── scheduler/
│       │   ├── __init__.py
│       │   └── scheduler.py
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   └── http/
│       │       ├── __init__.py
│       │       └── business_api_client.py
│       └── core/
│           ├── __init__.py
│           ├── config.py
│           └── logging.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── unit/
        └── test_tasks.py
```

---

## Components

### 1. main.py

```python
"""Background Worker entry point."""

import asyncio
import logging
import signal
from typing import Set

from {context}_worker.core.config import settings
from {context}_worker.core.logging import setup_logging
from {context}_worker.scheduler.scheduler import TaskScheduler
from {context}_worker.infrastructure.http.business_api_client import BusinessApiClient
from {context}_worker.tasks import register_tasks


class Worker:
    """Background Worker application."""

    def __init__(self):
        """Initialize the worker."""
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.tasks: Set[asyncio.Task] = set()
        self.scheduler: TaskScheduler | None = None
        self.api_client: BusinessApiClient | None = None

    async def start(self):
        """Start the worker."""
        setup_logging()
        self.logger.info("Worker is starting...")

        # Initialize clients
        self.api_client = BusinessApiClient(settings.business_api_url)

        # Initialize scheduler
        self.scheduler = TaskScheduler(self.api_client)
        register_tasks(self.scheduler)

        # Start
        self.running = True
        await self.scheduler.start()

        self.logger.info("Worker started")

    async def stop(self):
        """Stop the worker."""
        self.logger.info("Worker is stopping...")
        self.running = False

        if self.scheduler:
            await self.scheduler.stop()

        if self.api_client:
            await self.api_client.close()

        # Cancel all tasks
        for task in self.tasks:
            task.cancel()

        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        self.logger.info("Worker stopped")


async def main():
    """Main function."""
    worker = Worker()
    loop = asyncio.get_event_loop()

    # Signal handling
    def signal_handler():
        asyncio.create_task(worker.stop())

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    try:
        await worker.start()
        # Wait for stop
        while worker.running:
            await asyncio.sleep(1)
    finally:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Config (core/config.py)

```python
"""Worker configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Worker settings."""

    # Business API
    business_api_url: str = "http://localhost:8000"

    # Scheduler
    task_interval_seconds: int = 60

    # General
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

### 3. Scheduler (scheduler/scheduler.py)

```python
"""Task scheduler."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Awaitable, Dict, Any

from {context}_worker.infrastructure.http.business_api_client import BusinessApiClient


class TaskScheduler:
    """Periodic task scheduler."""

    def __init__(self, api_client: BusinessApiClient):
        """Initialize the scheduler."""
        self.logger = logging.getLogger(__name__)
        self.api_client = api_client
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._running_tasks: set[asyncio.Task] = set()
        self._stop_event = asyncio.Event()

    def register_task(
        self,
        name: str,
        handler: Callable[[BusinessApiClient], Awaitable[None]],
        interval_seconds: int,
        run_on_start: bool = False,
    ):
        """Register a periodic task."""
        self.tasks[name] = {
            "handler": handler,
            "interval": interval_seconds,
            "run_on_start": run_on_start,
            "last_run": None,
        }
        self.logger.info(
            f"Task '{name}' registered "
            f"(interval: {interval_seconds}s)"
        )

    async def start(self):
        """Start the scheduler."""
        self.logger.info("Scheduler is starting...")
        self._stop_event.clear()

        for name, task_info in self.tasks.items():
            task = asyncio.create_task(
                self._run_periodic_task(name, task_info)
            )
            self._running_tasks.add(task)
            task.add_done_callback(self._running_tasks.discard)

    async def stop(self):
        """Stop the scheduler."""
        self.logger.info("Scheduler is stopping...")
        self._stop_event.set()

        for task in self._running_tasks:
            task.cancel()

        if self._running_tasks:
            await asyncio.gather(
                *self._running_tasks,
                return_exceptions=True,
            )

    async def _run_periodic_task(
        self,
        name: str,
        task_info: Dict[str, Any],
    ):
        """Run a periodic task."""
        handler = task_info["handler"]
        interval = task_info["interval"]

        # Run on start
        if task_info["run_on_start"]:
            await self._execute_task(name, handler)

        while not self._stop_event.is_set():
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=interval,
                )
                break  # Stop signal received
            except asyncio.TimeoutError:
                await self._execute_task(name, handler)

    async def _execute_task(
        self,
        name: str,
        handler: Callable[[BusinessApiClient], Awaitable[None]],
    ):
        """Execute a task."""
        self.logger.info(f"Executing task: {name}")
        start_time = datetime.now()

        try:
            await handler(self.api_client)
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"Task '{name}' completed in {duration:.2f}s"
            )
        except Exception as e:
            self.logger.exception(f"Error in task '{name}': {e}")
```

### 4. Base Task (tasks/base.py)

```python
"""Base class for tasks."""

from abc import ABC, abstractmethod
import logging

from {context}_worker.infrastructure.http.business_api_client import BusinessApiClient


class BaseTask(ABC):
    """Base task class."""

    name: str = "base_task"
    interval_seconds: int = 60
    run_on_start: bool = False

    def __init__(self):
        """Initialize the task."""
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def execute(self, api_client: BusinessApiClient) -> None:
        """Execute the task."""
        pass

    async def __call__(self, api_client: BusinessApiClient) -> None:
        """Call the task."""
        await self.execute(api_client)
```

### 5. Task Example (tasks/{task_name}_task.py)

```python
"""Stale data cleanup task."""

from {context}_worker.tasks.base import BaseTask
from {context}_worker.infrastructure.http.business_api_client import BusinessApiClient


class CleanupTask(BaseTask):
    """Periodic cleanup task."""

    name = "cleanup"
    interval_seconds = 3600  # 1 hour
    run_on_start = False

    async def execute(self, api_client: BusinessApiClient) -> None:
        """Execute cleanup."""
        self.logger.info("Starting stale data cleanup...")

        try:
            # Call Business API for cleanup
            result = await api_client.cleanup_expired()
            self.logger.info(f"Records cleaned: {result.get('deleted', 0)}")

        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
            raise


class NotificationTask(BaseTask):
    """Notification sending task."""

    name = "notifications"
    interval_seconds = 300  # 5 minutes
    run_on_start = True

    async def execute(self, api_client: BusinessApiClient) -> None:
        """Send notifications."""
        self.logger.info("Checking and sending notifications...")

        try:
            # Get pending notifications
            pending = await api_client.get_pending_notifications()

            for notification in pending.get("items", []):
                await api_client.send_notification(notification["id"])
                self.logger.info(f"Notification sent: {notification['id']}")

        except Exception as e:
            self.logger.error(f"Notification sending error: {e}")
            raise
```

### 6. Task Registration (tasks/__init__.py)

```python
"""Task registration."""

from {context}_worker.scheduler.scheduler import TaskScheduler
from {context}_worker.tasks.cleanup_task import CleanupTask, NotificationTask


def register_tasks(scheduler: TaskScheduler):
    """Register all tasks."""
    tasks = [
        CleanupTask(),
        NotificationTask(),
    ]

    for task in tasks:
        scheduler.register_task(
            name=task.name,
            handler=task,
            interval_seconds=task.interval_seconds,
            run_on_start=task.run_on_start,
        )
```

### 7. HTTP Client (infrastructure/http/)

```python
"""HTTP client for Business API."""

from typing import Any

import httpx


class BusinessApiClient:
    """Client for interacting with the Business API."""

    def __init__(self, base_url: str):
        """Initialize the client."""
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=60.0,  # Longer timeout for background tasks
            )
        return self._client

    async def close(self):
        """Close the connection."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def cleanup_expired(self) -> dict[str, Any]:
        """Call expired data cleanup."""
        response = await self.client.post("/api/v1/admin/cleanup")
        response.raise_for_status()
        return response.json()

    async def get_pending_notifications(self) -> dict[str, Any]:
        """Get pending notifications."""
        response = await self.client.get(
            "/api/v1/notifications",
            params={"status": "pending"},
        )
        response.raise_for_status()
        return response.json()

    async def send_notification(self, notification_id: str) -> dict[str, Any]:
        """Send a notification."""
        response = await self.client.post(
            f"/api/v1/notifications/{notification_id}/send"
        )
        response.raise_for_status()
        return response.json()
```

---

## Template to Use

```
templates/services/asyncio_worker/
```

---

## Creation Order

```
1. Create directory structure
2. Create Dockerfile
3. Create requirements.txt
4. Create core/config.py, logging.py
5. Create infrastructure/http/business_api_client.py
6. Create scheduler/scheduler.py
7. Create tasks/base.py
8. Create tasks/{task_name}_task.py
9. Create tasks/__init__.py
10. Create main.py
```

---

## Quality Gates

### WORKER_READY

- [ ] Project structure created from template
- [ ] HTTP client for Business API created
- [ ] Scheduler configured
- [ ] Tasks registered
- [ ] Signal handlers configured
- [ ] Dockerfile created
- [ ] `docker-compose up {context}-worker` starts successfully
- [ ] Tasks execute on schedule

---

## References

| Document | Description |
|----------|-------------|
| `knowledge/services/asyncio-workers/basic-setup.md` | Basic setup |
| `knowledge/services/asyncio-workers/task-management.md` | Task management |
| `knowledge/services/asyncio-workers/signal-handling.md` | Signal handling |
| `templates/services/asyncio_worker/` | Service template |
