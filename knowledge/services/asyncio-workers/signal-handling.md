# Обработка сигналов Asyncio Worker

> **Назначение**: Graceful shutdown и обработка системных сигналов.

---

## Базовая обработка сигналов

```python
"""Обработка сигналов завершения."""

import asyncio
import signal
import logging

logger = logging.getLogger(__name__)


async def main() -> None:
    """Главная функция с обработкой сигналов."""
    # Событие для остановки
    stop_event = asyncio.Event()

    # Обработчик сигналов
    def handle_signal(sig: signal.Signals) -> None:
        logger.info(f"Received signal: {sig.name}")
        stop_event.set()

    # Регистрация обработчиков
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_signal, sig)

    try:
        # Запуск основной логики
        await run_worker(stop_event)
    finally:
        # Очистка обработчиков
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.remove_signal_handler(sig)


async def run_worker(stop_event: asyncio.Event) -> None:
    """
    Запустить воркер.

    Args:
        stop_event: Событие остановки.
    """
    logger.info("Worker started")

    while not stop_event.is_set():
        # Выполнение работы
        await do_work()

        # Ожидание с возможностью прерывания
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            continue

    logger.info("Worker stopped gracefully")
```

---

## Graceful shutdown с таймаутом

```python
"""Graceful shutdown с таймаутом."""

import asyncio
import signal
import logging
from typing import Set

logger = logging.getLogger(__name__)


class GracefulShutdown:
    """Менеджер graceful shutdown."""

    def __init__(self, shutdown_timeout: float = 30.0):
        """
        Инициализация.

        Args:
            shutdown_timeout: Таймаут завершения (секунды).
        """
        self.shutdown_timeout = shutdown_timeout
        self.stop_event = asyncio.Event()
        self.running_tasks: Set[asyncio.Task] = set()

    def register_task(self, task: asyncio.Task) -> None:
        """
        Зарегистрировать задачу.

        Args:
            task: Asyncio задача.
        """
        self.running_tasks.add(task)
        task.add_done_callback(self.running_tasks.discard)

    async def shutdown(self) -> None:
        """Выполнить graceful shutdown."""
        logger.info("Initiating shutdown...")

        # Сигнализировать остановку
        self.stop_event.set()

        if not self.running_tasks:
            logger.info("No running tasks")
            return

        # Ожидание завершения задач с таймаутом
        logger.info(f"Waiting for {len(self.running_tasks)} tasks...")

        done, pending = await asyncio.wait(
            self.running_tasks,
            timeout=self.shutdown_timeout,
        )

        # Принудительная отмена оставшихся
        if pending:
            logger.warning(f"Cancelling {len(pending)} tasks")
            for task in pending:
                task.cancel()

            await asyncio.gather(*pending, return_exceptions=True)

        logger.info("Shutdown complete")


async def main() -> None:
    """Главная функция."""
    shutdown_manager = GracefulShutdown(shutdown_timeout=30.0)

    def handle_signal() -> None:
        asyncio.create_task(shutdown_manager.shutdown())

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_signal)

    # Запуск задач
    task1 = asyncio.create_task(worker_loop(shutdown_manager.stop_event))
    shutdown_manager.register_task(task1)

    task2 = asyncio.create_task(another_worker(shutdown_manager.stop_event))
    shutdown_manager.register_task(task2)

    # Ожидание завершения
    await asyncio.gather(task1, task2, return_exceptions=True)
```

---

## Контекстный менеджер

```python
"""Контекстный менеджер для shutdown."""

import asyncio
import signal
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

logger = logging.getLogger(__name__)


@asynccontextmanager
async def graceful_shutdown_context() -> AsyncIterator[asyncio.Event]:
    """
    Контекстный менеджер для graceful shutdown.

    Yields:
        Событие остановки.
    """
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def handle_signal() -> None:
        logger.info("Shutdown requested")
        stop_event.set()

    # Регистрация
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_signal)

    try:
        yield stop_event
    finally:
        # Очистка
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.remove_signal_handler(sig)
        logger.info("Signal handlers removed")


# Использование
async def main() -> None:
    """Главная функция."""
    async with graceful_shutdown_context() as stop_event:
        scheduler = Scheduler()
        scheduler.register_task(my_task, interval_seconds=60)

        await scheduler.start(stop_event)
        await scheduler.shutdown()
```

---

## Обработка в Docker

```python
"""Особенности работы в Docker."""

import os
import asyncio
import signal
import logging

logger = logging.getLogger(__name__)


def is_docker() -> bool:
    """Проверить, запущены ли в Docker."""
    return os.path.exists("/.dockerenv")


async def main() -> None:
    """Главная функция с учётом Docker."""
    stop_event = asyncio.Event()

    def handle_signal(sig_name: str) -> None:
        logger.info(f"Received {sig_name}")
        stop_event.set()

    loop = asyncio.get_running_loop()

    # SIGTERM важен для Docker
    loop.add_signal_handler(
        signal.SIGTERM,
        lambda: handle_signal("SIGTERM"),
    )

    # SIGINT для локальной разработки (Ctrl+C)
    if not is_docker():
        loop.add_signal_handler(
            signal.SIGINT,
            lambda: handle_signal("SIGINT"),
        )

    try:
        await run_worker(stop_event)
    finally:
        logger.info("Cleanup complete")


# Docker-compose healthcheck
# healthcheck:
#   test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"]
#   interval: 30s
#   timeout: 10s
#   retries: 3
#   start_period: 10s
```

---

## Сохранение состояния при shutdown

```python
"""Сохранение состояния при shutdown."""

import asyncio
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class StatefulWorker:
    """Воркер с сохранением состояния."""

    STATE_FILE = Path("/tmp/worker_state.json")

    def __init__(self):
        """Инициализация."""
        self.state = {"processed_count": 0, "last_id": None}
        self._load_state()

    def _load_state(self) -> None:
        """Загрузить состояние из файла."""
        if self.STATE_FILE.exists():
            try:
                self.state = json.loads(self.STATE_FILE.read_text())
                logger.info(f"Loaded state: {self.state}")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")

    async def save_state(self) -> None:
        """Сохранить состояние в файл."""
        try:
            self.STATE_FILE.write_text(json.dumps(self.state))
            logger.info(f"Saved state: {self.state}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    async def run(self, stop_event: asyncio.Event) -> None:
        """
        Запустить воркер.

        Args:
            stop_event: Событие остановки.
        """
        try:
            while not stop_event.is_set():
                await self._process_batch()

                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=10.0)
                except asyncio.TimeoutError:
                    continue
        finally:
            # Сохранить состояние при завершении
            await self.save_state()

    async def _process_batch(self) -> None:
        """Обработать пакет данных."""
        # Обработка...
        self.state["processed_count"] += 1
```

---

## Сигналы Linux

| Сигнал | Номер | Описание | Docker |
|--------|-------|----------|--------|
| SIGTERM | 15 | Запрос завершения | docker stop |
| SIGINT | 2 | Прерывание (Ctrl+C) | docker attach |
| SIGKILL | 9 | Принудительное завершение | docker kill |
| SIGHUP | 1 | Перезагрузка конфигурации | — |

---

## Чек-лист

- [ ] SIGTERM обрабатывается
- [ ] SIGINT обрабатывается (для dev)
- [ ] Таймаут shutdown настроен
- [ ] Задачи отменяются gracefully
- [ ] Состояние сохраняется при shutdown
- [ ] Логирование shutdown событий
