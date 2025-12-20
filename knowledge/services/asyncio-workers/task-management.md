# Управление задачами Asyncio Worker

> **Назначение**: Паттерны создания и управления задачами.

---

## Базовый класс задачи

```python
"""Базовый класс задачи."""

import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx


class BaseTask(ABC):
    """Базовый класс для фоновых задач."""

    def __init__(self, http_client: httpx.AsyncClient):
        """
        Инициализация задачи.

        Args:
            http_client: HTTP клиент для API.
        """
        self.http_client = http_client
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    @abstractmethod
    def name(self) -> str:
        """Имя задачи."""
        pass

    @abstractmethod
    async def execute(self) -> Any:
        """Выполнить задачу."""
        pass

    async def run(self) -> Any:
        """
        Запустить задачу с логированием.

        Returns:
            Результат выполнения.
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

## Пример задачи

```python
"""Задача очистки старых заказов."""

from datetime import datetime, timedelta

from {context}_worker.tasks.base import BaseTask


class CleanupOldOrdersTask(BaseTask):
    """Задача очистки старых заказов."""

    @property
    def name(self) -> str:
        """Имя задачи."""
        return "cleanup_old_orders"

    async def execute(self) -> int:
        """
        Очистить старые заказы.

        Returns:
            Количество удалённых заказов.
        """
        # Дата для очистки (старше 30 дней)
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        # Вызов Data API
        response = await self.http_client.delete(
            "/api/v1/orders/cleanup",
            params={"before": cutoff_date.isoformat()},
        )
        response.raise_for_status()

        result = response.json()
        deleted_count = result.get("deleted_count", 0)

        self.logger.info(f"Deleted {deleted_count} old orders")
        return deleted_count


# Функция-обёртка для планировщика
async def cleanup_old_orders() -> int:
    """Очистить старые заказы."""
    async with httpx.AsyncClient(base_url=settings.data_api_url) as client:
        task = CleanupOldOrdersTask(client)
        return await task.run()
```

---

## Задача с ретраями

```python
"""Задача с повторными попытками."""

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
    Выполнить функцию с повторными попытками.

    Args:
        func: Асинхронная функция.
        max_retries: Максимальное количество попыток.
        delay: Начальная задержка.
        backoff: Множитель задержки.

    Returns:
        Результат функции.

    Raises:
        Exception: Если все попытки неудачны.
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
    """Задача синхронизации с внешним API."""

    @property
    def name(self) -> str:
        """Имя задачи."""
        return "sync_external_data"

    async def execute(self) -> dict:
        """
        Синхронизировать данные.

        Returns:
            Статистика синхронизации.
        """
        async def do_sync():
            response = await self.http_client.post("/api/v1/sync")
            response.raise_for_status()
            return response.json()

        # Выполнение с ретраями
        return await retry_async(
            do_sync,
            max_retries=3,
            delay=5.0,
        )
```

---

## Задача с транзакциями

```python
"""Задача с пакетной обработкой."""

from typing import List


class ProcessOrdersTask(BaseTask):
    """Задача обработки заказов."""

    BATCH_SIZE = 100

    @property
    def name(self) -> str:
        """Имя задачи."""
        return "process_pending_orders"

    async def execute(self) -> dict:
        """
        Обработать ожидающие заказы.

        Returns:
            Статистика обработки.
        """
        processed = 0
        failed = 0
        offset = 0

        while True:
            # Получить пакет заказов
            orders = await self._get_pending_orders(offset)

            if not orders:
                break

            # Обработать каждый заказ
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
        """Получить ожидающие заказы."""
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
        """Обработать один заказ."""
        response = await self.http_client.post(
            f"/api/v1/orders/{order['id']}/process"
        )
        response.raise_for_status()
```

---

## Задача уведомлений

```python
"""Задача отправки уведомлений."""

from datetime import datetime, timedelta


class SendRemindersTask(BaseTask):
    """Задача отправки напоминаний."""

    @property
    def name(self) -> str:
        """Имя задачи."""
        return "send_reminders"

    async def execute(self) -> dict:
        """
        Отправить напоминания.

        Returns:
            Статистика отправки.
        """
        # Бронирования на ближайший час
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=1)

        # Получить бронирования
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
        """Отправить напоминание."""
        await self.http_client.post(
            f"/api/v1/bookings/{booking['id']}/remind"
        )
```

---

## Регистрация задач

```python
"""Регистрация всех задач."""

from {context}_worker.scheduler.scheduler import Scheduler
from {context}_worker.tasks import cleanup, notifications, sync
from {context}_worker.core.config import settings


def register_all_tasks(scheduler: Scheduler) -> None:
    """
    Зарегистрировать все задачи.

    Args:
        scheduler: Планировщик задач.
    """
    # Очистка — каждый час
    scheduler.register_task(
        cleanup.cleanup_old_orders,
        interval_seconds=settings.cleanup_interval,
        name="cleanup_old_orders",
    )

    # Напоминания — каждые 5 минут
    scheduler.register_task(
        notifications.send_reminders,
        interval_seconds=300,
        name="send_reminders",
    )

    # Синхронизация — каждые 30 минут
    scheduler.register_task(
        sync.sync_external_data,
        interval_seconds=settings.sync_interval,
        name="sync_external_data",
    )
```

---

## Чек-лист

- [ ] Задачи наследуют BaseTask
- [ ] Ретраи настроены для нестабильных операций
- [ ] Пакетная обработка для больших данных
- [ ] Логирование результатов
- [ ] Обработка ошибок без падения воркера
