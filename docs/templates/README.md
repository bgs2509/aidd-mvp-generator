# Шаблоны документов AIDD-MVP

Шаблоны для генерации документации на каждом этапе пайплайна разработки.

## Содержимое

| Шаблон | Назначение | Этап | Агент |
|--------|------------|------|-------|
| `prd-template.md` | Product Requirements Document | Stage 1 | Аналитик |
| `architecture-template.md` | Архитектурный план | Stage 3 | Архитектор |
| `implementation-plan-template.md` | План реализации | Stage 3 | Архитектор |
| `review-report-template.md` | Отчёт code review | Stage 5 | Ревьюер |
| `qa-report-template.md` | Отчёт тестирования | Stage 6 | QA |
| `validation-report-template.md` | Отчёт валидации | Stage 7 | Валидатор |
| `rtm-template.md` | Матрица трассировки требований | All | Все агенты |

## Использование

### 1. PRD Template

Используется Аналитиком для формирования требований:

```bash
/idea "Описание проекта или фичи"
```

**Выходной файл**: `ai-docs/prd/{name}-prd.md`

### 2. Architecture Template

Используется Архитектором для проектирования:

```bash
/plan
```

**Выходной файл**: `ai-docs/architecture/{name}-architecture.md`

### 3. Implementation Plan Template

Используется Архитектором для планирования реализации:

```bash
/plan
# или
/feature-plan
```

**Выходной файл**: `ai-docs/plans/{name}-plan.md`

### 4. Review Report Template

Используется Ревьюером после code review:

```bash
/review
```

**Выходной файл**: `ai-docs/reports/review-{name}.md`

### 5. QA Report Template

Используется QA после тестирования:

```bash
/test
```

**Выходной файл**: `ai-docs/reports/qa-{name}.md`

### 6. Validation Report Template

Используется Валидатором для финальной проверки:

```bash
/validate
```

**Выходной файл**: `ai-docs/reports/validation-{name}.md`

### 7. RTM Template

Обновляется всеми агентами для трассировки требований:

**Файл**: `ai-docs/rtm.md`

## Структура директории ai-docs

```
ai-docs/
├── prd/
│   ├── {project}-prd.md
│   └── {feature}-prd.md
├── architecture/
│   └── {project}-architecture.md
├── plans/
│   ├── {project}-implementation-plan.md
│   └── {feature}-plan.md
├── reports/
│   ├── review-{name}.md
│   ├── qa-{name}.md
│   └── validation-{name}.md
└── rtm.md
```

## Placeholders

Шаблоны содержат placeholder'ы для автозамены:

| Placeholder | Описание |
|-------------|----------|
| `{Название проекта/фичи}` | Название из PRD |
| `{YYYY-MM-DD}` | Текущая дата |
| `{context}` | Контекст проекта (snake_case) |
| `{entities}` | Название сущностей (plural) |
| `{entity}` | Название сущности (singular) |
| `{domain}` | Доменная область |
| `{N}` | Числовые значения |
| `{XX}%` | Процентные значения |

## Качественные ворота

Каждый шаблон содержит секцию "Качественные ворота" с чеклистом критериев прохождения этапа:

- **PRD_READY** — PRD полный и согласованный
- **RESEARCH_DONE** — Исследование завершено
- **PLAN_APPROVED** — План утверждён
- **IMPLEMENTATION_DONE** — Реализация завершена
- **REVIEW_PASSED** — Code review пройден
- **QA_PASSED** — Тестирование успешно
- **DEPLOY_READY** — Готов к деплою

## Кастомизация

Шаблоны можно кастомизировать под специфику проекта:

1. Скопируйте шаблон в `ai-docs/templates/`
2. Модифицируйте секции
3. Обновите ссылки в инструкциях агентов

## Best Practices

1. **Всегда заполняйте ID требований** — FR-XXX, NF-XXX, UI-XXX
2. **Связывайте артефакты** — указывайте ссылки на связанные документы
3. **Обновляйте RTM** — после каждого изменения требований
4. **Сохраняйте историю** — не удаляйте старые версии
5. **Документируйте решения** — фиксируйте причины выбора
