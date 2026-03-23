# Knowledge Base Index

> **Purpose**: Navigation through the AIDD-MVP Generator Knowledge Base.
> These are reference materials used by the AI agent during code generation.

---

## Architecture

| File | Description |
|------|----------|
| [architecture/ddd-hexagonal.md](architecture/ddd-hexagonal.md) | DDD/Hexagonal architecture |
| [architecture/project-structure.md](architecture/project-structure.md) | Project structure |
| [architecture/service-separation.md](architecture/service-separation.md) | Business/Data service separation |
| [architecture/data-access.md](architecture/data-access.md) | Data access patterns |
| [architecture/improved-hybrid.md](architecture/improved-hybrid.md) | Hybrid architecture |
| [architecture/event-loop.md](architecture/event-loop.md) | Event Loop in Python |
| [architecture/quality-standards.md](architecture/quality-standards.md) | Quality standards |

### Subfolder: naming/
| File | Description |
|------|----------|
| [architecture/naming/README.md](architecture/naming/README.md) | Naming conventions overview |
| [architecture/naming/python.md](architecture/naming/python.md) | Python naming |
| [architecture/naming/services.md](architecture/naming/services.md) | Service naming |

---

## Services

### FastAPI (5 files)
| File | Description |
|------|----------|
| [services/fastapi/application-factory.md](services/fastapi/application-factory.md) | Application Factory pattern |
| [services/fastapi/dependency-injection.md](services/fastapi/dependency-injection.md) | Dependency Injection |
| [services/fastapi/error-handling.md](services/fastapi/error-handling.md) | Error handling |
| [services/fastapi/routing-patterns.md](services/fastapi/routing-patterns.md) | Routing patterns |
| [services/fastapi/schema-validation.md](services/fastapi/schema-validation.md) | Schema validation (Pydantic) |

### Aiogram (4 files)
| File | Description |
|------|----------|
| [services/aiogram/basic-setup.md](services/aiogram/basic-setup.md) | Basic bot setup |
| [services/aiogram/handler-patterns.md](services/aiogram/handler-patterns.md) | Handler patterns |
| [services/aiogram/middleware-setup.md](services/aiogram/middleware-setup.md) | Middleware setup |
| [services/aiogram/state-management.md](services/aiogram/state-management.md) | State management (FSM) |

### Asyncio Workers (3 files)
| File | Description |
|------|----------|
| [services/asyncio-workers/basic-setup.md](services/asyncio-workers/basic-setup.md) | Basic worker setup |
| [services/asyncio-workers/task-management.md](services/asyncio-workers/task-management.md) | Task management |
| [services/asyncio-workers/signal-handling.md](services/asyncio-workers/signal-handling.md) | Signal handling (graceful shutdown) |

### Data Services (2 files)
| File | Description |
|------|----------|
| [services/data-services/postgres-setup.md](services/data-services/postgres-setup.md) | PostgreSQL setup |
| [services/data-services/repository-patterns.md](services/data-services/repository-patterns.md) | Repository pattern |

---

## Integrations

### HTTP (3 files)
| File | Description |
|------|----------|
| [integrations/http/client-patterns.md](integrations/http/client-patterns.md) | HTTP client patterns |
| [integrations/http/error-handling.md](integrations/http/error-handling.md) | HTTP error handling |
| [integrations/http/business-to-data.md](integrations/http/business-to-data.md) | Business API -> Data API |

### Redis (2 files)
| File | Description |
|------|----------|
| [integrations/redis/connection.md](integrations/redis/connection.md) | Redis connection |
| [integrations/redis/caching.md](integrations/redis/caching.md) | Caching patterns |

---

## Infrastructure

| File | Description |
|------|----------|
| [infrastructure/docker-compose.md](infrastructure/docker-compose.md) | Docker Compose configuration |
| [infrastructure/dockerfile.md](infrastructure/dockerfile.md) | Writing Dockerfiles |
| [infrastructure/nginx.md](infrastructure/nginx.md) | Nginx as API Gateway |
| [infrastructure/ci-cd.md](infrastructure/ci-cd.md) | CI/CD pipelines |
| [infrastructure/ssl.md](infrastructure/ssl.md) | SSL/TLS setup |

---

## Quality

### Testing (5 files)
| File | Description |
|------|----------|
| [quality/testing/pytest-setup.md](quality/testing/pytest-setup.md) | pytest setup |
| [quality/testing/fastapi-testing.md](quality/testing/fastapi-testing.md) | FastAPI testing |
| [quality/testing/fixture-patterns.md](quality/testing/fixture-patterns.md) | Fixture patterns |
| [quality/testing/mocking.md](quality/testing/mocking.md) | Mocking dependencies |
| [quality/testing/testcontainers.md](quality/testing/testcontainers.md) | Testcontainers for integration tests |

### Logging (3 files)
| File | Description |
|------|----------|
| [quality/logging/structured.md](quality/logging/structured.md) | Structured logging |
| [quality/logging/correlation.md](quality/logging/correlation.md) | Correlation ID |
| [quality/logging/log-driven-design.md](quality/logging/log-driven-design.md) | Log-Driven Design for AI agents |

### Principles
| File | Description |
|------|----------|
| [quality/dry-kiss-yagni.md](quality/dry-kiss-yagni.md) | DRY, KISS, YAGNI principles |
| [quality/production-requirements.md](quality/production-requirements.md) | Production-ready requirements |
| [quality/quality-cascade.md](quality/quality-cascade.md) | Quality Cascade -- early error detection |

---

## Pipeline

| File | Description |
|------|----------|
| [pipeline/state-v2.md](pipeline/state-v2.md) | Pipeline State v2: parallel pipelines |
| [pipeline/automigration.md](pipeline/automigration.md) | Automigration v1 -> v2 |
| [pipeline/git-integration.md](pipeline/git-integration.md) | Git integration for parallel pipelines |

---

## Security

| File | Description |
|------|----------|
| [security/secrets-management.md](security/secrets-management.md) | Secrets management |
| [security/docker-security.md](security/docker-security.md) | Docker security |
| [security/security-checklist.md](security/security-checklist.md) | Security checklist for AI agents |
| [security/vps-mode.md](security/vps-mode.md) | Read-only mode on production VPS |

---

## Quick Search

| Looking for | See |
|----|----------|
| How to structure FastAPI | `services/fastapi/` |
| How to test | `quality/testing/` |
| How to set up Docker | `infrastructure/docker-compose.md` |
| How to write a bot | `services/aiogram/` |
| HTTP client for Data API | `integrations/http/business-to-data.md` |
| Naming conventions | `architecture/naming/` |
| Parallel pipelines | `pipeline/state-v2.md` |
| State v1->v2 migration | `pipeline/automigration.md` |
| Git integration | `pipeline/git-integration.md` |
| Secrets management | `security/secrets-management.md` |
| Docker security | `security/docker-security.md` |
| Quality Cascade | `quality/quality-cascade.md` |

---

**Version**: 2.2
**Updated**: 2026-01-20
