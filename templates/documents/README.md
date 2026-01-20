# Шаблоны документов AIDD-MVP

Шаблоны для генерации документации на каждом этапе пайплайна разработки.

## Содержимое

| Шаблон | Назначение | Этап | Агент |
|--------|------------|------|-------|
| `prd-template.md` | Product Requirements Document | Stage 1 | Аналитик |
| `research-report-template.md` | Research Report | Stage 2 | Исследователь |
| `architecture-template.md` | Архитектурный план (CREATE mode) | Stage 3 | Архитектор / Планировщик |
| `feature-plan-template.md` | План фичи (FEATURE mode) | Stage 3 | Архитектор / Планировщик |
| `implementation-plan-template.md` | План реализации | Stage 3 | Архитектор / Планировщик |
| `completion-report-template.md` | Completion Report (Review + Test + Validation) | Stage 5 | Валидатор |

> **Примечание**: Consolidation Stage 5 — роли Ревьюер, QA, и старый Валидатор объединены в одну роль **Валидатор**, выполняющую 4 шага: Review → Test → Validate → Deploy. Три отдельных отчета (`review-report`, `qa-report`, `validation-report`) заменены на единый **Completion Report**.

## Использование

### 1. PRD Template

Используется Аналитиком для формирования требований:

```bash
/aidd-idea "Описание проекта или фичи"
# или (migration mode v2.4+)
/aidd-analyze "Описание проекта или фичи"
```

**Выходной файл** (целевой проект):
- **naming v2** (по умолчанию): `ai-docs/docs/prd/{date}_{FID}_{slug}-prd.md`
- **naming v3**: `ai-docs/docs/_analysis/{date}_{FID}_{slug}.md`

### 2. Research Report Template

Используется Исследователем после анализа требований/кода:

```bash
/aidd-research
```

**Выходной файл** (целевой проект):
- **naming v2**: `ai-docs/docs/research/{date}_{FID}_{slug}-research.md`
- **naming v3**: `ai-docs/docs/_research/{date}_{FID}_{slug}.md`

### 3. Architecture Template

Используется Архитектором/Планировщиком для проектирования (CREATE mode):

```bash
/aidd-plan
```

**Выходной файл** (целевой проект):
- **naming v2**: `ai-docs/docs/architecture/{date}_{FID}_{slug}-plan.md`
- **naming v3**: `ai-docs/docs/_plans/mvp/{date}_{FID}_{slug}.md`

### 4. Feature Plan Template

Используется Архитектором/Планировщиком для планирования фичи (FEATURE mode):

```bash
/aidd-feature-plan
# или (migration mode v2.4+)
/aidd-plan-feature
```

**Выходной файл** (целевой проект):
- **naming v2**: `ai-docs/docs/plans/{date}_{FID}_{slug}-plan.md`
- **naming v3**: `ai-docs/docs/_plans/features/{date}_{FID}_{slug}.md`

### 5. Implementation Plan Template

Используется Архитектором/Планировщиком для детального планирования реализации:

```bash
/aidd-plan
# или
/aidd-feature-plan  # для FEATURE mode
```

**Выходной файл** (целевой проект):
- **naming v2**: `ai-docs/docs/plans/{date}_{FID}_{slug}-implementation.md`
- **naming v3**: `ai-docs/docs/_plans/mvp/{date}_{FID}_{slug}-implementation.md` или `_plans/features/{date}_{FID}_{slug}-implementation.md`

### 6. Completion Report Template

Используется Валидатором для комплексного Quality & Deploy (Stage 5):

```bash
/aidd-finalize
# или (migration mode v2.4+)
/aidd-validate
```

**Режимы**:
- **Full** (по умолчанию): Review → Test → Validate → Deploy → Production-ready MVP
- **Quick**: Draft Completion Report + Static Analysis (для документации/незавершенных фич)

**Выходной файл** (целевой проект):
- **naming v2**: `ai-docs/docs/reports/{date}_{FID}_{slug}-completion.md`
- **naming v3**: `ai-docs/docs/_validation/{date}_{FID}_{slug}.md`

**Содержание Completion Report**:
1. Executive Summary — что сделано (2-3 предложения)
2. Code Review Summary — результаты проверки качества
3. Testing Summary — результаты тестирования
4. Requirements Traceability — соответствие требованиям
5. ADR — архитектурные решения
6. Scope Changes — отклонения от плана
7. Known Limitations — ограничения и workarounds
8. Метрики — coverage, tests, security
9. Ссылки — на все артефакты

## Структура директории ai-docs (в целевом проекте)

### naming v2 (по умолчанию)

```
{целевой-проект}/
└── ai-docs/
    └── docs/
        ├── prd/
        │   ├── {date}_{FID}_{slug}-prd.md
        │   └── ...
        ├── architecture/
        │   └── {date}_{FID}_{slug}-plan.md
        ├── research/
        │   └── {date}_{FID}_{slug}-research.md
        ├── plans/
        │   ├── {date}_{FID}_{slug}-implementation.md
        │   └── {date}_{FID}_{slug}-plan.md  # FEATURE mode
        └── reports/
            └── {date}_{FID}_{slug}-completion.md
```

### naming v3 (после миграции)

```
{целевой-проект}/
└── ai-docs/
    └── docs/
        ├── _analysis/
        │   ├── {date}_{FID}_{slug}.md  # PRD (без дублирования -prd)
        │   └── ...
        ├── _research/
        │   └── {date}_{FID}_{slug}.md  # Research Report
        ├── _plans/
        │   ├── mvp/
        │   │   ├── {date}_{FID}_{slug}.md  # Architecture (CREATE mode)
        │   │   └── {date}_{FID}_{slug}-implementation.md
        │   └── features/
        │       ├── {date}_{FID}_{slug}.md  # Feature Plan
        │       └── {date}_{FID}_{slug}-implementation.md
        └── _validation/
            └── {date}_{FID}_{slug}.md  # Completion Report (без дублирования -completion)
```

> **Migration Mode v2.4+**: Фреймворк поддерживает обе структуры. Выбор определяется полем `naming_version` в `.pipeline-state.json`.

## Placeholders

Шаблоны содержат placeholder'ы для автозамены:

| Placeholder | Описание |
|-------------|----------|
| `{Название проекта/фичи}` | Название из PRD |
| `{YYYY-MM-DD}` | Текущая дата |
| `{FID}` | Feature ID (например, F042) |
| `{slug}` | URL-friendly slug (например, oauth-integration) |
| `{context}` | Контекст проекта (snake_case) |
| `{entities}` | Название сущностей (plural) |
| `{entity}` | Название сущности (singular) |
| `{domain}` | Доменная область |
| `{N}` | Числовые значения |
| `{XX}%` | Процентные значения |

## Качественные ворота

Каждый шаблон содержит секцию "Качественные ворота" с чеклистом критериев прохождения этапа:

| Этап | Ворота | Описание |
|------|--------|----------|
| 0 | `BOOTSTRAP_READY` | Целевой проект инициализирован |
| 1 | `PRD_READY` | PRD полный и согласованный |
| 2 | `RESEARCH_DONE` | Исследование завершено |
| 3 | `PLAN_APPROVED` | План утверждён (требует подтверждения пользователя!) |
| 4 | `IMPLEMENT_OK` | Реализация завершена |
| 5 (Full) | `REVIEW_OK` → `QA_PASSED` → `ALL_GATES_PASSED` → `DEPLOYED` | Production-ready MVP |
| 5 (Quick) | `DOCUMENTED` | Draft Completion Report (минует sub-gates) |

> **Примечание**: Stage 5 поддерживает два режима — **Full** (полный цикл Quality & Deploy) и **Quick** (только документация).

## Кастомизация

Шаблоны можно кастомизировать под специфику проекта:

1. Скопируйте шаблон в целевой проект: `ai-docs/templates/`
2. Модифицируйте секции под свои требования
3. Обновите ссылки в инструкциях агентов (опционально)

## Best Practices

1. **Всегда заполняйте ID требований** — FR-XXX, NF-XXX, UI-XXX
2. **Связывайте артефакты** — указывайте ссылки на связанные документы (PRD → Research → Plan → Completion)
3. **Обновляйте Completion Report** — фиксируйте все изменения scope, ADR, limitations
4. **Сохраняйте историю** — не удаляйте старые версии артефактов
5. **Документируйте решения** — используйте ADR секцию для фиксации причин выбора

## Миграция на naming v3

Для переноса проекта с naming v2 на v3:

```bash
cd your-project/
python3 .aidd/scripts/migrate-naming-v3.py
```

Скрипт автоматически:
- Переименует папки артефактов
- Уберёт дублирование в именах файлов (`-prd.md` → `.md`, `-completion.md` → `.md`)
- Обновит `.pipeline-state.json` (установит `naming_version: "v3"`)
- Обновит ссылки в документах

## Связанные документы

- **Главная точка входа**: [../../CLAUDE.md](../../CLAUDE.md)
- **Процесс пайплайна**: [../../workflow.md](../../workflow.md)
- **Соглашения**: [../../conventions.md](../../conventions.md)
- **Migration Mode v2.4**: [../../contributors/2026-01-19-phase2-completion-summary.md](../../contributors/2026-01-19-phase2-completion-summary.md)
- **Consolidation Stage 5**: [../../contributors/2026-01-19-aidd-finalize-implementation.md](../../contributors/2026-01-19-aidd-finalize-implementation.md)

---

**Версия документа**: 2.0
**Обновлён**: 2026-01-20
**Изменения**: Синхронизация с Migration Mode v2.4 и Consolidation Stage 5
