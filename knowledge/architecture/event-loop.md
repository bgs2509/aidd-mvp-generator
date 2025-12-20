# Управление Event Loop

> **Назначение**: Правила работы с asyncio event loop в сервисах.

---

## Принцип

```
ПРАВИЛО: Каждый сервис владеет ОДНИМ event loop.
         Нельзя создавать дополнительные event loops внутри сервиса.
```

---

## Event Loop по типам сервисов

### FastAPI

```python
"""FastAPI управляет event loop автоматически."""

# main.py
from fastapi import FastAPI

app = FastAPI()

# uvicorn создаёт и управляет event loop
# НЕ нужно вызывать asyncio.run() или создавать loop
```

```bash
# Запуск
uvicorn booking_api.main:app --host 0.0.0.0 --port 8000
```

### Aiogram 3.x

```python
"""Aiogram 3.x использует собственный event loop."""

import asyncio
from aiogram import Bot, Dispatcher

async def main():
    bot = Bot(token="...")
    dp = Dispatcher()

    # dp.start_polling() работает в текущем event loop
    await dp.start_polling(bot)

# asyncio.run() создаёт event loop ОДИН раз
if __name__ == "__main__":
    asyncio.run(main())
```

### Background Worker

```python
"""Worker с собственным event loop."""

import asyncio
import signal


class Worker:
    def __init__(self):
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            await self.process_tasks()
            await asyncio.sleep(1)

    async def stop(self):
        self.running = False


async def main():
    worker = Worker()
    loop = asyncio.get_event_loop()

    # Обработка сигналов
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(worker.stop())
        )

    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Что НЕЛЬЗЯ делать

### ❌ Создавать новый event loop внутри async функции

```python
async def bad_example():
    # ПЛОХО! Создание нового loop внутри async
    loop = asyncio.new_event_loop()  # ❌
    result = loop.run_until_complete(some_coro())  # ❌
```

### ❌ Использовать asyncio.run() внутри сервиса

```python
async def bad_example():
    # ПЛОХО! asyncio.run() создаёт новый loop
    result = asyncio.run(some_coro())  # ❌
```

### ❌ Использовать get_event_loop().run_until_complete()

```python
async def bad_example():
    # ПЛОХО! run_until_complete() блокирует
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(some_coro())  # ❌
```

### ❌ Блокирующие операции в async коде

```python
async def bad_example():
    # ПЛОХО! Блокирующий вызов
    import time
    time.sleep(5)  # ❌ Блокирует весь event loop

    # ПЛОХО! Синхронный HTTP
    import requests
    response = requests.get("http://...")  # ❌
```

---

## Что НУЖНО делать

### ✓ Использовать await для асинхронных операций

```python
async def good_example():
    # ХОРОШО! await для async операций
    result = await some_coro()  # ✓
```

### ✓ asyncio.sleep() вместо time.sleep()

```python
async def good_example():
    # ХОРОШО! Неблокирующий sleep
    await asyncio.sleep(5)  # ✓
```

### ✓ httpx вместо requests

```python
async def good_example():
    # ХОРОШО! Асинхронный HTTP клиент
    async with httpx.AsyncClient() as client:
        response = await client.get("http://...")  # ✓
```

### ✓ asyncio.create_task() для параллельных задач

```python
async def good_example():
    # ХОРОШО! Параллельное выполнение
    task1 = asyncio.create_task(fetch_users())
    task2 = asyncio.create_task(fetch_orders())

    users, orders = await asyncio.gather(task1, task2)  # ✓
```

### ✓ run_in_executor() для блокирующего кода

```python
async def good_example():
    # ХОРОШО! Блокирующий код в executor
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,  # default ThreadPoolExecutor
        blocking_function,
        arg1, arg2
    )  # ✓
```

---

## Проверка нарушений

```bash
# Поиск проблемных паттернов

# asyncio.run() внутри кода (допустимо только в main)
grep -r "asyncio.run(" services/ --include="*.py" | grep -v "main.py"

# Создание новых event loops
grep -r "new_event_loop()" services/

# run_until_complete
grep -r "run_until_complete" services/

# Блокирующий sleep
grep -r "time.sleep" services/

# Синхронный requests
grep -r "import requests" services/
```

---

## Lifespan в FastAPI

```python
"""Управление жизненным циклом через lifespan."""

from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление ресурсами приложения."""
    # Startup
    app.state.http_client = httpx.AsyncClient()
    app.state.db_pool = await create_pool()

    yield

    # Shutdown
    await app.state.http_client.aclose()
    await app.state.db_pool.close()


app = FastAPI(lifespan=lifespan)
```

---

## Обработка сигналов

```python
"""Graceful shutdown с обработкой сигналов."""

import asyncio
import signal


async def main():
    # Получить текущий event loop
    loop = asyncio.get_event_loop()

    # Создать event для shutdown
    shutdown_event = asyncio.Event()

    def signal_handler():
        shutdown_event.set()

    # Зарегистрировать обработчики
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    # Запустить сервис
    await start_service()

    # Ждать сигнала
    await shutdown_event.wait()

    # Graceful shutdown
    await stop_service()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Связанные документы

| Документ | Описание |
|----------|----------|
| `../services/fastapi/application-factory.md` | Фабрика FastAPI |
| `../services/aiogram/basic-setup.md` | Настройка aiogram |
| `../services/asyncio-workers/basic-setup.md` | Настройка workers |
