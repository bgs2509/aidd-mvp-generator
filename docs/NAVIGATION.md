# Навигационная матрица AIDD-MVP Generator

**Примечание:** В этом документе встречаются устаревшие команды `/aidd-idea`, `/aidd-generate`, `/aidd-finalize`, `/aidd-feature-plan`. Актуальные команды: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


> **Назначение**: Явная таблица "роль → какие документы читать → какие создавать"
> для каждого этапа пайплайна.

---

## Принцип инициализации

> **Сначала ГДЕ мы, потом КАК действовать.**
>
> **Подробный алгоритм**: [initialization.md](initialization.md)

```
┌─────────────────────────────────────────────────────────────────┐
│  ФАЗА 1: Контекст целевого проекта (ЦП)                         │
│  ./CLAUDE.md → ./.pipeline-state.json → ./ai-docs/docs/         │
├─────────────────────────────────────────────────────────────────┤
│  ФАЗА 2: Проверка предусловий                                   │
│  .pipeline-state.json → gates.{GATE}.passed == true             │
├─────────────────────────────────────────────────────────────────┤
│  ФАЗА 3: Инструкции фреймворка                                  │
│  .aidd/CLAUDE.md → workflow.md → commands → agents              │
├─────────────────────────────────────────────────────────────────┤
│  ФАЗА 4: Шаблоны (только если артефакт не существует)           │
│  .aidd/templates/documents/*.md                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Структура матрицы

Для каждого этапа указано:
- **Читать (в ЦП)** — файлы целевого проекта
- **Читать (в фреймворке)** — файлы из `.aidd/`
- **Создавать (в ЦП)** — артефакты в `{project-name}/`

---

## Этап 0: Bootstrap (Инициализация)

**Команда**: `/aidd-init` (ручной) или авто с `/aidd-idea`
**Агент**: — (системный)
**Ворота**: `BOOTSTRAP_READY`

| Фаза | # | Проверка/Чтение | Условие |
|------|---|-----------------|---------|
| **Проверки** | 1 | `git rev-parse --git-dir` | Должен быть git репо |
| **Проверки** | 2 | `.aidd/CLAUDE.md` | Фреймворк подключен |
| **Проверки** | 3 | `python3 --version` | >= 3.11 |
| **Проверки** | 4 | `docker --version` | Docker установлен |
| **Фреймворк** | 5 | `.aidd/.claude/commands/aidd-init.md` | Всегда |
| **Фреймворк** | 6 | `.aidd/docs/target-project-structure.md` | Для создания структуры |

**Создавать (в ЦП)**:
- `ai-docs/docs/{prd,architecture,plans,reports,research}/`
- `.claude/` (локальные настройки Claude Code)
- `.pipeline-state.json`
- `CLAUDE.md`

**Чек-лист ворот BOOTSTRAP_READY**:
- [ ] Git репозиторий инициализирован
- [ ] Фреймворк `.aidd/` подключен
- [ ] Python версия >= 3.11
- [ ] Docker установлен
- [ ] Структура `ai-docs/docs/` создана
- [ ] Папка `.claude/` создана
- [ ] `.pipeline-state.json` создан

---

## Этап 1: Идея → PRD

**Команда**: `/aidd-idea`
**Агент**: Аналитик
**Ворота**: `PRD_READY`

| Фаза | # | Читать | Условие |
|------|---|--------|---------|
| **1. ЦП** | 1 | `./CLAUDE.md` | Если существует |
| **1. ЦП** | 2 | `./.pipeline-state.json` | Если существует |
| **1. ЦП** | 3 | `./ai-docs/docs/prd/` | Для FEATURE режима |
| **2. Ворота** | — | Нет предусловий | Первый этап |
| **3. Фреймворк** | 4 | `.aidd/CLAUDE.md` | Всегда |
| **3. Фреймворк** | 5 | `.aidd/workflow.md` | Всегда |
| **3. Фреймворк** | 6 | `.aidd/.claude/commands/aidd-idea.md` | Всегда |
| **3. Фреймворк** | 7 | `.aidd/.claude/agents/analyst.md` | Всегда |
| **4. Шаблоны** | 8 | `.aidd/templates/documents/prd-template.md` | Если PRD не существует |

**Создавать (в ЦП)**:
- `ai-docs/docs/prd/{name}-prd.md`
- `.pipeline-state.json`

**Чек-лист ворот PRD_READY**:
- [ ] Все секции PRD заполнены
- [ ] Требования имеют ID (FR-*, NF-*, UI-*, INT-*)
- [ ] Приоритеты Must/Should/Could указаны
- [ ] Нет блокирующих вопросов
- [ ] `.pipeline-state.json` обновлён

---

## Этап 2: Исследование

**Команда**: `/aidd-research`
**Агент**: Исследователь
**Ворота**: `RESEARCH_DONE`

| Фаза | # | Читать | Условие |
|------|---|--------|---------|
| **1. ЦП** | 1 | `./CLAUDE.md` | Если существует |
| **1. ЦП** | 2 | `./.pipeline-state.json` | Обязательно |
| **1. ЦП** | 3 | `./ai-docs/docs/prd/*.md` | Обязательно |
| **1. ЦП** | 4 | `./services/` | Для FEATURE режима |
| **2. Ворота** | — | `gates.PRD_READY.passed == true` | Обязательно |
| **3. Фреймворк** | 5 | `.aidd/CLAUDE.md` | Всегда |
| **3. Фреймворк** | 6 | `.aidd/workflow.md` | Всегда |
| **3. Фреймворк** | 7 | `.aidd/.claude/commands/aidd-research.md` | Всегда |
| **3. Фреймворк** | 8 | `.aidd/.claude/agents/researcher.md` | Всегда |
| **4. База знаний** | 9 | `.aidd/knowledge/architecture/*.md` | По необходимости |

**Создавать (в ЦП)**:
- `ai-docs/docs/research/{name}-research.md`
- Обновление `.pipeline-state.json`

**Чек-лист ворот RESEARCH_DONE**:
- [ ] Существующий код проанализирован (для FEATURE)
- [ ] Архитектурные паттерны и ограничения описаны в отчёте
- [ ] Рекомендации по интеграции зафиксированы
- [ ] Отчёт сохранён в `ai-docs/docs/research/{name}-research.md`
- [ ] `.pipeline-state.json` обновлён

---

## Этап 3: Архитектура

**Команда**: `/aidd-plan` (CREATE) или `/aidd-feature-plan` (FEATURE)
**Агент**: Архитектор
**Ворота**: `PLAN_APPROVED`

### Режим CREATE (`/aidd-plan`)

| Фаза | # | Читать | Условие |
|------|---|--------|---------|
| **1. ЦП** | 1 | `./CLAUDE.md` | Если существует |
| **1. ЦП** | 2 | `./.pipeline-state.json` | Обязательно |
| **1. ЦП** | 3 | `./ai-docs/docs/prd/*.md` | Обязательно |
| **1. ЦП** | 4 | `./ai-docs/docs/research/*.md` | Обязательно |
| **2. Ворота** | — | `gates.PRD_READY + RESEARCH_DONE` | Обязательно |
| **3. Фреймворк** | 5 | `.aidd/.claude/commands/aidd-plan.md` | Всегда |
| **3. Фреймворк** | 6 | `.aidd/.claude/agents/architect.md` | Всегда |
| **4. Шаблоны** | 7 | `.aidd/templates/documents/architecture-template.md` | Всегда |
| **4. База знаний** | 8 | `.aidd/knowledge/architecture/*.md` | Всегда |

### Режим FEATURE (`/aidd-feature-plan`)

| Фаза | # | Читать | Условие |
|------|---|--------|---------|
| **1. ЦП** | 1 | `./CLAUDE.md` | Если существует |
| **1. ЦП** | 2 | `./.pipeline-state.json` | Обязательно |
| **1. ЦП** | 3 | `./ai-docs/docs/prd/*.md` | Обязательно |
| **1. ЦП** | 4 | `./ai-docs/docs/research/*.md` | Обязательно |
| **1. ЦП** | 5 | `./ai-docs/docs/architecture/*.md` | Обязательно |
| **1. ЦП** | 6 | `./services/` | Обязательно |
| **2. Ворота** | — | `mode == FEATURE + gates` | Обязательно |
| **3. Фреймворк** | 7 | `.aidd/.claude/commands/aidd-feature-plan.md` | Всегда |
| **3. Фреймворк** | 8 | `.aidd/.claude/agents/architect.md` | Всегда |

**Создавать (в ЦП)**:
- CREATE: `ai-docs/docs/architecture/{name}-plan.md`
- FEATURE: `ai-docs/docs/plans/{feature}-plan.md`

**Чек-лист ворот PLAN_APPROVED**:
- [ ] Компоненты системы описаны
- [ ] API контракты определены
- [ ] NFR учтены
- [ ] **План утверждён пользователем**
- [ ] `.pipeline-state.json` обновлён

---

## Этап 4: Реализация

**Команда**: `/aidd-generate`
**Агент**: Реализатор
**Ворота**: `IMPLEMENT_OK`

| Фаза | # | Читать | Условие |
|------|---|--------|---------|
| **1. ЦП** | 1 | `./CLAUDE.md` | Если существует |
| **1. ЦП** | 2 | `./.pipeline-state.json` | Обязательно |
| **1. ЦП** | 3 | `./ai-docs/docs/prd/*.md` | Обязательно |
| **1. ЦП** | 4 | `./ai-docs/docs/architecture/*.md` | Для CREATE |
| **1. ЦП** | 5 | `./ai-docs/docs/plans/*.md` | Для FEATURE |
| **1. ЦП** | 6 | `./services/` | Для FEATURE |
| **2. Ворота** | — | `gates.PLAN_APPROVED.passed + approved_by` | Обязательно |
| **3. Фреймворк** | 7 | `.aidd/conventions.md` | Всегда |
| **3. Фреймворк** | 8 | `.aidd/.claude/commands/aidd-generate.md` | Всегда |
| **3. Фреймворк** | 9 | `.aidd/.claude/agents/implementer.md` | Всегда |
| **4. Шаблоны** | 10 | `.aidd/templates/services/*.md` | Всегда |
| **4. Шаблоны** | 11 | `.aidd/templates/infrastructure/*.md` | Всегда |

**Создавать (в ЦП)**:
- `docker-compose.yml`, `Makefile`
- `services/{name}_data/`, `services/{name}_api/`
- `services/{name}_bot/`, `services/{name}_worker/` (опционально)
- `services/*/tests/`

**Чек-лист ворот IMPLEMENT_OK**:
- [ ] Код написан согласно плану
- [ ] Unit-тесты проходят
- [ ] Структура DDD/Hexagonal соблюдена
- [ ] Type hints везде
- [ ] `.pipeline-state.json` обновлён

---

## Этап 5: Quality & Deploy

**Команда**: `/aidd-finalize` (или `/aidd-validate` в v2.4+)
**Роль**: Валидатор (`.claude/agents/validator.md`)
**Предусловие**: `IMPLEMENT_OK` ✓
**Артефакт**: `ai-docs/docs/reports/{YYYY-MM-DD}_{FID}_{slug}-completion.md`

### Описание

Этап Quality & Deploy выполняет полный цикл проверки качества и деплоя в 4 последовательных шага:

```
┌──────────────────────────────────────────────────────────────┐
│  Шаг 1: Code Review → REVIEW_OK                              │
│  Шаг 2: Testing → QA_PASSED                                  │
│  Шаг 3: Validation → ALL_GATES_PASSED                        │
│  Шаг 4: Deploy & Completion Report → DEPLOYED                │
└──────────────────────────────────────────────────────────────┘
```

### Таблица чтения

| Фаза | # | Читать | Условие |
|------|---|--------|---------|
| **1. ЦП** | 1 | `./CLAUDE.md` | Если существует |
| **1. ЦП** | 2 | `./.pipeline-state.json` | Обязательно |
| **1. ЦП** | 3 | `./ai-docs/docs/prd/*.md` | Обязательно |
| **1. ЦП** | 4 | `./ai-docs/docs/architecture/*.md` | Обязательно |
| **1. ЦП** | 5 | `./services/` | Обязательно |
| **1. ЦП** | 6 | `./docker-compose.yml`, `./Makefile` | Для шага 4 (Deploy) |
| **2. Ворота** | — | Проверка `IMPLEMENT_OK` | Обязательно (для Full режима) |
| **3. Фреймворк** | 7 | `.aidd/CLAUDE.md` | Всегда |
| **3. Фреймворк** | 8 | `.aidd/workflow.md` | Всегда |
| **3. Фреймворк** | 9 | `.aidd/.claude/commands/aidd-finalize.md` | Главные инструкции |
| **3. Фреймворк** | 10 | `.aidd/.claude/agents/validator.md` | Роль Валидатора |
| **3. Фреймворк** | 11 | `.aidd/.claude/agents/code-review-library.md` | Библиотека для шага 1 |
| **3. Фреймворк** | 12 | `.aidd/.claude/agents/testing-library.md` | Библиотека для шага 2 |
| **3. Фреймворк** | 13 | `.aidd/conventions.md` | Соглашения о коде |
| **4. Шаблоны** | 14 | `.aidd/templates/documents/completion-report-template.md` | Для создания итогового отчёта |
| **4. База знаний** | 15 | `.aidd/knowledge/quality/quality-cascade.md` | Quality Cascade (17 проверок) |
| **4. База знаний** | 16 | `.aidd/knowledge/security/security-checklist.md` | Security checklist |

### Два режима работы

| Режим | Когда использовать | Ворота |
|-------|-------------------|--------|
| **Полный** (рекомендуется) | Production-ready MVP | `REVIEW_OK` → `QA_PASSED` → `ALL_GATES_PASSED` → `DEPLOYED` |
| **Быстрый** | Документация, застопорившаяся фича | `DOCUMENTED` (только static analysis) |

**Быстрый режим** (Quick Mode):
- Выполняет только mypy, ruff, bandit (без тестов)
- Создаёт DRAFT Completion Report с пометкой "⚠️ DRAFT — QA не выполнено"
- Фича остаётся в `active_pipelines` (НЕ переносится в `features_registry`)
- Позволяет переключиться на другую фичу без завершения текущей

### Создаваемый артефакт (единственный)

- `ai-docs/docs/reports/{YYYY-MM-DD}_{FID}_{slug}-completion.md`

**Completion Report** содержит:
- Executive Summary
- Code Review Summary (вместо отдельного review-report.md)
- Testing Summary (вместо отдельного qa-report.md)
- Requirements Traceability (вместо отдельного rtm.md)
- ADR (Architecture Decision Records)
- Scope Changes (план vs факт)
- Known Limitations
- Метрики качества

### Библиотеки инструкций

Валидатор использует две вспомогательные библиотеки:

| Библиотека | Файл | Содержимое |
|------------|------|-----------|
| **Code Review** | `.claude/agents/code-review-library.md` | Quality Cascade (17 проверок), Log-Driven Design, Security |
| **Testing** | `.claude/agents/testing-library.md` | Тестовые сценарии, Coverage, Верификация требований |

### Чек-лист ворот

**REVIEW_OK** (после шага 1):
- [ ] Архитектура соответствует плану (DDD, HTTP-only)
- [ ] Security checklist пройден (нет уязвимостей)
- [ ] Code style соблюдён (conventions.md)
- [ ] Log-Driven Design проверен
- [ ] Quality Cascade (QC-1 до QC-17) пройден

**QA_PASSED** (после шага 2):
- [ ] Все тесты проходят (0 failed)
- [ ] Coverage ≥ 75%
- [ ] Integration тесты пройдены
- [ ] Все FR-* требования верифицированы

**ALL_GATES_PASSED** (после шага 3):
- [ ] PRD_READY ✓
- [ ] RESEARCH_DONE ✓
- [ ] PLAN_APPROVED ✓
- [ ] IMPLEMENT_OK ✓
- [ ] REVIEW_OK ✓ (из шага 1)
- [ ] QA_PASSED ✓ (из шага 2)
- [ ] Security BLOCKER issues = 0
- [ ] Security CRITICAL issues = 0
- [ ] Все артефакты существуют и актуальны

**DEPLOYED** (после шага 4):
- [ ] Docker-контейнеры собраны и запущены
- [ ] Health-check проходит
- [ ] Базовые сценарии работают (API запросы успешны)
- [ ] Логи проверены (нет ошибок)
- [ ] **Completion Report создан** ← ОБЯЗАТЕЛЬНО!
- [ ] Фича перенесена в `features_registry`

---

## Сводная таблица

| # | Этап | Команда | Агент | Читает | Создаёт | Ворота |
|---|------|---------|-------|--------|---------|--------|
| 0 | Bootstrap | `/aidd-init` | — | init.md, target-structure | Структура ЦП | BOOTSTRAP_READY |
| 1 | Идея | `/aidd-idea` | Аналитик | CLAUDE, workflow, analyst, prd-template | PRD, state | PRD_READY |
| 2 | Исследование | `/aidd-research` | Исследователь | researcher, knowledge | (state) | RESEARCH_DONE |
| 3 | Архитектура | `/aidd-plan` | Архитектор | architect, ddd, http-only | План | PLAN_APPROVED |
| 4 | Реализация | `/aidd-generate` | Реализатор | implementer, conventions, templates | Код, тесты | IMPLEMENT_OK |
| 5 | Quality & Deploy | `/aidd-finalize` | Валидатор | validator, code-review-library, testing-library, completion-report-template | Completion Report | REVIEW_OK → QA_PASSED → ALL_GATES_PASSED → DEPLOYED |

> **Примечание (v2.4+)**: Унификация naming conventions:
>
> | Старое | Новое | Статус |
> |--------|-------|--------|
> | `/aidd-idea` | `/aidd-analyze` | ✅ Оба работают |
> | `/aidd-feature-plan` | `/aidd-plan-feature` | ✅ Оба работают |
> | `/aidd-generate` | `/aidd-code` | ✅ Оба работают |
> | `/aidd-finalize` | `/aidd-validate` | ✅ Оба работают |
> | `architect.md` | `planner.md` | ✅ Оба доступны |
> | `implementer.md` | `coder.md` | ✅ Оба доступны |
>
> **Важно**: `/aidd-finalize` (или `/aidd-validate`) объединяет этапы 5-8 в один цикл Quality & Deploy.

---

## См. также

- [initialization.md](initialization.md) — Алгоритм инициализации (4 фазы)
- [INDEX.md](INDEX.md) — Полный индекс файлов генератора
- [PIPELINE-TREE.md](PIPELINE-TREE.md) — Дерево всех пайплайнов
- [target-project-structure.md](target-project-structure.md) — Структура целевого проекта
- [workflow.md](../workflow.md) — Детальное описание процесса

---

**Версия**: 2.0
**Обновлён**: 2025-12-21
