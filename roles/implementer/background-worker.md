# Функция: Stage 4.4 — Background Worker

> **Назначение**: Создание фонового воркера для асинхронных задач.

---

## Цель

Создать Background Worker для выполнения фоновых и
периодических задач, не блокируя основные сервисы.

---

## Когда применяется

```
if "фоновая" in FR or "периодически" in FR or "по расписанию" in FR:
    → Создать Background Worker сервис
else:
    → Пропустить этот этап
```

---

## Архитектурный принцип

```
ПРАВИЛО: Worker использует Business API для бизнес-операций,
         а не обращается к БД напрямую.

Scheduler ──▶ Task Handler ──HTTP──▶ Business API

Worker содержит логику планирования и выполнения задач,
но бизнес-логика находится в Business API.
```

---

## Структура Background Worker

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

## Компоненты

### 1. main.py

```python
"""Точка входа Background Worker."""

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
    """Background Worker приложение."""

    def __init__(self):
        """Инициализация воркера."""
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.tasks: Set[asyncio.Task] = set()
        self.scheduler: TaskScheduler | None = None
        self.api_client: BusinessApiClient | None = None

    async def start(self):
        """Запуск воркера."""
        setup_logging()
        self.logger.info("Worker запускается...")

        # Инициализация клиентов
        self.api_client = BusinessApiClient(settings.business_api_url)

        # Инициализация планировщика
        self.scheduler = TaskScheduler(self.api_client)
        register_tasks(self.scheduler)

        # Запуск
        self.running = True
        await self.scheduler.start()

        self.logger.info("Worker запущен")

    async def stop(self):
        """Остановка воркера."""
        self.logger.info("Worker останавливается...")
        self.running = False

        if self.scheduler:
            await self.scheduler.stop()

        if self.api_client:
            await self.api_client.close()

        # Отмена всех задач
        for task in self.tasks:
            task.cancel()

        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        self.logger.info("Worker остановлен")


async def main():
    """Главная функция."""
    worker = Worker()
    loop = asyncio.get_event_loop()

    # Обработка сигналов
    def signal_handler():
        asyncio.create_task(worker.stop())

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    try:
        await worker.start()
        # Ожидание остановки
        while worker.running:
            await asyncio.sleep(1)
    finally:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Config (core/config.py)

```python
"""Конфигурация воркера."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки воркера."""

    # Business API
    business_api_url: str = "http://localhost:8000"

    # Scheduler
    task_interval_seconds: int = 60

    # Общие
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

### 3. Scheduler (scheduler/scheduler.py)

```python
"""Планировщик задач."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Awaitable, Dict, Any

from {context}_worker.infrastructure.http.business_api_client import BusinessApiClient


class TaskScheduler:
    """Планировщик периодических задач."""

    def __init__(self, api_client: BusinessApiClient):
        """Инициализация планировщика."""
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
        """Зарегистрировать периодическую задачу."""
        self.tasks[name] = {
            "handler": handler,
            "interval": interval_seconds,
            "run_on_start": run_on_start,
            "last_run": None,
        }
        self.logger.info(
            f"Задача '{name}' зарегистрирована "
            f"(интервал: {interval_seconds}с)"
        )

    async def start(self):
        """Запустить планировщик."""
        self.logger.info("Планировщик запускается...")
        self._stop_event.clear()

        for name, task_info in self.tasks.items():
            task = asyncio.create_task(
                self._run_periodic_task(name, task_info)
            )
            self._running_tasks.add(task)
            task.add_done_callback(self._running_tasks.discard)

    async def stop(self):
        """Остановить планировщик."""
        self.logger.info("Планировщик останавливается...")
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
        """Запуск периодической задачи."""
        handler = task_info["handler"]
        interval = task_info["interval"]

        # Запуск при старте
        if task_info["run_on_start"]:
            await self._execute_task(name, handler)

        while not self._stop_event.is_set():
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=interval,
                )
                break  # Получен сигнал остановки
            except asyncio.TimeoutError:
                await self._execute_task(name, handler)

    async def _execute_task(
        self,
        name: str,
        handler: Callable[[BusinessApiClient], Awaitable[None]],
    ):
        """Выполнить задачу."""
        self.logger.info(f"Выполняется задача: {name}")
        start_time = datetime.now()

        try:
            await handler(self.api_client)
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"Задача '{name}' выполнена за {duration:.2f}с"
            )
        except Exception as e:
            self.logger.exception(f"Ошибка в задаче '{name}': {e}")
```

### 4. Base Task (tasks/base.py)

```python
"""Базовый класс для задач."""

from abc import ABC, abstractmethod
import logging

from {context}_worker.infrastructure.http.business_api_client import BusinessApiClient


class BaseTask(ABC):
    """Базовый класс задачи."""

    name: str = "base_task"
    interval_seconds: int = 60
    run_on_start: bool = False

    def __init__(self):
        """Инициализация задачи."""
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def execute(self, api_client: BusinessApiClient) -> None:
        """Выполнить задачу."""
        pass

    async def __call__(self, api_client: BusinessApiClient) -> None:
        """Вызов задачи."""
        await self.execute(api_client)
```

### 5. Пример задачи (tasks/{task_name}_task.py)

```python
"""Задача очистки устаревших данных."""

from {context}_worker.tasks.base import BaseTask
from {context}_worker.infrastructure.http.business_api_client import BusinessApiClient


class CleanupTask(BaseTask):
    """Задача периодической очистки."""

    name = "cleanup"
    interval_seconds = 3600  # 1 час
    run_on_start = False

    async def execute(self, api_client: BusinessApiClient) -> None:
        """Выполнить очистку."""
        self.logger.info("Запуск очистки устаревших данных...")

        try:
            # Вызов Business API для очистки
            result = await api_client.cleanup_expired()
            self.logger.info(f"Очищено записей: {result.get('deleted', 0)}")

        except Exception as e:
            self.logger.error(f"Ошибка очистки: {e}")
            raise


class NotificationTask(BaseTask):
    """Задача отправки уведомлений."""

    name = "notifications"
    interval_seconds = 300  # 5 минут
    run_on_start = True

    async def execute(self, api_client: BusinessApiClient) -> None:
        """Отправить уведомления."""
        self.logger.info("Проверка и отправка уведомлений...")

        try:
            # Получить ожидающие уведомления
            pending = await api_client.get_pending_notifications()

            for notification in pending.get("items", []):
                await api_client.send_notification(notification["id"])
                self.logger.info(f"Отправлено уведомление: {notification['id']}")

        except Exception as e:
            self.logger.error(f"Ошибка отправки уведомлений: {e}")
            raise
```

### 6. Регистрация задач (tasks/__init__.py)

```python
"""Регистрация задач."""

from {context}_worker.scheduler.scheduler import TaskScheduler
from {context}_worker.tasks.cleanup_task import CleanupTask, NotificationTask


def register_tasks(scheduler: TaskScheduler):
    """Зарегистрировать все задачи."""
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
"""HTTP клиент для Business API."""

from typing import Any

import httpx


class BusinessApiClient:
    """Клиент для взаимодействия с Business API."""

    def __init__(self, base_url: str):
        """Инициализация клиента."""
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Получить HTTP клиент."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=60.0,  # Больше таймаут для фоновых задач
            )
        return self._client

    async def close(self):
        """Закрыть соединение."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def cleanup_expired(self) -> dict[str, Any]:
        """Вызвать очистку устаревших данных."""
        response = await self.client.post("/api/v1/admin/cleanup")
        response.raise_for_status()
        return response.json()

    async def get_pending_notifications(self) -> dict[str, Any]:
        """Получить ожидающие уведомления."""
        response = await self.client.get(
            "/api/v1/notifications",
            params={"status": "pending"},
        )
        response.raise_for_status()
        return response.json()

    async def send_notification(self, notification_id: str) -> dict[str, Any]:
        """Отправить уведомление."""
        response = await self.client.post(
            f"/api/v1/notifications/{notification_id}/send"
        )
        response.raise_for_status()
        return response.json()
```

---

## Шаблон для использования

```
templates/services/asyncio_worker/
```

---

## Порядок создания

```
1. Создать структуру директорий
2. Создать Dockerfile
3. Создать requirements.txt
4. Создать core/config.py, logging.py
5. Создать infrastructure/http/business_api_client.py
6. Создать scheduler/scheduler.py
7. Создать tasks/base.py
8. Создать tasks/{task_name}_task.py
9. Создать tasks/__init__.py
10. Создать main.py
```

---

## Качественные ворота

### WORKER_READY

- [ ] Структура проекта создана по шаблону
- [ ] HTTP клиент для Business API создан
- [ ] Scheduler настроен
- [ ] Задачи зарегистрированы
- [ ] Signal handlers настроены
- [ ] Dockerfile создан
- [ ] `docker-compose up {context}-worker` запускается
- [ ] Задачи выполняются по расписанию

---

## Источники

| Документ | Описание |
|----------|----------|
| `knowledge/services/asyncio-workers/basic-setup.md` | Базовая настройка |
| `knowledge/services/asyncio-workers/task-management.md` | Управление задачами |
| `knowledge/services/asyncio-workers/signal-handling.md` | Обработка сигналов |
| `templates/services/asyncio_worker/` | Шаблон сервиса |
