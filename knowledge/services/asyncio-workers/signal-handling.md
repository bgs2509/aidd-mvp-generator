# Asyncio Worker Signal Handling

> **Purpose**: Graceful shutdown and system signal handling.

---

## Basic Signal Handling

```python
"""Shutdown signal handling."""

import asyncio
import signal
import logging

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main function with signal handling."""
    # Stop event
    stop_event = asyncio.Event()

    # Signal handler
    def handle_signal(sig: signal.Signals) -> None:
        logger.info(f"Received signal: {sig.name}")
        stop_event.set()

    # Register handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_signal, sig)

    try:
        # Start main logic
        await run_worker(stop_event)
    finally:
        # Clean up handlers
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.remove_signal_handler(sig)


async def run_worker(stop_event: asyncio.Event) -> None:
    """
    Start the worker.

    Args:
        stop_event: Stop event.
    """
    logger.info("Worker started")

    while not stop_event.is_set():
        # Do work
        await do_work()

        # Wait with interruption capability
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            continue

    logger.info("Worker stopped gracefully")
```

---

## Graceful Shutdown with Timeout

```python
"""Graceful shutdown with timeout."""

import asyncio
import signal
import logging
from typing import Set

logger = logging.getLogger(__name__)


class GracefulShutdown:
    """Graceful shutdown manager."""

    def __init__(self, shutdown_timeout: float = 30.0):
        """
        Initialize.

        Args:
            shutdown_timeout: Shutdown timeout (seconds).
        """
        self.shutdown_timeout = shutdown_timeout
        self.stop_event = asyncio.Event()
        self.running_tasks: Set[asyncio.Task] = set()

    def register_task(self, task: asyncio.Task) -> None:
        """
        Register a task.

        Args:
            task: Asyncio task.
        """
        self.running_tasks.add(task)
        task.add_done_callback(self.running_tasks.discard)

    async def shutdown(self) -> None:
        """Perform graceful shutdown."""
        logger.info("Initiating shutdown...")

        # Signal stop
        self.stop_event.set()

        if not self.running_tasks:
            logger.info("No running tasks")
            return

        # Wait for task completion with timeout
        logger.info(f"Waiting for {len(self.running_tasks)} tasks...")

        done, pending = await asyncio.wait(
            self.running_tasks,
            timeout=self.shutdown_timeout,
        )

        # Force cancel remaining tasks
        if pending:
            logger.warning(f"Cancelling {len(pending)} tasks")
            for task in pending:
                task.cancel()

            await asyncio.gather(*pending, return_exceptions=True)

        logger.info("Shutdown complete")


async def main() -> None:
    """Main function."""
    shutdown_manager = GracefulShutdown(shutdown_timeout=30.0)

    def handle_signal() -> None:
        asyncio.create_task(shutdown_manager.shutdown())

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_signal)

    # Start tasks
    task1 = asyncio.create_task(worker_loop(shutdown_manager.stop_event))
    shutdown_manager.register_task(task1)

    task2 = asyncio.create_task(another_worker(shutdown_manager.stop_event))
    shutdown_manager.register_task(task2)

    # Wait for completion
    await asyncio.gather(task1, task2, return_exceptions=True)
```

---

## Context Manager

```python
"""Context manager for shutdown."""

import asyncio
import signal
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

logger = logging.getLogger(__name__)


@asynccontextmanager
async def graceful_shutdown_context() -> AsyncIterator[asyncio.Event]:
    """
    Context manager for graceful shutdown.

    Yields:
        Stop event.
    """
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def handle_signal() -> None:
        logger.info("Shutdown requested")
        stop_event.set()

    # Register
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_signal)

    try:
        yield stop_event
    finally:
        # Cleanup
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.remove_signal_handler(sig)
        logger.info("Signal handlers removed")


# Usage
async def main() -> None:
    """Main function."""
    async with graceful_shutdown_context() as stop_event:
        scheduler = Scheduler()
        scheduler.register_task(my_task, interval_seconds=60)

        await scheduler.start(stop_event)
        await scheduler.shutdown()
```

---

## Docker Handling

```python
"""Docker-specific considerations."""

import os
import asyncio
import signal
import logging

logger = logging.getLogger(__name__)


def is_docker() -> bool:
    """Check if running inside Docker."""
    return os.path.exists("/.dockerenv")


async def main() -> None:
    """Main function with Docker awareness."""
    stop_event = asyncio.Event()

    def handle_signal(sig_name: str) -> None:
        logger.info(f"Received {sig_name}")
        stop_event.set()

    loop = asyncio.get_running_loop()

    # SIGTERM is important for Docker
    loop.add_signal_handler(
        signal.SIGTERM,
        lambda: handle_signal("SIGTERM"),
    )

    # SIGINT for local development (Ctrl+C)
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

## State Persistence on Shutdown

```python
"""State persistence on shutdown."""

import asyncio
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class StatefulWorker:
    """Worker with state persistence."""

    STATE_FILE = Path("/tmp/worker_state.json")

    def __init__(self):
        """Initialize."""
        self.state = {"processed_count": 0, "last_id": None}
        self._load_state()

    def _load_state(self) -> None:
        """Load state from file."""
        if self.STATE_FILE.exists():
            try:
                self.state = json.loads(self.STATE_FILE.read_text())
                logger.info(f"Loaded state: {self.state}")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")

    async def save_state(self) -> None:
        """Save state to file."""
        try:
            self.STATE_FILE.write_text(json.dumps(self.state))
            logger.info(f"Saved state: {self.state}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    async def run(self, stop_event: asyncio.Event) -> None:
        """
        Start the worker.

        Args:
            stop_event: Stop event.
        """
        try:
            while not stop_event.is_set():
                await self._process_batch()

                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=10.0)
                except asyncio.TimeoutError:
                    continue
        finally:
            # Save state on shutdown
            await self.save_state()

    async def _process_batch(self) -> None:
        """Process a batch of data."""
        # Processing...
        self.state["processed_count"] += 1
```

---

## Linux Signals

| Signal | Number | Description | Docker |
|--------|--------|-------------|--------|
| SIGTERM | 15 | Termination request | docker stop |
| SIGINT | 2 | Interrupt (Ctrl+C) | docker attach |
| SIGKILL | 9 | Force termination | docker kill |
| SIGHUP | 1 | Configuration reload | — |

---

## Checklist

- [ ] SIGTERM handled
- [ ] SIGINT handled (for dev)
- [ ] Shutdown timeout configured
- [ ] Tasks cancelled gracefully
- [ ] State persisted on shutdown
- [ ] Shutdown events logged
