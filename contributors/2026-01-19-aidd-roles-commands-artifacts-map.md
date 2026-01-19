# Полная карта ролей AIDD-MVP Generator

> **Цель**: Систематизировать все роли, команды, артефакты и связи между ними.

> **⚠️ Naming Convention Migration (v2.4+)**:
>
> Фреймворк унифицирует naming на основе 5 базовых слов: **analyst**, **researcher**, **planner**, **coder**, **validator**.
>
> **Изменения в этом документе**:
> - Роли: `architect` → `planner` (оба доступны), `implementer` → `coder` (оба доступны)
> - Команды: `/aidd-idea` → `/aidd-analyze`, `/aidd-feature-plan` → `/aidd-plan-feature`, `/aidd-generate` → `/aidd-code`, `/aidd-finalize` → `/aidd-validate`
> - Все старые названия продолжают работать (backward compatible)
>
> **Полный план**: `/home/bgs/.claude/plans/idempotent-drifting-wirth.md`

---

## Сводная таблица: Роли → Команды → Артефакты

| # | Роль | Файл роли | Команда | Этап | Ворота | Входные артефакты | Выходные артефакты |
|---|------|-----------|---------|------|--------|-------------------|-------------------|
| 0 | — | — | `/aidd-init` | Bootstrap | `BOOTSTRAP_READY` | Пустой проект | Структура ЦП, `.pipeline-state.json`, `CLAUDE.md` |
| 1 | **Аналитик** | `analyst.md` | `/aidd-idea` | Идея | `PRD_READY` | Описание идеи | `prd/{name}-prd.md` |
| 2 | **Исследователь** | `researcher.md` | `/aidd-research` | Исследование | `RESEARCH_DONE` | PRD, существующий код | `research/{name}-research.md` |
| 3a | **Архитектор** | `architect.md` | `/aidd-plan` | Архитектура (CREATE) | `PLAN_APPROVED`⚠️ | PRD, Research | `architecture/{name}-plan.md` |
| 3b | **Архитектор** | `architect.md` | `/aidd-feature-plan` | Архитектура (FEATURE) | `PLAN_APPROVED`⚠️ | PRD, Research, Existing code | `plans/{feature}-plan.md` |
| 4 | **Реализатор** | `implementer.md` | `/aidd-generate` | Реализация | `IMPLEMENT_OK` | Architecture Plan | `services/`, тесты, инфраструктура |
| 5 | **Валидатор** | `validator.md` | `/aidd-finalize` (Full) | Quality & Deploy | `REVIEW_OK`, `QA_PASSED`, `ALL_GATES_PASSED`, `DEPLOYED` | Все артефакты проекта | `reports/{date}_{FID}_{slug}-completion.md` |
| 5b | **Валидатор** | `validator.md` | `/aidd-finalize` (Quick) | Static Analysis | `DOCUMENTED` | Код | DRAFT Completion Report |
| — | **Reviewer** | `reviewer.md` | — | Внутри `/aidd-finalize` Шаг 1 | `REVIEW_OK` | Код, Plan | Review Summary (в Completion Report) |
| — | **QA** | `qa.md` | — | Внутри `/aidd-finalize` Шаг 2 | `QA_PASSED` | Код, тесты, PRD | Testing Summary (в Completion Report) |

> ⚠️ `PLAN_APPROVED` требует **явного подтверждения пользователя**

---

## Детализация по ролям

### 1. Аналитик (Analyst)

**Файл**: `.claude/agents/analyst.md`

**Назначение**: Преобразование идеи пользователя в структурированный PRD документ.

**Команды**:
- `/aidd-idea` — создание PRD

**Инструменты**:
- Read, Glob, Grep, Edit, Write

**Входные данные**:
- Описание идеи от пользователя (текст)
- `CLAUDE.md` — контекст фреймворка
- `conventions.md` — соглашения о коде
- `workflow.md` — процесс разработки

**Выходные артефакты**:
- `ai-docs/docs/prd/{name}-prd.md` — Product Requirements Document
- `ai-docs/docs/rtm.md` (начало) — Requirements Traceability Matrix

**Качественные ворота**:
- `PRD_READY` ✓

**Чеклист PRD_READY**:
- [ ] Все секции PRD заполнены
- [ ] Каждое требование имеет уникальный ID (FR-*, NF-*, UI-*, INT-*)
- [ ] Приоритеты расставлены (Must/Should/Could)
- [ ] Критерии приёмки определены
- [ ] Бизнес-пайплайн описан
- [ ] Data Pipeline описан
- [ ] Интеграционный пайплайн описан
- [ ] Раздел "Влияние на существующие пайплайны" заполнен
- [ ] Нет блокирующих открытых вопросов

**Связанные документы**:
- `roles/analyst/initialization.md`
- `roles/analyst/prompt-validation.md`
- `roles/analyst/requirements-gathering.md`
- `roles/analyst/prd-formation.md`
- `templates/documents/prd-template.md`

---

### 2. Исследователь (Researcher)

**Файл**: `.claude/agents/researcher.md`

**Назначение**: Анализ кодовой базы и выявление паттернов.

**Команды**:
- `/aidd-research` — анализ кода и требований

**Инструменты**:
- Read, Glob, Grep, Bash

**Входные данные**:
- `ai-docs/docs/prd/{name}-prd.md` — PRD документ
- Существующий код проекта (для режима FEATURE)
- `CLAUDE.md` — контекст фреймворка
- `knowledge/architecture/` — архитектурные принципы

**Выходные артефакты**:
- `ai-docs/docs/research/{name}-research.md` — Research Report с Quality Cascade Checklist (7/7)

**Качественные ворота**:
- `RESEARCH_DONE` ✓

**Quality Cascade (7 проверок)**:
1. **DRY** — Выявление существующего кода для переиспользования
2. **KISS** — Критическая оценка сложности PRD
3. **YAGNI** — Фильтрация "на будущее"
4. **SoC** — Анализ разделения ответственностей
5. **SSoT** — Определение источников данных
6. **CoC** — Выявление конвенций проекта
7. **Security** — Анализ практик безопасности

**Связанные документы**:
- `roles/researcher/codebase-analysis.md`
- `roles/researcher/pattern-identification.md`
- `roles/researcher/constraint-identification.md`
- `roles/researcher/pipeline-refinement.md`
- `knowledge/architecture/ddd-hexagonal.md`

---

### 3. Архитектор (Architect)

**Файл**: `.claude/agents/architect.md`

**Назначение**: Проектирование архитектуры и создание Implementation Plan.

**Команды**:
- `/aidd-plan` — для CREATE режима
- `/aidd-feature-plan` — для FEATURE режима

**Инструменты**:
- Read, Glob, Grep, Edit, Write

**Входные данные**:
- `ai-docs/docs/prd/{name}-prd.md` — PRD документ
- `ai-docs/docs/research/{name}-research.md` — Research Report
- `knowledge/architecture/` — архитектурные принципы
- `templates/services/` — доступные шаблоны

**Выходные артефакты**:
- **CREATE**: `ai-docs/docs/architecture/{name}-plan.md`
- **FEATURE**: `ai-docs/docs/plans/{feature}-plan.md`

**Качественные ворота**:
- `PLAN_APPROVED` ✓ (требует подтверждения пользователя!)

**Quality Cascade (16 проверок)**:
1. **DRY** — Нет дублирования с существующим
2. **KISS** — Минимальная сложность
3. **YAGNI** — Только необходимые компоненты
4. **SRP** — Единая ответственность
5. **OCP** — Открыто для расширения
6. **ISP** — Маленькие интерфейсы
7. **DIP** — Инверсия зависимостей
8. **SoC** — Разделение ответственностей
9. **SSoT** — Единый источник данных
10. **LoD** — Минимальная связанность
11. **CoC** — Следование конвенциям
12. **Fail Fast** — Стратегия обработки ошибок
13. **Explicit > Implicit** — Явность
14. **Composition > Inheritance** — Композиция
15. **Testability** — Тестируемость
16. **Security** — Безопасность

**Связанные документы**:
- `roles/architect/architecture-design.md`
- `roles/architect/maturity-level-selection.md`
- `roles/architect/service-naming.md`
- `roles/architect/implementation-plan.md`
- `roles/architect/api-contracts.md`
- `knowledge/architecture/improved-hybrid.md`
- `knowledge/architecture/ddd-hexagonal.md`

---

### 4. Реализатор (Implementer)

**Файл**: `.claude/agents/implementer.md`

**Назначение**: Генерация кода на основе утверждённого плана.

**Команды**:
- `/aidd-generate` — генерация кода

**Инструменты**:
- Read, Glob, Grep, Edit, Write, Bash

**Входные данные**:
- `ai-docs/docs/architecture/{name}-plan.md` — Architecture Plan
- `templates/services/` — шаблоны сервисов
- `templates/shared/` — общие компоненты
- `templates/infrastructure/` — шаблоны инфраструктуры
- `conventions.md` — соглашения о коде

**Выходные артефакты**:
- `services/{name}/` — код сервисов
- `services/{name}/tests/` — тесты
- `docker-compose.yml` — инфраструктура
- `Makefile` — команды управления
- `.github/workflows/` — CI/CD

**Качественные ворота**:
- `IMPLEMENT_OK` ✓

**Обязательная процедура**:
1. **Подготовка** — прочитать план, составить список компонентов, создать TodoWrite
2. **Генерация** — сверка с планом, запрет на scope creep
3. **Проверка** — Plan-to-Code Mapping, выявление отклонений, финальная проверка

**Quality Cascade (17 проверок)**:
1-16 — те же что у Архитектора
17. **Security** — безопасный код

**КРИТИЧЕСКИЕ ЗАПРЕТЫ**:
- ❌ Чтение `.env` файлов
- ❌ Добавление методов "на будущее"
- ❌ Изменение архитектурных решений из плана

**Связанные документы**:
- `roles/implementer/infrastructure-setup.md`
- `roles/implementer/data-service.md`
- `roles/implementer/business-api.md`
- `roles/implementer/background-worker.md`
- `roles/implementer/telegram-bot.md`
- `roles/implementer/testing.md`
- `roles/implementer/logging.md`
- `roles/implementer/nginx.md`
- `knowledge/services/`

---

### 5. Валидатор (Validator)

**Файл**: `.claude/agents/validator.md`

**Назначение**: Полный цикл Quality & Deploy (объединяет Reviewer + QA).

**Команды**:
- `/aidd-finalize` — с двумя режимами:
  - **Full Mode** (рекомендуется) — 4 шага → Production-ready MVP
  - **Quick Mode** — Static Analysis → DRAFT документация

**Инструменты**:
- Read, Glob, Grep, Bash, Edit, Write

**Входные данные**:
- Все артефакты проекта: `ai-docs/`, `services/`
- `ai-docs/docs/prd/{name}-prd.md` — PRD
- `ai-docs/docs/architecture/{name}-plan.md` — Plan
- `ai-docs/docs/research/{name}-research.md` — Research
- `.pipeline-state.json` — состояние пайплайна

**Выходные артефакты**:
- **Full Mode**: `ai-docs/docs/reports/{YYYY-MM-DD}_{FID}_{slug}-completion.md` — Completion Report
- **Quick Mode**: DRAFT Completion Report с пометкой "⚠️ DRAFT — QA не выполнено"

**Качественные ворота**:
- **Full Mode**:
  - `REVIEW_OK` ✓ (после шага 1)
  - `QA_PASSED` ✓ (после шага 2)
  - `ALL_GATES_PASSED` ✓ (после шага 3)
  - `DEPLOYED` ✓ (после шага 4)
- **Quick Mode**:
  - `DOCUMENTED` ✓

**4 шага Full Mode**:
1. **Code Review** (как Reviewer) → `REVIEW_OK`
2. **Testing** (как QA) → `QA_PASSED`
3. **Validation** (как Validator) → `ALL_GATES_PASSED`
4. **Deploy & Completion Report** → `DEPLOYED`

**Completion Report содержит**:
- Executive Summary — что сделано
- Code Review Summary — вместо review-report.md
- Testing Summary — вместо qa-report.md
- Requirements Traceability — вместо rtm.md
- ADR (Architecture Decision Records)
- Scope Changes (план vs факт)
- Known Limitations
- Метрики качества
- Timeline

**КРИТИЧЕСКИЕ ЗАПРЕТЫ**:
- ❌ Чтение `.env` файлов
- ❌ Пропуск создания Completion Report

**Связанные документы**:
- `.claude/commands/aidd-finalize.md` — главная инструкция
- `templates/documents/completion-report-template.md`
- `conventions.md`
- `knowledge/quality/quality-cascade.md`
- `knowledge/quality/logging/log-driven-design.md`
- `knowledge/infrastructure/docker-compose.md`
- `knowledge/security/security-checklist.md`
- `knowledge/security/secrets-management.md`

---

### 6. Reviewer (вспомогательная роль)

**Файл**: `.claude/agents/reviewer.md`

**Назначение**: Код-ревью на соответствие стандартам.

**Команды**:
- Нет отдельной команды, используется внутри `/aidd-finalize` (Шаг 1)

**Инструменты**:
- Read, Glob, Grep, Edit, Write

**Входные данные**:
- `services/` — сгенерированный код
- `ai-docs/docs/architecture/{name}-plan.md` — Plan
- `conventions.md` — соглашения
- `knowledge/quality/dry-kiss-yagni.md` — принципы

**Выходные артефакты**:
- Review Summary (секция в Completion Report)

**Качественные ворота**:
- `REVIEW_OK` ✓

**Quality Cascade (17 проверок)** — те же что у Implementer

**Проверки**:
- Архитектура (DDD, HTTP-only)
- Соблюдение conventions.md
- Log-Driven Design
- Безопасность секретов

**КРИТИЧЕСКИЕ ЗАПРЕТЫ**:
- ❌ Чтение `.env` файлов

**Связанные документы**:
- `roles/reviewer/architecture-compliance.md`
- `roles/reviewer/convention-compliance.md`
- `roles/reviewer/review-report.md`
- `knowledge/quality/dry-kiss-yagni.md`
- `knowledge/quality/logging/log-driven-design.md`
- `roles/implementer/logging.md`

---

### 7. QA (вспомогательная роль)

**Файл**: `.claude/agents/qa.md`

**Назначение**: Тестирование и верификация качества кода.

**Команды**:
- Нет отдельной команды, используется внутри `/aidd-finalize` (Шаг 2)

**Инструменты**:
- Read, Glob, Grep, Bash, Edit, Write

**Входные данные**:
- `ai-docs/docs/prd/{name}-prd.md` — PRD
- `services/` — код после ревью
- `services/*/tests/` — существующие тесты
- `knowledge/quality/testing/` — документация по тестированию

**Выходные артефакты**:
- Testing Summary (секция в Completion Report)

**Качественные ворота**:
- `QA_PASSED` ✓

**Чеклист QA_PASSED**:
- [ ] Все тесты проходят (0 failed)
- [ ] Coverage ≥ 75%
- [ ] Нет критических багов (Critical/Blocker)
- [ ] Все FR-* требования верифицированы

**Связанные документы**:
- `roles/qa/test-scenarios.md`
- `roles/qa/test-execution.md`
- `roles/qa/coverage-verification.md`
- `roles/qa/qa-report.md`
- `knowledge/quality/testing/pytest-setup.md`

---

## Матрица сущностей

### Качественные ворота

| Ворота | Этап | Команда | Кто проверяет | Блокирует переход |
|--------|------|---------|---------------|-------------------|
| `BOOTSTRAP_READY` | 0 | `/aidd-init` | — | Да |
| `PRD_READY` | 1 | `/aidd-idea` | Аналитик | Да |
| `RESEARCH_DONE` | 2 | `/aidd-research` | Исследователь | Да |
| `PLAN_APPROVED`⚠️ | 3 | `/aidd-plan` или `/aidd-feature-plan` | Архитектор + **Пользователь** | Да |
| `IMPLEMENT_OK` | 4 | `/aidd-generate` | Реализатор | Да |
| `REVIEW_OK` | 5.1 | `/aidd-finalize` (Шаг 1) | Валидатор (как Reviewer) | Да |
| `QA_PASSED` | 5.2 | `/aidd-finalize` (Шаг 2) | Валидатор (как QA) | Да |
| `ALL_GATES_PASSED` | 5.3 | `/aidd-finalize` (Шаг 3) | Валидатор | Да |
| `DEPLOYED` | 5.4 | `/aidd-finalize` (Шаг 4) | Валидатор | Нет (финальные ворота) |
| `DOCUMENTED` | 5.0 | `/aidd-finalize` (Quick) | Валидатор | Нет (DRAFT) |

### Типы артефактов

| Артефакт | Путь | Создаёт | Читает | Назначение |
|----------|------|---------|--------|------------|
| `CLAUDE.md` | `./CLAUDE.md` | `/aidd-init` | Все роли | Точка входа ЦП |
| `.pipeline-state.json` | `./.pipeline-state.json` | `/aidd-init`, все команды | Все роли | Состояние пайплайна (v2) |
| **PRD** | `ai-docs/docs/prd/{name}-prd.md` | Аналитик | Исследователь, Архитектор, QA | Product Requirements |
| **Research Report** | `ai-docs/docs/research/{name}-research.md` | Исследователь | Архитектор | Анализ кода/требований |
| **Architecture Plan** | `ai-docs/docs/architecture/{name}-plan.md` | Архитектор (CREATE) | Реализатор, Валидатор | Архитектурный план |
| **Feature Plan** | `ai-docs/docs/plans/{feature}-plan.md` | Архитектор (FEATURE) | Реализатор, Валидатор | План фичи |
| **Сервисы** | `services/{name}/` | Реализатор | Валидатор | Код сервисов |
| **Тесты** | `services/{name}/tests/` | Реализатор | QA, Валидатор | Unit/Integration тесты |
| **Инфраструктура** | `docker-compose.yml`, `Makefile` | Реализатор | Валидатор | Настройка окружения |
| **Completion Report** | `ai-docs/docs/reports/{date}_{FID}_{slug}-completion.md` | Валидатор | AI в будущих сессиях | Итоговый отчёт о фиче |

### Quality Cascade уровни

| Роль | Количество проверок | Что проверяется |
|------|---------------------|-----------------|
| Исследователь | 7 | DRY, KISS, YAGNI, SoC, SSoT, CoC, Security (анализ существующего) |
| Архитектор | 16 | DRY, KISS, YAGNI, SRP, OCP, ISP, DIP, SoC, SSoT, LoD, CoC, Fail Fast, Explicit, Composition, Testability, Security (проектирование) |
| Реализатор | 17 | Те же 16 + Security (написание кода) |
| Reviewer | 17 | Те же 17 (верификация кода) |

### Режимы работы

| Режим | Признак | Команда архитектуры | Артефакт плана |
|-------|---------|---------------------|----------------|
| **CREATE** | Нет `services/` или `docker-compose.yml` | `/aidd-plan` | `architecture/{name}-plan.md` |
| **FEATURE** | Есть `services/` или `docker-compose.yml` | `/aidd-feature-plan` | `plans/{feature}-plan.md` |

### Два режима `/aidd-finalize`

| Режим | Шаги | Ворота | Результат | Когда использовать |
|-------|------|--------|-----------|-------------------|
| **Full** (рекомендуется) | 4 (Review → Test → Validate → Deploy) | `REVIEW_OK`, `QA_PASSED`, `ALL_GATES_PASSED`, `DEPLOYED` | Production-ready MVP | Завершение фичи |
| **Quick** | 1 (Static Analysis) | `DOCUMENTED` | DRAFT Completion Report | Документационная фича, временный коммит |

---

## Ключевые принципы

### VERIFY BEFORE ACT

```
┌─────────────────────────────────────────────────────────────────┐
│  ПЕРЕД ЛЮБЫМ ДЕЙСТВИЕМ AI ОБЯЗАН:                               │
├─────────────────────────────────────────────────────────────────┤
│  1. СОЗДАНИЕ ФАЙЛА  → Проверить, что файл НЕ существует         │
│  2. РЕДАКТИРОВАНИЕ  → Сначала прочитать текущее содержимое      │
│  3. УДАЛЕНИЕ        → Проверить все зависимости и ссылки        │
│  4. ДОБАВЛЕНИЕ ССЫЛКИ → Проверить, что цель существует          │
│  5. НАПИСАНИЕ КОДА  → Проверить нет ли похожего кода (DRY)      │
│  6. ДОБАВЛЕНИЕ ФИЧИ → Проверить, что это нужно СЕЙЧАС (YAGNI)   │
└─────────────────────────────────────────────────────────────────┘

НИКОГДА НЕ ПРЕДПОЛАГАТЬ → ВСЕГДА ПРОВЕРЯТЬ → ЗАТЕМ ДЕЙСТВОВАТЬ
```

### Артефакты = Память

Не полагаемся на контекст чата. Всё важное записывается в артефакты:
- PRD — требования
- Research — анализ кода
- Plan — архитектурные решения
- Completion Report — итоги реализации

### Запрет чтения .env файлов

```
┌─────────────────────────────────────────────────────────────────┐
│  ⛔ AI НИКОГДА НЕ ЧИТАЕТ .env ФАЙЛЫ                             │
├─────────────────────────────────────────────────────────────────┤
│  • Файлы .env, .env.*, *.env, .env.local содержат СЕКРЕТЫ       │
│  • Запрещены ВСЕ инструменты: Read, Bash (cat/grep/less/...)   │
│  • Альтернатива: .env.example (БЕЗ реальных значений)           │
│  • Исключений НЕТ — даже для других проектов                    │
│                                                                 │
│  Нарушение = BLOCKER для любой задачи                           │
└─────────────────────────────────────────────────────────────────┘
```

### Выполнение команд /aidd-*

При выполнении любой команды `/aidd-*` AI ОБЯЗАН:

1. **Прочитать ВЕСЬ** файл команды `.aidd/.claude/commands/{cmd}.md`
2. **Найти** секцию "Чеклист ворот" в конце файла
3. **Создать TodoWrite** со ВСЕМИ пунктами чеклиста
4. **Выполнить** каждый пункт и отметить completed
5. **Завершить** команду ТОЛЬКО когда ВСЕ 🔴 пункты выполнены

Маркеры:
- 🔴 **BLOCKER** — без этого команда НЕ завершена
- 🟡 **REQUIRED** — обязательно выполнить
- ⚪ **OPTIONAL** — рекомендуется

---

## Итоговая статистика

**Количество ролей**: 7 (5 основных + 2 вспомогательных)
**Количество команд**: 7 (`/aidd-init`, `/aidd-idea`, `/aidd-research`, `/aidd-plan`, `/aidd-feature-plan`, `/aidd-generate`, `/aidd-finalize`)
**Количество ворот**: 9 (`BOOTSTRAP_READY`, `PRD_READY`, `RESEARCH_DONE`, `PLAN_APPROVED`, `IMPLEMENT_OK`, `REVIEW_OK`, `QA_PASSED`, `ALL_GATES_PASSED`, `DEPLOYED`) + 1 Quick mode (`DOCUMENTED`)
**Количество этапов**: 6 (0-5)
**Количество артефактов**: 10+ типов

---

**Версия документа**: 1.0
**Дата создания**: 2026-01-19
**Назначение**: Систематизация всех ролей, команд и артефактов фреймворка AIDD-MVP Generator
