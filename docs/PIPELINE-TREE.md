# PIPELINE-TREE.md — Дерево пайплайнов AIDD-MVP

**Примечание:** В этом документе встречаются устаревшие команды `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Актуальные команды: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


> **Назначение**: Полная карта всех пайплайнов фреймворка.
> Для каждого пайплайна указаны: команда, агент, ворота, артефакты, источники файлов.

---

## Визуальное дерево пайплайнов

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          AIDD-MVP PIPELINE TREE                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────┐                                                                │
│  │   ЭТАП 0     │  Bootstrap Pipeline                                           │
│  │   /aidd-init      │  ────────────────────────────────────────────────────────────  │
│  │              │  Инициализация целевого проекта                               │
│  └──────┬───────┘                                                                │
│         │ BOOTSTRAP_READY                                                        │
│         ▼                                                                        │
│  ┌──────────────┐                                                                │
│  │   ЭТАП 1     │  Idea Pipeline                                                │
│  │   /aidd-analyze      │  ────────────────────────────────────────────────────────────  │
│  │              │  Создание PRD документа                                       │
│  └──────┬───────┘                                                                │
│         │ PRD_READY                                                              │
│         ▼                                                                        │
│  ┌──────────────┐                                                                │
│  │   ЭТАП 2     │  Research Pipeline                                            │
│  │   /aidd-research  │  ────────────────────────────────────────────────────────────  │
│  │              │  Исследование и анализ                                        │
│  └──────┬───────┘                                                                │
│         │ RESEARCH_DONE                                                          │
│         ▼                                                                        │
│  ┌──────────────┐                                                                │
│  │   ЭТАП 3     │  Architecture Pipeline                                        │
│  │ /aidd-plan или    │  ────────────────────────────────────────────────────────────  │
│  │ /feature-plan│  Проектирование архитектуры                                   │
│  └──────┬───────┘                                                                │
│         │ PLAN_APPROVED (требует подтверждения пользователя)                     │
│         ▼                                                                        │
│  ┌──────────────┐                                                                │
│  │   ЭТАП 4     │  Implementation Pipeline                                       │
│  │   /aidd-code  │  ────────────────────────────────────────────────────────────  │
│  │              │  Генерация кода                                               │
│  └──────┬───────┘                                                                │
│         │ IMPLEMENT_OK                                                           │
│         ▼                                                                        │
│  ┌───────────────────────────────────────────────────────────────┐              │
│  │   ЭТАП 5: Quality & Deploy Pipeline (/aidd-validate)          │              │
│  │  ──────────────────────────────────────────────────────────── │              │
│  │                                                                │              │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────────────┐      │              │
│  │  │ Review │─▶│  Test  │─▶│Validate│─▶│Deploy + Report │      │              │
│  │  └────┬───┘  └────┬───┘  └────┬───┘  └────┬───────────┘      │              │
│  │       │           │           │            │                  │              │
│  │  REVIEW_OK    QA_PASSED  ALL_GATES     DEPLOYED              │              │
│  │                                 PASSED                        │              │
│  │                                                                │              │
│  │  Артефакт: 1 Completion Report (вместо 4 файлов)             │              │
│  └────────────────────────────────┬───────────────────────────────┘              │
│                                   │                                              │
│                                   ▼                                              │
│                              ✅ MVP ГОТОВ                                        │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Детальное описание пайплайнов

### Этап 0: Bootstrap Pipeline

| Параметр | Значение |
|----------|----------|
| **Команда** | `/aidd-init` (ручной) или авто с `/aidd-analyze` |
| **Агент** | — (системный) |
| **Предусловия** | — |
| **Качественные ворота** | `BOOTSTRAP_READY` |

#### Проверки

| # | Проверка | Команда/Файл | Критерий |
|---|----------|--------------|----------|
| 1 | Git репозиторий | `git rev-parse --git-dir` | Выход 0 |
| 2 | Фреймворк подключен | `.aidd/CLAUDE.md` | Файл существует |
| 3 | Python версия | `python3 --version` | >= 3.11 |
| 4 | Docker | `docker --version` | Установлен |

#### Действия

| # | Действие | Результат |
|---|----------|-----------|
| 1 | Создать структуру папок | `ai-docs/docs/{prd,architecture,plans,reports,research}` |
| 2 | Создать состояние пайплайна | `.pipeline-state.json` |
| 3 | Создать CLAUDE.md | `./CLAUDE.md` → ссылка на `.aidd/CLAUDE.md` |

#### Источники файлов

| Файл | Источник | Путь |
|------|----------|------|
| Инструкции команды | Фреймворк | `.aidd/.claude/commands/aidd-init.md` |
| CLAUDE.md (шаблон) | Фреймворк | `.aidd/CLAUDE.md` |
| Структура ЦП | Фреймворк | `.aidd/docs/target-project-structure.md` |
| **Результат** | ЦП | `./CLAUDE.md`, `./ai-docs/docs/`, `./.pipeline-state.json` |

---

### Этап 1: Idea Pipeline (PRD)

| Параметр | Значение |
|----------|----------|
| **Команда** | `/idea "описание"` |
| **Агент** | Аналитик |
| **Предусловия** | `BOOTSTRAP_READY` (или авто-bootstrap) |
| **Качественные ворота** | `PRD_READY` |

#### Входные артефакты

| Артефакт | Источник | Путь |
|----------|----------|------|
| Описание идеи | Пользователь | Аргумент команды |
| Шаблон PRD | Фреймворк | `.aidd/templates/documents/prd-template.md` |

#### Выходные артефакты

| Артефакт | Путь в ЦП |
|----------|-----------|
| PRD документ | `ai-docs/docs/_analysis/{name}-prd.md` |
| Состояние | `.pipeline-state.json` (обновлено) |

#### Источники файлов

| Файл | Источник | Путь |
|------|----------|------|
| Инструкции команды | Фреймворк | `.aidd/.claude/commands/aidd-analyze.md` |
| Инструкции агента | Фреймворк | `.aidd/.claude/agents/analyst.md` |
| Шаблон PRD | Фреймворк | `.aidd/templates/documents/prd-template.md` |
| Workflow | Фреймворк | `.aidd/workflow.md` |
| **Результат** | ЦП | `ai-docs/docs/_analysis/{name}-prd.md` |

---

### Этап 2: Research Pipeline

| Параметр | Значение |
|----------|----------|
| **Команда** | `/aidd-research` |
| **Агент** | Исследователь |
| **Предусловия** | `PRD_READY` |
| **Качественные ворота** | `RESEARCH_DONE` |

#### Входные артефакты

| Артефакт | Источник | Путь |
|----------|----------|------|
| PRD | ЦП | `ai-docs/docs/_analysis/{name}-prd.md` |
| Существующий код | ЦП | `services/` (для FEATURE) |

#### Выходные артефакты

| Артефакт | Путь в ЦП |
|----------|-----------|
| Отчёт исследования | `ai-docs/docs/research/{name}-research.md` |
| Состояние | `.pipeline-state.json` (обновлено) |

#### Источники файлов

| Файл | Источник | Путь |
|------|----------|------|
| Инструкции команды | Фреймворк | `.aidd/.claude/commands/aidd-research.md` |
| Инструкции агента | Фреймворк | `.aidd/.claude/agents/researcher.md` |
| Детальные инструкции | Фреймворк | `.aidd/roles/researcher/*.md` |
| Шаблон отчёта | Фреймворк | `.aidd/templates/documents/research-report-template.md` |
| PRD | ЦП | `ai-docs/docs/_analysis/{name}-prd.md` |

---

### Этап 3: Architecture Pipeline

| Параметр | Значение CREATE | Значение FEATURE |
|----------|-----------------|------------------|
| **Команда** | `/aidd-plan` | `/aidd-plan-feature` |
| **Агент** | Архитектор | Архитектор |
| **Предусловия** | `PRD_READY`, `RESEARCH_DONE` | `PRD_READY`, `RESEARCH_DONE` |
| **Качественные ворота** | `PLAN_APPROVED` | `PLAN_APPROVED` |

#### Входные артефакты

| Артефакт | Источник | Путь |
|----------|----------|------|
| PRD | ЦП | `ai-docs/docs/_analysis/{name}-prd.md` |
| Отчёт исследования | ЦП | `ai-docs/docs/research/{name}-research.md` |
| Шаблон архитектуры | Фреймворк | `.aidd/templates/documents/architecture-template.md` |

#### Выходные артефакты

| Артефакт | Путь в ЦП (CREATE) | Путь в ЦП (FEATURE) |
|----------|-------------------|---------------------|
| План архитектуры | `ai-docs/docs/_plans/mvp/{name}-plan.md` | — |
| План фичи | — | `ai-docs/docs/_plans/features/{feature}-plan.md` |

#### Источники файлов

| Файл | Источник | Путь |
|------|----------|------|
| Инструкции команды | Фреймворк | `.aidd/.claude/commands/aidd-plan.md` или `aidd-feature-plan.md` |
| Инструкции агента | Фреймворк | `.aidd/.claude/agents/planner.md` |
| Детальные инструкции | Фреймворк | `.aidd/roles/architect/*.md` |
| База знаний | Фреймворк | `.aidd/knowledge/architecture/*.md` |
| **Результат** | ЦП | `ai-docs/docs/_plans/mvp/` или `ai-docs/docs/_plans/features/` |

---

### Этап 4: Implementation Pipeline

| Параметр | Значение |
|----------|----------|
| **Команда** | `/aidd-code` |
| **Агент** | Реализатор |
| **Предусловия** | `PLAN_APPROVED` |
| **Качественные ворота** | `IMPLEMENT_OK` |

#### Входные артефакты

| Артефакт | Источник | Путь |
|----------|----------|------|
| План | ЦП | `ai-docs/docs/_plans/mvp/{name}-plan.md` |
| Шаблоны сервисов | Фреймворк | `.aidd/templates/services/` |
| Шаблоны инфраструктуры | Фреймворк | `.aidd/templates/infrastructure/` |
| Shared компоненты | Фреймворк | `.aidd/templates/shared/` |

#### Выходные артефакты

| Артефакт | Путь в ЦП |
|----------|-----------|
| Business API | `services/{name}_api/` |
| Data API | `services/{name}_data/` |
| Telegram Bot | `services/{name}_bot/` |
| Background Worker | `services/{name}_worker/` |
| Docker Compose | `docker-compose.yml` |
| Makefile | `Makefile` |
| Nginx | `nginx/` |

#### Источники файлов

| Файл | Источник | Путь |
|------|----------|------|
| Инструкции команды | Фреймворк | `.aidd/.claude/commands/aidd-code.md` |
| Инструкции агента | Фреймворк | `.aidd/.claude/agents/coder.md` |
| Детальные инструкции | Фреймворк | `.aidd/roles/implementer/*.md` |
| Шаблон FastAPI | Фреймворк | `.aidd/templates/services/fastapi_business_api/` |
| Шаблон Data API | Фреймворк | `.aidd/templates/services/postgres_data_api/` |
| Шаблон Bot | Фреймворк | `.aidd/templates/services/aiogram_bot/` |
| Шаблон Worker | Фреймворк | `.aidd/templates/services/asyncio_worker/` |
| База знаний | Фреймворк | `.aidd/knowledge/services/*.md` |
| Conventions | Фреймворк | `.aidd/conventions.md` |
| **Результат** | ЦП | `services/`, `docker-compose.yml`, `Makefile` |

---

### Этап 5: Quality & Deploy Pipeline

| Параметр | Значение |
|----------|----------|
| **Команда** | `/aidd-validate` (или `/aidd-validate` в v2.4+) |
| **Агент** | Валидатор |
| **Предусловия** | `IMPLEMENT_OK` |
| **Качественные ворота** | `REVIEW_OK` → `QA_PASSED` → `ALL_GATES_PASSED` → `DEPLOYED` |

#### Описание

Этап Quality & Deploy выполняет полный цикл проверки качества и деплоя в 4 последовательных шага:

1. **Code Review** → `REVIEW_OK`
2. **Testing** → `QA_PASSED`
3. **Validation** → `ALL_GATES_PASSED`
4. **Deploy & Completion Report** → `DEPLOYED`

#### Входные артефакты

| Артефакт | Источник | Путь |
|----------|----------|------|
| Код сервисов | ЦП | `services/` |
| PRD | ЦП | `ai-docs/docs/_analysis/{name}-prd.md` |
| План | ЦП | `ai-docs/docs/_plans/mvp/{name}-plan.md` |
| Docker Compose | ЦП | `docker-compose.yml` |
| Makefile | ЦП | `Makefile` |
| Состояние | ЦП | `.pipeline-state.json` |

#### Выходные артефакты

| Артефакт | Путь в ЦП |
|----------|-----------|
| **Completion Report** | `ai-docs/docs/_validation/{YYYY-MM-DD}_{FID}_{slug}-completion.md` |

**Completion Report содержит** (единственный артефакт вместо 4 файлов):
- Executive Summary
- Code Review Summary
- Testing Summary
- Requirements Traceability
- ADR (Architecture Decision Records)
- Scope Changes
- Known Limitations
- Метрики качества

#### Два режима работы

| Режим | Ворота | Артефакт |
|-------|--------|----------|
| **Полный** (рекомендуется) | `REVIEW_OK` → `QA_PASSED` → `ALL_GATES_PASSED` → `DEPLOYED` | Production-ready Completion Report |
| **Быстрый** | `DOCUMENTED` | DRAFT Completion Report (только static analysis) |

#### Действия (Полный режим)

| Шаг | Действия | Проверки |
|-----|----------|----------|
| 1. Review | Quality Cascade (17 проверок), Security checklist | DDD, HTTP-only, conventions.md |
| 2. Test | `pytest --cov --cov-fail-under=75` | Coverage ≥75%, все FR-* |
| 3. Validate | Проверка всех ворот, финальная security проверка | ALL_GATES_PASSED |
| 4. Deploy | `make build && make up && make health` | Контейнеры запущены, Completion Report создан |

#### Источники файлов

| Файл | Источник | Путь |
|------|----------|------|
| Инструкции команды | Фреймворк | `.aidd/.claude/commands/aidd-validate.md` |
| Инструкции агента | Фреймворк | `.aidd/.claude/agents/validator.md` |
| **Библиотека Code Review** | Фреймворк | `.aidd/.claude/agents/code-review-library.md` |
| **Библиотека Testing** | Фреймворк | `.aidd/.claude/agents/testing-library.md` |
| Conventions | Фреймворк | `.aidd/conventions.md` |
| Quality Cascade | Фреймворк | `.aidd/knowledge/quality/quality-cascade.md` |
| Security Checklist | Фреймворк | `.aidd/knowledge/security/security-checklist.md` |
| Шаблон Completion Report | Фреймворк | `.aidd/templates/documents/completion-report-template.md` |
| **Результат** | ЦП | `ai-docs/docs/_validation/{date}_{FID}_{slug}-completion.md` |

---

## Сводная таблица пайплайнов

| # | Этап | Команда | Агент | Ворота | Выходной артефакт |
|---|------|---------|-------|--------|-------------------|
| 0 | Bootstrap | `/aidd-init` | — | `BOOTSTRAP_READY` | Структура ЦП |
| 1 | Идея | `/aidd-analyze` | Аналитик | `PRD_READY` | PRD документ |
| 2 | Исследование | `/aidd-research` | Исследователь | `RESEARCH_DONE` | Research Report (`ai-docs/docs/research/{name}-research.md`) |
| 3 | Архитектура | `/aidd-plan` | Архитектор | `PLAN_APPROVED` | План архитектуры |
| 3 | Архитектура | `/aidd-plan-feature` | Архитектор | `PLAN_APPROVED` | План фичи |
| 4 | Реализация | `/aidd-code` | Реализатор | `IMPLEMENT_OK` | Код сервисов |
| 5 | Quality & Deploy | `/aidd-validate` | Валидатор | `REVIEW_OK` → `QA_PASSED` → `ALL_GATES_PASSED` → `DEPLOYED` | **Completion Report** (`ai-docs/docs/_validation/{date}_{FID}_{slug}-completion.md`) |

---

## Матрица источников файлов

| Категория | Источник | Примеры путей |
|-----------|----------|---------------|
| **Инструкции команд** | Фреймворк | `.aidd/.claude/commands/*.md` |
| **Инструкции агентов** | Фреймворк | `.aidd/.claude/agents/*.md` |
| **Детальные роли** | Фреймворк | `.aidd/roles/*/*.md` |
| **Шаблоны документов** | Фреймворк | `.aidd/templates/documents/*.md` |
| **Шаблоны сервисов** | Фреймворк | `.aidd/templates/services/*/` |
| **Шаблоны инфраструктуры** | Фреймворк | `.aidd/templates/infrastructure/*/` |
| **База знаний** | Фреймворк | `.aidd/knowledge/*/*.md` |
| **Conventions** | Фреймворк | `.aidd/conventions.md` |
| **Workflow** | Фреймворк | `.aidd/workflow.md` |
| **PRD** | ЦП | `ai-docs/docs/_analysis/*.md` |
| **Планы** | ЦП | `ai-docs/docs/_plans/mvp/*.md`, `ai-docs/docs/_plans/features/*.md` |
| **Отчёты исследования** | ЦП | `ai-docs/docs/research/*.md` |
| **Отчёты** | ЦП | `ai-docs/docs/_validation/*.md` |
| **RTM** | ЦП | `ai-docs/docs/rtm.md` |
| **Код сервисов** | ЦП | `services/*/` |
| **Инфраструктура** | ЦП | `docker-compose.yml`, `Makefile`, `nginx/` |
| **Состояние** | ЦП | `.pipeline-state.json` |

---

## См. также

- [workflow.md](../workflow.md) — Детальное описание процесса
- [initialization.md](initialization.md) — Алгоритм инициализации
- [INDEX.md](INDEX.md) — Индекс файлов фреймворка
- [NAVIGATION.md](NAVIGATION.md) — Навигационная матрица

---

**Версия**: 1.0
**Создан**: 2025-12-21
**Назначение**: Полная карта пайплайнов AIDD-MVP Generator
