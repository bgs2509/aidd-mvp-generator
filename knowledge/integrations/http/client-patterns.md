# HTTP Client Patterns

> **Purpose**: Common patterns for HTTP clients.

---

## Base Client

```python
"""Base HTTP client."""

from typing import Any, TypeVar
import logging

import httpx

from {context}_api.core.exceptions import ExternalServiceError

T = TypeVar("T")
logger = logging.getLogger(__name__)


class BaseHttpClient:
    """Base class for HTTP clients."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        service_name: str = "external",
    ):
        """
        Initialize client.

        Args:
            client: HTTP client.
            base_url: Service base URL.
            service_name: Service name for logs.
        """
        self.client = client
        self.base_url = base_url.rstrip("/")
        self.service_name = service_name

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> dict[str, Any] | list | None:
        """
        Execute HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            path: API path.
            **kwargs: Additional httpx parameters.

        Returns:
            API response in JSON format.

        Raises:
            ExternalServiceError: On service error.
        """
        url = f"{self.base_url}{path}"

        logger.debug(f"Request: {method} {url}")

        try:
            response = await self.client.request(method, url, **kwargs)
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            raise ExternalServiceError(
                service=self.service_name,
                message=str(e),
            )

        logger.debug(f"Response: {response.status_code}")

        if response.status_code == 204:
            return None

        if response.status_code >= 400:
            self._handle_error(response)

        if not response.content:
            return None

        return response.json()

    def _handle_error(self, response: httpx.Response) -> None:
        """
        Handle response error.

        Args:
            response: HTTP response.

        Raises:
            ExternalServiceError: Always.
        """
        try:
            error_detail = response.json().get("detail", response.text)
        except Exception:
            error_detail = response.text

        raise ExternalServiceError(
            service=self.service_name,
            message=error_detail,
            status_code=response.status_code,
        )

    # Convenience methods

    async def get(self, path: str, **kwargs) -> dict | list | None:
        """GET request."""
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs) -> dict | None:
        """POST request."""
        return await self._request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs) -> dict | None:
        """PUT request."""
        return await self._request("PUT", path, **kwargs)

    async def patch(self, path: str, **kwargs) -> dict | None:
        """PATCH request."""
        return await self._request("PATCH", path, **kwargs)

    async def delete(self, path: str, **kwargs) -> None:
        """DELETE request."""
        await self._request("DELETE", path, **kwargs)
```

---

## Client with Retry

```python
"""HTTP client with retries."""

import asyncio
from typing import Any
import logging

import httpx

logger = logging.getLogger(__name__)


class RetryableHttpClient(BaseHttpClient):
    """HTTP client with automatic retries."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_statuses: tuple[int, ...] = (502, 503, 504),
    ):
        """
        Initialize.

        Args:
            client: HTTP client.
            base_url: Base URL.
            max_retries: Maximum attempts.
            retry_delay: Delay between attempts.
            retry_statuses: Statuses to retry on.
        """
        super().__init__(client, base_url)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_statuses = retry_statuses

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> dict[str, Any] | list | None:
        """Request with retry."""
        last_exception = None
        delay = self.retry_delay

        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(
                    method,
                    f"{self.base_url}{path}",
                    **kwargs,
                )

                if response.status_code in self.retry_statuses:
                    logger.warning(
                        f"Retryable status {response.status_code}, "
                        f"attempt {attempt + 1}/{self.max_retries}"
                    )
                    await asyncio.sleep(delay)
                    delay *= 2  # Exponential backoff
                    continue

                if response.status_code >= 400:
                    self._handle_error(response)

                if response.status_code == 204:
                    return None

                return response.json()

            except httpx.RequestError as e:
                logger.warning(
                    f"Request error: {e}, "
                    f"attempt {attempt + 1}/{self.max_retries}"
                )
                last_exception = e
                await asyncio.sleep(delay)
                delay *= 2

        raise ExternalServiceError(
            service=self.service_name,
            message=f"Max retries exceeded: {last_exception}",
        )
```

---

## Client with Circuit Breaker

```python
"""HTTP client with circuit breaker."""

import asyncio
from datetime import datetime, timedelta
from enum import Enum

import httpx


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failure, requests blocked
    HALF_OPEN = "half_open"  # Test mode


class CircuitBreaker:
    """Circuit breaker for cascading failure protection."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
    ):
        """
        Initialize.

        Args:
            failure_threshold: Failure threshold.
            recovery_timeout: Recovery time (sec).
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time: datetime | None = None

    def record_success(self) -> None:
        """Record successful request."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self) -> None:
        """Record failed request."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def can_execute(self) -> bool:
        """Check if request can be executed."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self._recovery_time_passed():
                self.state = CircuitState.HALF_OPEN
                return True
            return False

        return True  # HALF_OPEN

    def _recovery_time_passed(self) -> bool:
        """Check if recovery time has passed."""
        if self.last_failure_time is None:
            return True

        return datetime.now() > (
            self.last_failure_time + timedelta(seconds=self.recovery_timeout)
        )


class CircuitBreakerClient(BaseHttpClient):
    """HTTP client with circuit breaker."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        service_name: str = "external",
    ):
        """Initialize."""
        super().__init__(client, base_url, service_name)
        self.circuit = CircuitBreaker()

    async def _request(self, method: str, path: str, **kwargs):
        """Request with circuit breaker."""
        if not self.circuit.can_execute():
            raise ExternalServiceError(
                service=self.service_name,
                message="Circuit breaker is OPEN",
            )

        try:
            result = await super()._request(method, path, **kwargs)
            self.circuit.record_success()
            return result
        except Exception as e:
            self.circuit.record_failure()
            raise
```

---

## Client Creation

```python
"""HTTP client creation."""

import httpx

from {context}_api.core.config import settings


def create_http_client(
    base_url: str | None = None,
    timeout: float = 30.0,
) -> httpx.AsyncClient:
    """
    Create HTTP client.

    Args:
        base_url: Base URL.
        timeout: Request timeout.

    Returns:
        Configured HTTP client.
    """
    return httpx.AsyncClient(
        base_url=base_url,
        timeout=httpx.Timeout(timeout),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        follow_redirects=True,
    )


# In lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle."""
    app.state.http_client = create_http_client(
        base_url=settings.data_api_url,
    )

    yield

    await app.state.http_client.aclose()
```

---

## Checklist

- [ ] Base client with error handling
- [ ] Retry for unstable connections
- [ ] Circuit breaker for protection
- [ ] Timeouts configured
- [ ] Request logging
