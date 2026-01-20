# Справочник ссылок AIDD-MVP Generator

**Примечание:** В этом документе встречаются устаревшие команды `/aidd-idea`, `/aidd-generate`, `/aidd-finalize`, `/aidd-feature-plan`. Актуальные команды: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


> **Назначение**: Централизованный справочник всех важных ссылок в генераторе.
> Используйте этот файл для быстрого поиска нужного документа.

---

## Точки входа

| Файл | Описание | Когда читать |
|------|----------|--------------|
| [CLAUDE.md](../CLAUDE.md) | Главная точка входа | Первым делом |
| [conventions.md](../conventions.md) | Соглашения о коде | При написании кода |
| [workflow.md](../workflow.md) | 9-этапный процесс (0-8) | При выполнении команд |

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
| [.claude/agents/validator.md](../.claude/agents/validator.md) | Валидатор | 5 |

**Вспомогательные библиотеки инструкций** (используются внутри Валидатора):

| Файл | Назначение |
|------|-----------|
| [.claude/agents/code-review-library.md](../.claude/agents/code-review-library.md) | Детальные инструкции для Code Review (Шаг 1) |
| [.claude/agents/testing-library.md](../.claude/agents/testing-library.md) | Детальные инструкции для Testing (Шаг 2) |

---

## Команды

| Файл | Команда | Этап |
|------|---------|------|
| [.claude/commands/aidd-idea.md](../.claude/commands/aidd-idea.md) | `/aidd-idea` | 1 |
| [.claude/commands/aidd-research.md](../.claude/commands/aidd-research.md) | `/aidd-research` | 2 |
| [.claude/commands/aidd-plan.md](../.claude/commands/aidd-plan.md) | `/aidd-plan` | 3 (CREATE) |
| [.claude/commands/aidd-feature-plan.md](../.claude/commands/aidd-feature-plan.md) | `/aidd-feature-plan` | 3 (FEATURE) |
| [.claude/commands/aidd-generate.md](../.claude/commands/aidd-generate.md) | `/aidd-generate` | 4 |
| [.claude/commands/aidd-validate.md](../.claude/commands/aidd-validate.md) | `/aidd-validate` | 7 |

---

## Шаблоны документов

| Шаблон (в генераторе) | Создаёт (в целевом проекте) |
|-----------------------|-----------------------------|
| [templates/documents/prd-template.md](../templates/documents/prd-template.md) | `ai-docs/docs/prd/{name}-prd.md` |
| [templates/documents/research-report-template.md](../templates/documents/research-report-template.md) | `ai-docs/docs/research/{name}-research.md` |
| [templates/documents/architecture-template.md](../templates/documents/architecture-template.md) | `ai-docs/docs/architecture/{name}-plan.md` |
| [templates/documents/feature-plan-template.md](../templates/documents/feature-plan-template.md) | `ai-docs/docs/plans/{feature}-plan.md` |
| [templates/documents/completion-report-template.md](../templates/documents/completion-report-template.md) | `ai-docs/docs/reports/{YYYY-MM-DD}_{FID}_{slug}-completion.md` |
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

| Директория | Описание |
|------------|----------|
| [knowledge/services/fastapi/](../knowledge/services/fastapi/) | FastAPI сервисы |
| [knowledge/services/aiogram/](../knowledge/services/aiogram/) | Telegram боты |
| [knowledge/services/asyncio-workers/](../knowledge/services/asyncio-workers/) | Background workers |
| [knowledge/services/data-services/](../knowledge/services/data-services/) | Data API сервисы |

### Качество

| Файл | Описание |
|------|----------|
| [knowledge/quality/quality-cascade.md](../knowledge/quality/quality-cascade.md) | **Quality Cascade v2** — каскадные проверки |
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
