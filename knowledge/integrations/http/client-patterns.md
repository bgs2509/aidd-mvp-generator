# Паттерны HTTP клиентов

> **Назначение**: Общие паттерны для HTTP клиентов.

---

## Базовый клиент

```python
"""Базовый HTTP клиент."""

from typing import Any, TypeVar
import logging

import httpx

from {context}_api.core.exceptions import ExternalServiceError

T = TypeVar("T")
logger = logging.getLogger(__name__)


class BaseHttpClient:
    """Базовый класс для HTTP клиентов."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        service_name: str = "external",
    ):
        """
        Инициализация клиента.

        Args:
            client: HTTP клиент.
            base_url: Базовый URL сервиса.
            service_name: Имя сервиса для логов.
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
        Выполнить HTTP запрос.

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE).
            path: Путь API.
            **kwargs: Дополнительные параметры httpx.

        Returns:
            Ответ API в формате JSON.

        Raises:
            ExternalServiceError: При ошибке сервиса.
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
        Обработать ошибку ответа.

        Args:
            response: HTTP ответ.

        Raises:
            ExternalServiceError: Всегда.
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

    # Удобные методы

    async def get(self, path: str, **kwargs) -> dict | list | None:
        """GET запрос."""
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs) -> dict | None:
        """POST запрос."""
        return await self._request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs) -> dict | None:
        """PUT запрос."""
        return await self._request("PUT", path, **kwargs)

    async def patch(self, path: str, **kwargs) -> dict | None:
        """PATCH запрос."""
        return await self._request("PATCH", path, **kwargs)

    async def delete(self, path: str, **kwargs) -> None:
        """DELETE запрос."""
        await self._request("DELETE", path, **kwargs)
```

---

## Клиент с retry

```python
"""HTTP клиент с повторными попытками."""

import asyncio
from typing import Any
import logging

import httpx

logger = logging.getLogger(__name__)


class RetryableHttpClient(BaseHttpClient):
    """HTTP клиент с автоматическими retry."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_statuses: tuple[int, ...] = (502, 503, 504),
    ):
        """
        Инициализация.

        Args:
            client: HTTP клиент.
            base_url: Базовый URL.
            max_retries: Максимум попыток.
            retry_delay: Задержка между попытками.
            retry_statuses: Статусы для retry.
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
        """Запрос с retry."""
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

## Клиент с circuit breaker

```python
"""HTTP клиент с circuit breaker."""

import asyncio
from datetime import datetime, timedelta
from enum import Enum

import httpx


class CircuitState(Enum):
    """Состояния circuit breaker."""

    CLOSED = "closed"      # Нормальная работа
    OPEN = "open"          # Отказ, запросы блокируются
    HALF_OPEN = "half_open"  # Тестовый режим


class CircuitBreaker:
    """Circuit breaker для защиты от каскадных отказов."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
    ):
        """
        Инициализация.

        Args:
            failure_threshold: Порог отказов.
            recovery_timeout: Время восстановления (сек).
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time: datetime | None = None

    def record_success(self) -> None:
        """Записать успешный запрос."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self) -> None:
        """Записать неудачный запрос."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def can_execute(self) -> bool:
        """Проверить, можно ли выполнить запрос."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self._recovery_time_passed():
                self.state = CircuitState.HALF_OPEN
                return True
            return False

        return True  # HALF_OPEN

    def _recovery_time_passed(self) -> bool:
        """Проверить, прошло ли время восстановления."""
        if self.last_failure_time is None:
            return True

        return datetime.now() > (
            self.last_failure_time + timedelta(seconds=self.recovery_timeout)
        )


class CircuitBreakerClient(BaseHttpClient):
    """HTTP клиент с circuit breaker."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        service_name: str = "external",
    ):
        """Инициализация."""
        super().__init__(client, base_url, service_name)
        self.circuit = CircuitBreaker()

    async def _request(self, method: str, path: str, **kwargs):
        """Запрос с circuit breaker."""
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

## Создание клиента

```python
"""Создание HTTP клиента."""

import httpx

from {context}_api.core.config import settings


def create_http_client(
    base_url: str | None = None,
    timeout: float = 30.0,
) -> httpx.AsyncClient:
    """
    Создать HTTP клиент.

    Args:
        base_url: Базовый URL.
        timeout: Таймаут запроса.

    Returns:
        Настроенный HTTP клиент.
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


# В lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл."""
    app.state.http_client = create_http_client(
        base_url=settings.data_api_url,
    )

    yield

    await app.state.http_client.aclose()
```

---

## Чек-лист

- [ ] Базовый клиент с обработкой ошибок
- [ ] Retry для нестабильных соединений
- [ ] Circuit breaker для защиты
- [ ] Таймауты настроены
- [ ] Логирование запросов
