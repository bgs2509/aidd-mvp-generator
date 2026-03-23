# Production Requirements for MVP

> **Purpose**: Checklist of requirements for a production-ready MVP.
> Combines all deployment readiness criteria into a single document.

---

## Overview

A production-ready MVP must meet **Level 2** quality:
- Stable operation under load
- Correct error handling
- Monitoring and debugging capability
- Basic level of security

---

## 1. Health Checks

### Requirements

- [ ] Endpoint `/health` returns HTTP 200
- [ ] DB connection check
- [ ] Redis connection check (if used)
- [ ] External dependencies check

### Implementation Example

```python
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> JSONResponse:
    """Service health check."""
    checks = {
        "status": "healthy",
        "checks": {}
    }

    # DB check
    try:
        await db.execute(text("SELECT 1"))
        checks["checks"]["database"] = "ok"
    except Exception as e:
        checks["checks"]["database"] = f"error: {str(e)}"
        checks["status"] = "unhealthy"

    # Redis check
    try:
        await redis.ping()
        checks["checks"]["redis"] = "ok"
    except Exception as e:
        checks["checks"]["redis"] = f"error: {str(e)}"
        checks["status"] = "unhealthy"

    status_code = (
        status.HTTP_200_OK
        if checks["status"] == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(content=checks, status_code=status_code)
```

### Kubernetes Probes

```yaml
# In Deployment
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

---

## 2. Graceful Shutdown

### Requirements

- [ ] SIGTERM and SIGINT signal handling
- [ ] Completion of current HTTP requests
- [ ] Closing DB connections
- [ ] Closing Redis connections
- [ ] Shutdown timeout (default: 30s)

### FastAPI Example

```python
import signal
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    await init_database()
    await init_redis()

    yield

    # Shutdown
    await close_database()
    await close_redis()


app = FastAPI(lifespan=lifespan)
```

### AsyncIO Worker Example

```python
import signal
import asyncio


class GracefulShutdown:
    """Graceful shutdown handler."""

    def __init__(self):
        self.shutdown_event = asyncio.Event()

    def setup(self):
        """Set up signal handlers."""
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(self._shutdown(sig))
            )

    async def _shutdown(self, sig: signal.Signals):
        """Handle shutdown signal."""
        print(f"Received signal {sig.name}, shutting down...")
        self.shutdown_event.set()

    async def wait(self):
        """Wait for shutdown signal."""
        await self.shutdown_event.wait()
```

### Docker Stop Timeout

```yaml
# docker-compose.yml
services:
  api:
    stop_grace_period: 30s
```

---

## 3. Structured Logging

### Requirements

- [ ] JSON log format
- [ ] Request ID for tracing
- [ ] Log levels: DEBUG, INFO, WARNING, ERROR
- [ ] Contextual information (user_id, endpoint, etc.)
- [ ] Do not log sensitive data (passwords, tokens)

### Example with structlog

```python
import structlog
from uuid import uuid4


def setup_logging(json_logs: bool = True):
    """Set up structured logging."""
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Middleware for request_id
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request_id to each request."""
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    structlog.contextvars.bind_contextvars(request_id=request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response
```

### What NOT to Log

```python
SENSITIVE_FIELDS = {
    "password",
    "token",
    "secret",
    "api_key",
    "authorization",
    "credit_card",
}


def sanitize_log_data(data: dict) -> dict:
    """Remove sensitive data from logs."""
    return {
        k: "***REDACTED***" if k.lower() in SENSITIVE_FIELDS else v
        for k, v in data.items()
    }
```

---

## 4. Error Handling

### Requirements

- [ ] Centralized exception handling
- [ ] Different responses for dev and prod (stack trace only in dev)
- [ ] Logging of all unhandled exceptions
- [ ] Standardized error format

### Exception Handler Example

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error format."""

    error: str
    message: str
    request_id: str | None = None
    details: dict | None = None


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Global exception handler."""
    logger = structlog.get_logger()

    # Log the error
    logger.error(
        "Unhandled exception",
        exc_type=type(exc).__name__,
        exc_message=str(exc),
        path=request.url.path,
    )

    # Build response
    error_response = ErrorResponse(
        error="internal_server_error",
        message="Internal server error",
        request_id=request.headers.get("X-Request-ID"),
    )

    # In dev mode add details
    if settings.DEBUG:
        error_response.details = {
            "exception": type(exc).__name__,
            "message": str(exc),
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )
```

### Custom Exceptions

```python
class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 400,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} with ID {resource_id} not found",
            error_code="not_found",
            status_code=404,
        )
```

---

## 5. Configuration Management

### Requirements

- [ ] All secrets via environment variables
- [ ] Config validation at application startup
- [ ] Default values for optional parameters
- [ ] Config separation: dev / staging / prod
- [ ] No secrets in code or git

### Pydantic Settings Example

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Required
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str = Field(..., min_length=32)

    # Optional with defaults
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_PREFIX: str = "/api/v1"

    # Validation
    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL must be PostgreSQL")
        return v


# Singleton
settings = Settings()
```

### .env.example

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-at-least-32-characters

# Optional
DEBUG=false
LOG_LEVEL=INFO
```

---

## 6. Security

### Requirements

- [ ] HTTPS only in production
- [ ] CORS configured (not `*` in production)
- [ ] Rate limiting for public endpoints
- [ ] Input validation via Pydantic
- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection (output escaping)

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

# Production
ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]

# Development
if settings.DEBUG:
    ALLOWED_ORIGINS.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.get("/api/public")
@limiter.limit("10/minute")
async def public_endpoint(request: Request):
    """Public endpoint with rate limiting."""
    return {"message": "ok"}
```

### Input Validation

```python
from pydantic import BaseModel, Field, validator
import re


class UserCreate(BaseModel):
    """User creation schema."""

    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)

    @validator("email")
    def validate_email(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email")
        return v.lower()

    @validator("password")
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain a digit")
        return v
```

---

## 7. Monitoring & Metrics

### Requirements

- [ ] Request metrics (count, latency, errors)
- [ ] Business logic metrics (orders, users, etc.)
- [ ] Alerts for critical errors
- [ ] Dashboard for visualization

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Collect metrics for each request."""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
    ).inc()
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path,
    ).observe(duration)

    return response


@app.get("/metrics")
async def metrics():
    """Endpoint for Prometheus."""
    return Response(
        content=generate_latest(),
        media_type="text/plain",
    )
```

---

## 8. Pre-deployment Checklist

### Infrastructure

- [ ] Docker images build without errors
- [ ] docker-compose up starts all services
- [ ] Health checks pass for all services
- [ ] Volumes for persistent data are configured

### Code

- [ ] All tests pass (`pytest`)
- [ ] Coverage >=75%
- [ ] Linter passes (`ruff check`)
- [ ] Type checker passes (`mypy`)
- [ ] No placeholder/FIXME in critical code

### Security

- [ ] Secrets not in code or git
- [ ] .env.example is up to date
- [ ] CORS configured for production
- [ ] Rate limiting enabled

### Logging

- [ ] JSON log format
- [ ] Log level INFO or higher
- [ ] Sensitive data not logged

### Monitoring

- [ ] /health endpoint works
- [ ] /metrics endpoint works (if needed)
- [ ] Alerts configured

---

## Related Documents

| Document | Description |
|----------|----------|
| `knowledge/quality/logging/structured.md` | structlog setup |
| `knowledge/services/asyncio-workers/signal-handling.md` | Graceful shutdown |
| `knowledge/services/fastapi/application-factory.md` | Application Factory pattern |
| `knowledge/infrastructure/docker-compose.md` | Docker Compose configuration |
| `knowledge/infrastructure/ci-cd.md` | CI/CD pipeline |

---

**Document version**: 1.0
**Created**: 2025-12-20
