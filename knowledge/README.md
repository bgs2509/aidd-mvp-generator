# Knowledge Base Index

> **Назначение**: Навигация по базе знаний AIDD-MVP Generator.
> Это справочные материалы, используемые AI-агентом при генерации кода.

---

## Архитектура

| Файл | Описание |
|------|----------|
| [architecture/ddd-hexagonal.md](architecture/ddd-hexagonal.md) | DDD/Hexagonal архитектура |
| [architecture/project-structure.md](architecture/project-structure.md) | Структура проекта |
| [architecture/service-separation.md](architecture/service-separation.md) | Разделение Business/Data сервисов |
| [architecture/data-access.md](architecture/data-access.md) | Паттерны доступа к данным |
| [architecture/improved-hybrid.md](architecture/improved-hybrid.md) | Гибридная архитектура |
| [architecture/event-loop.md](architecture/event-loop.md) | Event Loop в Python |
| [architecture/quality-standards.md](architecture/quality-standards.md) | Стандарты качества |

### Подпапка: naming/
| Файл | Описание |
|------|----------|
| [architecture/naming/README.md](architecture/naming/README.md) | Обзор конвенций именования |
| [architecture/naming/python.md](architecture/naming/python.md) | Python именование |
| [architecture/naming/services.md](architecture/naming/services.md) | Именование сервисов |

---

## Сервисы

### FastAPI (5 файлов)
| Файл | Описание |
|------|----------|
| [services/fastapi/application-factory.md](services/fastapi/application-factory.md) | Паттерн Application Factory |
| [services/fastapi/dependency-injection.md](services/fastapi/dependency-injection.md) | Dependency Injection |
| [services/fastapi/error-handling.md](services/fastapi/error-handling.md) | Обработка ошибок |
| [services/fastapi/routing-patterns.md](services/fastapi/routing-patterns.md) | Паттерны роутинга |
| [services/fastapi/schema-validation.md](services/fastapi/schema-validation.md) | Валидация схем (Pydantic) |

### Aiogram (4 файла)
| Файл | Описание |
|------|----------|
| [services/aiogram/basic-setup.md](services/aiogram/basic-setup.md) | Базовая настройка бота |
| [services/aiogram/handler-patterns.md](services/aiogram/handler-patterns.md) | Паттерны обработчиков |
| [services/aiogram/middleware-setup.md](services/aiogram/middleware-setup.md) | Настройка middleware |
| [services/aiogram/state-management.md](services/aiogram/state-management.md) | Управление состоянием (FSM) |

### Asyncio Workers (3 файла)
| Файл | Описание |
|------|----------|
| [services/asyncio-workers/basic-setup.md](services/asyncio-workers/basic-setup.md) | Базовая настройка воркера |
| [services/asyncio-workers/task-management.md](services/asyncio-workers/task-management.md) | Управление задачами |
| [services/asyncio-workers/signal-handling.md](services/asyncio-workers/signal-handling.md) | Обработка сигналов (graceful shutdown) |

### Data Services (2 файла)
| Файл | Описание |
|------|----------|
| [services/data-services/postgres-setup.md](services/data-services/postgres-setup.md) | Настройка PostgreSQL |
| [services/data-services/repository-patterns.md](services/data-services/repository-patterns.md) | Паттерн Repository |

---

## Интеграции

### HTTP (3 файла)
| Файл | Описание |
|------|----------|
| [integrations/http/client-patterns.md](integrations/http/client-patterns.md) | Паттерны HTTP-клиентов |
| [integrations/http/error-handling.md](integrations/http/error-handling.md) | Обработка ошибок HTTP |
| [integrations/http/business-to-data.md](integrations/http/business-to-data.md) | Business API → Data API |

### Redis (2 файла)
| Файл | Описание |
|------|----------|
| [integrations/redis/connection.md](integrations/redis/connection.md) | Подключение к Redis |
| [integrations/redis/caching.md](integrations/redis/caching.md) | Паттерны кеширования |

---

## Инфраструктура

| Файл | Описание |
|------|----------|
| [infrastructure/docker-compose.md](infrastructure/docker-compose.md) | Docker Compose конфигурация |
| [infrastructure/dockerfile.md](infrastructure/dockerfile.md) | Написание Dockerfile |
| [infrastructure/nginx.md](infrastructure/nginx.md) | Nginx как API Gateway |
| [infrastructure/ci-cd.md](infrastructure/ci-cd.md) | CI/CD пайплайны |
| [infrastructure/ssl.md](infrastructure/ssl.md) | SSL/TLS настройка |

---

## Качество

### Тестирование (5 файлов)
| Файл | Описание |
|------|----------|
| [quality/testing/pytest-setup.md](quality/testing/pytest-setup.md) | Настройка pytest |
| [quality/testing/fastapi-testing.md](quality/testing/fastapi-testing.md) | Тестирование FastAPI |
| [quality/testing/fixture-patterns.md](quality/testing/fixture-patterns.md) | Паттерны фикстур |
| [quality/testing/mocking.md](quality/testing/mocking.md) | Мокирование зависимостей |
| [quality/testing/testcontainers.md](quality/testing/testcontainers.md) | Testcontainers для интеграционных тестов |

### Логирование (2 файла)
| Файл | Описание |
|------|----------|
| [quality/logging/structured.md](quality/logging/structured.md) | Структурированное логирование |
| [quality/logging/correlation.md](quality/logging/correlation.md) | Correlation ID |

### Принципы
| Файл | Описание |
|------|----------|
| [quality/dry-kiss-yagni.md](quality/dry-kiss-yagni.md) | Принципы DRY, KISS, YAGNI |
| [quality/production-requirements.md](quality/production-requirements.md) | Production-ready требования |

---

## Pipeline

| Файл | Описание |
|------|----------|
| [pipeline/state-v2.md](pipeline/state-v2.md) | Pipeline State v2: параллельные пайплайны |
| [pipeline/automigration.md](pipeline/automigration.md) | Автомиграция v1 → v2 |

---

## Быстрый поиск

| Ищу | Смотреть |
|----|----------|
| Как структурировать FastAPI | `services/fastapi/` |
| Как тестировать | `quality/testing/` |
| Как настроить Docker | `infrastructure/docker-compose.md` |
| Как писать бота | `services/aiogram/` |
| HTTP-клиент для Data API | `integrations/http/business-to-data.md` |
| Конвенции именования | `architecture/naming/` |
| Параллельные пайплайны | `pipeline/state-v2.md` |
| Миграция state v1→v2 | `pipeline/automigration.md` |

---

**Версия**: 2.1
**Обновлён**: 2025-12-25
