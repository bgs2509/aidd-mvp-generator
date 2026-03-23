# Asyncio Worker Task Management

> **Purpose**: Task creation and management patterns.

---

## Base Task Class

```python
"""Base task class."""

import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx


class BaseTask(ABC):
    """Base class for background tasks."""

    def __init__(self, http_client: httpx.AsyncClient):
        """
        Initialize task.

        Args:
            http_client: HTTP client for API.
        """
        self.http_client = http_client
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    @abstractmethod
    def name(self) -> str:
        """Task name."""
        pass

    @abstractmethod
    async def execute(self) -> Any:
        """Execute task."""
        pass

    async def run(self) -> Any:
        """
        Run task with logging.

        Returns:
            Execution result.
        """
        self.logger.info(f"Starting task: {self.name}")
        try:
            result = await self.execute()
            self.logger.info(f"Task completed: {self.name}")
            return result
        except Exception as e:
            self.logger.exception(f"Task failed: {self.name} - {e}")
            raise
```

---

## Task Example

```python
"""Old orders cleanup task."""

from datetime import datetime, timedelta

from {context}_worker.tasks.base import BaseTask


class CleanupOldOrdersTask(BaseTask):
    """Old orders cleanup task."""

    @property
    def name(self) -> str:
        """Task name."""
        return "cleanup_old_orders"

    async def execute(self) -> int:
        """
        Clean up old orders.

        Returns:
            Number of deleted orders.
        """
        # Cleanup date (older than 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        # Call Data API
        response = await self.http_client.delete(
            "/api/v1/orders/cleanup",
            params={"before": cutoff_date.isoformat()},
        )
        response.raise_for_status()

        result = response.json()
        deleted_count = result.get("deleted_count", 0)

        self.logger.info(f"Deleted {deleted_count} old orders")
        return deleted_count


# Wrapper function for the scheduler
async def cleanup_old_orders() -> int:
    """Clean up old orders."""
    async with httpx.AsyncClient(base_url=settings.data_api_url) as client:
        task = CleanupOldOrdersTask(client)
        return await task.run()
```

---

## Task with Retries

```python
"""Task with retry logic."""

import asyncio
from typing import TypeVar, Callable, Awaitable

T = TypeVar("T")


async def retry_async(
    func: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> T:
    """
    Execute function with retries.

    Args:
        func: Async function.
        max_retries: Maximum number of attempts.
        delay: Initial delay.
        backoff: Delay multiplier.

    Returns:
        Function result.

    Raises:
        Exception: If all attempts fail.
    """
    last_exception = None
    current_delay = delay

    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                await asyncio.sleep(current_delay)
                current_delay *= backoff

    raise last_exception


class SyncExternalDataTask(BaseTask):
    """External API synchronization task."""

    @property
    def name(self) -> str:
        """Task name."""
        return "sync_external_data"

    async def execute(self) -> dict:
        """
        Synchronize data.

        Returns:
            Synchronization statistics.
        """
        async def do_sync():
            response = await self.http_client.post("/api/v1/sync")
            response.raise_for_status()
            return response.json()

        # Execute with retries
        return await retry_async(
            do_sync,
            max_retries=3,
            delay=5.0,
        )
```

---

## Task with Batch Processing

```python
"""Batch processing task."""

from typing import List


class ProcessOrdersTask(BaseTask):
    """Order processing task."""

    BATCH_SIZE = 100

    @property
    def name(self) -> str:
        """Task name."""
        return "process_pending_orders"

    async def execute(self) -> dict:
        """
        Process pending orders.

        Returns:
            Processing statistics.
        """
        processed = 0
        failed = 0
        offset = 0

        while True:
            # Get batch of orders
            orders = await self._get_pending_orders(offset)

            if not orders:
                break

            # Process each order
            for order in orders:
                try:
                    await self._process_order(order)
                    processed += 1
                except Exception as e:
                    self.logger.error(f"Failed to process order {order['id']}: {e}")
                    failed += 1

            offset += self.BATCH_SIZE

        return {"processed": processed, "failed": failed}

    async def _get_pending_orders(self, offset: int) -> List[dict]:
        """Get pending orders."""
        response = await self.http_client.get(
            "/api/v1/orders",
            params={
                "status": "pending",
                "offset": offset,
                "limit": self.BATCH_SIZE,
            },
        )
        response.raise_for_status()
        return response.json().get("items", [])

    async def _process_order(self, order: dict) -> None:
        """Process a single order."""
        response = await self.http_client.post(
            f"/api/v1/orders/{order['id']}/process"
        )
        response.raise_for_status()
```

---

## Notification Task

```python
"""Notification sending task."""

from datetime import datetime, timedelta


class SendRemindersTask(BaseTask):
    """Reminder sending task."""

    @property
    def name(self) -> str:
        """Task name."""
        return "send_reminders"

    async def execute(self) -> dict:
        """
        Send reminders.

        Returns:
            Sending statistics.
        """
        # Bookings in the next hour
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=1)

        # Get bookings
        response = await self.http_client.get(
            "/api/v1/bookings/upcoming",
            params={
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
            },
        )
        response.raise_for_status()
        bookings = response.json().get("items", [])

        sent = 0
        for booking in bookings:
            if not booking.get("reminder_sent"):
                try:
                    await self._send_reminder(booking)
                    sent += 1
                except Exception as e:
                    self.logger.error(f"Failed to send reminder: {e}")

        return {"sent": sent, "total": len(bookings)}

    async def _send_reminder(self, booking: dict) -> None:
        """Send a reminder."""
        await self.http_client.post(
            f"/api/v1/bookings/{booking['id']}/remind"
        )
```

---

## Task Registration

```python
"""Register all tasks."""

from {context}_worker.scheduler.scheduler import Scheduler
from {context}_worker.tasks import cleanup, notifications, sync
from {context}_worker.core.config import settings


def register_all_tasks(scheduler: Scheduler) -> None:
    """
    Register all tasks.

    Args:
        scheduler: Task scheduler.
    """
    # Cleanup — every hour
    scheduler.register_task(
        cleanup.cleanup_old_orders,
        interval_seconds=settings.cleanup_interval,
        name="cleanup_old_orders",
    )

    # Reminders — every 5 minutes
    scheduler.register_task(
        notifications.send_reminders,
        interval_seconds=300,
        name="send_reminders",
    )

    # Synchronization — every 30 minutes
    scheduler.register_task(
        sync.sync_external_data,
        interval_seconds=settings.sync_interval,
        name="sync_external_data",
    )
```

---

## Checklist

- [ ] Tasks inherit BaseTask
- [ ] Retries configured for unstable operations
- [ ] Batch processing for large data
- [ ] Result logging
- [ ] Error handling without crashing the worker
