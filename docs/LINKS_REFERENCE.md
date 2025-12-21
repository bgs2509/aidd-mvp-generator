# Справочник ссылок AIDD-MVP Generator

> **Назначение**: Централизованный справочник всех важных ссылок в генераторе.
> Используйте этот файл для быстрого поиска нужного документа.

---

## Точки входа

| Файл | Описание | Когда читать |
|------|----------|--------------|
| [CLAUDE.md](../CLAUDE.md) | Главная точка входа | Первым делом |
| [conventions.md](../conventions.md) | Соглашения о коде | При написании кода |
| [workflow.md](../workflow.md) | 8-этапный процесс | При выполнении команд |

---

## Индексы и навигация

| Файл | Описание |
|------|----------|
| [docs/INDEX.md](INDEX.md) | Полный индекс файлов генератора |
| [docs/NAVIGATION.md](NAVIGATION.md) | Матрица "читать → создавать" |
| [docs/target-project-structure.md](target-project-structure.md) | Структура целевого проекта |

---

## Агенты (роли)

| Файл | Роль | Этап |
|------|------|------|
| [.claude/agents/analyst.md](../.claude/agents/analyst.md) | Аналитик | 1 |
| [.claude/agents/researcher.md](../.claude/agents/researcher.md) | Исследователь | 2 |
| [.claude/agents/architect.md](../.claude/agents/architect.md) | Архитектор | 3 |
| [.claude/agents/implementer.md](../.claude/agents/implementer.md) | Реализатор | 4 |
| [.claude/agents/reviewer.md](../.claude/agents/reviewer.md) | Ревьюер | 5 |
| [.claude/agents/qa.md](../.claude/agents/qa.md) | QA | 6 |
| [.claude/agents/validator.md](../.claude/agents/validator.md) | Валидатор | 7, 8 |

---

## Команды

| Файл | Команда | Этап |
|------|---------|------|
| [.claude/commands/idea.md](../.claude/commands/idea.md) | `/idea` | 1 |
| [.claude/commands/research.md](../.claude/commands/research.md) | `/research` | 2 |
| [.claude/commands/plan.md](../.claude/commands/plan.md) | `/plan` | 3 (CREATE) |
| [.claude/commands/feature-plan.md](../.claude/commands/feature-plan.md) | `/feature-plan` | 3 (FEATURE) |
| [.claude/commands/generate.md](../.claude/commands/generate.md) | `/generate` | 4 |
| [.claude/commands/review.md](../.claude/commands/review.md) | `/review` | 5 |
| [.claude/commands/test.md](../.claude/commands/test.md) | `/test` | 6 |
| [.claude/commands/validate.md](../.claude/commands/validate.md) | `/validate` | 7 |
| [.claude/commands/deploy.md](../.claude/commands/deploy.md) | `/deploy` | 8 |

---

## Шаблоны документов

| Шаблон (в генераторе) | Создаёт (в целевом проекте) |
|-----------------------|-----------------------------|
| [templates/documents/prd-template.md](../templates/documents/prd-template.md) | `ai-docs/docs/prd/{name}-prd.md` |
| [templates/documents/architecture-template.md](../templates/documents/architecture-template.md) | `ai-docs/docs/architecture/{name}-plan.md` |
| [templates/documents/feature-plan-template.md](../templates/documents/feature-plan-template.md) | `ai-docs/docs/plans/{feature}-plan.md` |
| [templates/documents/rtm-template.md](../templates/documents/rtm-template.md) | `ai-docs/docs/rtm.md` |
| [templates/documents/pipeline-state-template.json](../templates/documents/pipeline-state-template.json) | `.pipeline-state.json` |

---

## База знаний

### Архитектура

| Файл | Описание |
|------|----------|
| [knowledge/architecture/improved-hybrid.md](../knowledge/architecture/improved-hybrid.md) | Гибридная архитектура |
| [knowledge/architecture/ddd-hexagonal.md](../knowledge/architecture/ddd-hexagonal.md) | DDD и Hexagonal |
| [knowledge/architecture/project-structure.md](../knowledge/architecture/project-structure.md) | Структура проекта |

### Сервисы

| Файл | Описание |
|------|----------|
| [knowledge/services/fastapi.md](../knowledge/services/fastapi.md) | FastAPI сервисы |
| [knowledge/services/aiogram.md](../knowledge/services/aiogram.md) | Telegram боты |
| [knowledge/services/asyncio-workers.md](../knowledge/services/asyncio-workers.md) | Background workers |

### Качество

| Файл | Описание |
|------|----------|
| [knowledge/quality/testing/](../knowledge/quality/testing/) | Тестирование |
| [knowledge/quality/dry-kiss-yagni.md](../knowledge/quality/dry-kiss-yagni.md) | Принципы качества |

---

## Шаблоны сервисов

| Шаблон | Тип сервиса | Порт |
|--------|-------------|------|
| [templates/services/fastapi_business_api/](../templates/services/fastapi_business_api/) | Business API | 8000+ |
| [templates/services/aiogram_bot/](../templates/services/aiogram_bot/) | Telegram Bot | — |
| [templates/services/asyncio_worker/](../templates/services/asyncio_worker/) | Background Worker | — |
| [templates/services/postgres_data_api/](../templates/services/postgres_data_api/) | Data API (PostgreSQL) | 8001 |
| [templates/services/mongo_data_api/](../templates/services/mongo_data_api/) | Data API (MongoDB) | 8002 |

---

## Инфраструктура

| Файл | Описание |
|------|----------|
| [templates/infrastructure/docker-compose.yml](../templates/infrastructure/docker-compose.yml) | Docker Compose |
| [templates/infrastructure/Makefile](../templates/infrastructure/Makefile) | Makefile |
| [templates/infrastructure/nginx/](../templates/infrastructure/nginx/) | Nginx конфигурация |
| [templates/infrastructure/github-actions/](../templates/infrastructure/github-actions/) | CI/CD |

---

## Справочные материалы

| Файл | Описание |
|------|----------|
| [templates/documents/template-map.md](../templates/documents/template-map.md) | Карта шаблонов |
| [docs/reference/deliverables-catalog.md](reference/deliverables-catalog.md) | Каталог артефактов |

---

**Версия**: 1.0
**Создан**: 2025-12-21
