# FastAPI Application Factory

> **Purpose**: FastAPI application creation pattern.

---

## Basic Pattern

```python
"""FastAPI application factory."""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from {context}_api.api.v1.router import api_router
from {context}_api.core.config import settings
from {context}_api.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    setup_logging()
    yield
    # Shutdown


def create_app() -> FastAPI:
    """
    Create FastAPI application instance.

    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(
        title=settings.service_name,
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Include routers
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
```

---

## With HTTP Client

```python
"""Factory with HTTP client management."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx

from {context}_api.api.v1.router import api_router
from {context}_api.core.config import settings
from {context}_api.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage lifecycle."""
    setup_logging()

    # Create HTTP client
    app.state.http_client = httpx.AsyncClient(
        base_url=settings.data_api_url,
        timeout=httpx.Timeout(30.0),
    )

    yield

    # Close HTTP client
    await app.state.http_client.aclose()


def create_app() -> FastAPI:
    """Create application."""
    app = FastAPI(
        title=settings.service_name,
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
```

---

## Middleware

```python
"""Adding middleware."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid


def create_app() -> FastAPI:
    """Create application with middleware."""
    app = FastAPI(
        title=settings.service_name,
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID middleware
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """Add request_id to request."""
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response

    # Timing middleware
    @app.middleware("http")
    async def add_timing(request: Request, call_next):
        """Measure request processing time."""
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        return response

    app.include_router(api_router, prefix="/api/v1")

    return app
```

---

## Health Check

```python
"""Health check endpoint."""

from fastapi import APIRouter, Response

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """
    Check service health.

    Returns:
        Service status.
    """
    return {"status": "healthy"}


@router.get("/ready")
async def readiness_check() -> dict:
    """
    Check service readiness.

    Returns:
        Readiness status.
    """
    # Dependency checks can be added here
    return {"status": "ready"}
```

---

## main.py Structure

```
main.py
├── Imports
├── lifespan() — lifecycle management
├── create_app() — application factory
│   ├── Create FastAPI
│   ├── Add middleware
│   └── Include routers
└── app = create_app()
```

---

## Checklist

- [ ] lifespan used for startup/shutdown
- [ ] HTTP client created in lifespan
- [ ] Docs disabled in production
- [ ] Request ID middleware added
- [ ] Health check endpoint present
