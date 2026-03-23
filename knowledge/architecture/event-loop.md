# Event Loop Management

> **Purpose**: Rules for working with the asyncio event loop in services.

---

## Principle

```
RULE: Each service owns ONE event loop.
      You must not create additional event loops inside a service.
```

---

## Event Loop by Service Type

### FastAPI

```python
"""FastAPI manages the event loop automatically."""

# main.py
from fastapi import FastAPI

app = FastAPI()

# uvicorn creates and manages the event loop
# No need to call asyncio.run() or create a loop
```

```bash
# Launch
uvicorn booking_api.main:app --host 0.0.0.0 --port 8000
```

### Aiogram 3.x

```python
"""Aiogram 3.x uses its own event loop."""

import asyncio
from aiogram import Bot, Dispatcher

async def main():
    bot = Bot(token="...")
    dp = Dispatcher()

    # dp.start_polling() runs in the current event loop
    await dp.start_polling(bot)

# asyncio.run() creates the event loop ONCE
if __name__ == "__main__":
    asyncio.run(main())
```

### Background Worker

```python
"""Worker with its own event loop."""

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

    # Signal handling
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

## What NOT to Do

### Do NOT create a new event loop inside an async function

```python
async def bad_example():
    # BAD! Creating a new loop inside async
    loop = asyncio.new_event_loop()  # ❌
    result = loop.run_until_complete(some_coro())  # ❌
```

### Do NOT use asyncio.run() inside a service

```python
async def bad_example():
    # BAD! asyncio.run() creates a new loop
    result = asyncio.run(some_coro())  # ❌
```

### Do NOT use get_event_loop().run_until_complete()

```python
async def bad_example():
    # BAD! run_until_complete() blocks
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(some_coro())  # ❌
```

### Do NOT use blocking operations in async code

```python
async def bad_example():
    # BAD! Blocking call
    import time
    time.sleep(5)  # ❌ Blocks the entire event loop

    # BAD! Synchronous HTTP
    import requests
    response = requests.get("http://...")  # ❌
```

---

## What to Do

### Use await for asynchronous operations

```python
async def good_example():
    # GOOD! await for async operations
    result = await some_coro()  # ✓
```

### Use asyncio.sleep() instead of time.sleep()

```python
async def good_example():
    # GOOD! Non-blocking sleep
    await asyncio.sleep(5)  # ✓
```

### Use httpx instead of requests

```python
async def good_example():
    # GOOD! Asynchronous HTTP client
    async with httpx.AsyncClient() as client:
        response = await client.get("http://...")  # ✓
```

### Use asyncio.create_task() for parallel tasks

```python
async def good_example():
    # GOOD! Parallel execution
    task1 = asyncio.create_task(fetch_users())
    task2 = asyncio.create_task(fetch_orders())

    users, orders = await asyncio.gather(task1, task2)  # ✓
```

### Use run_in_executor() for blocking code

```python
async def good_example():
    # GOOD! Blocking code in executor
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,  # default ThreadPoolExecutor
        blocking_function,
        arg1, arg2
    )  # ✓
```

---

## Violation Detection

```bash
# Search for problematic patterns

# asyncio.run() inside code (only acceptable in main)
grep -r "asyncio.run(" services/ --include="*.py" | grep -v "main.py"

# Creating new event loops
grep -r "new_event_loop()" services/

# run_until_complete
grep -r "run_until_complete" services/

# Blocking sleep
grep -r "time.sleep" services/

# Synchronous requests
grep -r "import requests" services/
```

---

## Lifespan in FastAPI

```python
"""Lifecycle management through lifespan."""

from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application resource management."""
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

## Signal Handling

```python
"""Graceful shutdown with signal handling."""

import asyncio
import signal


async def main():
    # Get current event loop
    loop = asyncio.get_event_loop()

    # Create shutdown event
    shutdown_event = asyncio.Event()

    def signal_handler():
        shutdown_event.set()

    # Register handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    # Start service
    await start_service()

    # Wait for signal
    await shutdown_event.wait()

    # Graceful shutdown
    await stop_service()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Related Documents

| Document | Description |
|----------|----------|
| `../services/fastapi/application-factory.md` | FastAPI factory |
| `../services/aiogram/basic-setup.md` | aiogram setup |
| `../services/asyncio-workers/basic-setup.md` | Workers setup |
