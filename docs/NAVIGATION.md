# Навигационная матрица AIDD-MVP Generator

> **Назначение**: Явная таблица "роль → какие документы читать → какие создавать"
> для каждого этапа пайплайна.

---

## Структура матрицы

Для каждого этапа указано:
- **Читать (в генераторе)** — файлы фреймворка для изучения
- **Создавать (в целевом проекте)** — артефакты в `{project-name}/`

---

## Этап 1: Идея → PRD

**Команда**: `/idea`
**Агент**: Аналитик
**Ворота**: `PRD_READY`

| Что делать | Читать (в генераторе) | Создавать (в целевом проекте) |
|------------|----------------------|-------------------------------|
| Понять контекст | [CLAUDE.md](../CLAUDE.md) | — |
| Изучить процесс | [workflow.md](../workflow.md) | — |
| Изучить роль | [.claude/agents/analyst.md](../.claude/agents/analyst.md) | — |
| Изучить шаблон | [docs/templates/prd-template.md](templates/prd-template.md) | — |
| Bootstrap структуры | — | `mkdir -p ai-docs/docs/{prd,architecture,plans,reports}` |
| Инициализация state | — | `.pipeline-state.json` |
| Создать PRD | — | `ai-docs/docs/prd/{name}-prd.md` |

**Чек-лист ворот PRD_READY**:
- [ ] Все секции PRD заполнены
- [ ] Требования имеют ID (FR-*, NF-*, UI-*)
- [ ] Приоритеты Must/Should/Could указаны
- [ ] Нет блокирующих вопросов
- [ ] `.pipeline-state.json` обновлён

---

## Этап 2: Исследование

**Команда**: `/research`
**Агент**: Исследователь
**Ворота**: `RESEARCH_DONE`

| Что делать | Читать (в генераторе) | Создавать (в целевом проекте) |
|------------|----------------------|-------------------------------|
| Изучить роль | [.claude/agents/researcher.md](../.claude/agents/researcher.md) | — |
| Анализ кода (FEATURE) | — | Существующий код в `services/` |
| Паттерны | [knowledge/architecture/](../knowledge/architecture/) | — |
| Результат | — | (в памяти / обновление state) |

**Чек-лист ворот RESEARCH_DONE**:
- [ ] Существующий код проанализирован (для FEATURE)
- [ ] Архитектурные паттерны выявлены
- [ ] Технические ограничения определены
- [ ] `.pipeline-state.json` обновлён

---

## Этап 3: Архитектура

**Команда**: `/plan` (CREATE) или `/feature-plan` (FEATURE)
**Агент**: Архитектор
**Ворота**: `PLAN_APPROVED`

### Режим CREATE

| Что делать | Читать (в генераторе) | Создавать (в целевом проекте) |
|------------|----------------------|-------------------------------|
| Изучить роль | [.claude/agents/architect.md](../.claude/agents/architect.md) | — |
| DDD/Hexagonal | [knowledge/architecture/ddd-hexagonal.md](../knowledge/architecture/ddd-hexagonal.md) | — |
| HTTP-only | [knowledge/architecture/http-only.md](../knowledge/architecture/http-only.md) | — |
| Шаблон плана | [docs/templates/architecture-template.md](templates/architecture-template.md) | — |
| Создать план | — | `ai-docs/docs/architecture/{name}-plan.md` |

### Режим FEATURE

| Что делать | Читать (в генераторе) | Создавать (в целевом проекте) |
|------------|----------------------|-------------------------------|
| Изучить роль | [.claude/agents/architect.md](../.claude/agents/architect.md) | — |
| Существующая архитектура | — | `ai-docs/docs/architecture/*.md` |
| Создать план фичи | — | `ai-docs/docs/plans/{feature}-plan.md` |

**Чек-лист ворот PLAN_APPROVED**:
- [ ] Компоненты системы описаны
- [ ] API контракты определены
- [ ] NFR учтены
- [ ] **План утверждён пользователем**
- [ ] `.pipeline-state.json` обновлён

---

## Этап 4: Реализация

**Команда**: `/generate`
**Агент**: Реализатор
**Ворота**: `IMPLEMENT_OK`

| Что делать | Читать (в генераторе) | Создавать (в целевом проекте) |
|------------|----------------------|-------------------------------|
| Изучить роль | [.claude/agents/implementer.md](../.claude/agents/implementer.md) | — |
| Соглашения | [conventions.md](../conventions.md) | — |
| Шаблоны сервисов | [templates/services/](../templates/services/) | — |
| Шаблоны инфраструктуры | [templates/infrastructure/](../templates/infrastructure/) | — |
| Инфраструктура | — | `docker-compose.yml`, `Makefile` |
| Data Service | — | `services/{name}_data/` |
| Business API | — | `services/{name}_api/` |
| Bot (опционально) | — | `services/{name}_bot/` |
| Worker (опционально) | — | `services/{name}_worker/` |
| Тесты | — | `services/*/tests/` |

**Чек-лист ворот IMPLEMENT_OK**:
- [ ] Код написан согласно плану
- [ ] Unit-тесты проходят
- [ ] Структура DDD/Hexagonal соблюдена
- [ ] Type hints везде
- [ ] `.pipeline-state.json` обновлён

---

## Этап 5: Ревью

**Команда**: `/review`
**Агент**: Ревьюер
**Ворота**: `REVIEW_OK`

| Что делать | Читать (в генераторе) | Создавать (в целевом проекте) |
|------------|----------------------|-------------------------------|
| Изучить роль | [.claude/agents/reviewer.md](../.claude/agents/reviewer.md) | — |
| Соглашения | [conventions.md](../conventions.md) | — |
| Проверить код | — | `services/*/` |
| Проверить план | — | `ai-docs/docs/architecture/*.md` |
| Создать отчёт | — | `ai-docs/docs/reports/review-report.md` |

**Чек-лист ворот REVIEW_OK**:
- [ ] Архитектура соответствует плану
- [ ] conventions.md соблюдён
- [ ] DRY/KISS/YAGNI соблюдены
- [ ] Нет Blocker/Critical замечаний
- [ ] `.pipeline-state.json` обновлён

---

## Этап 6: QA

**Команда**: `/test`
**Агент**: QA
**Ворота**: `QA_PASSED`

| Что делать | Читать (в генераторе) | Создавать (в целевом проекте) |
|------------|----------------------|-------------------------------|
| Изучить роль | [.claude/agents/qa.md](../.claude/agents/qa.md) | — |
| Тестирование | [knowledge/quality/testing.md](../knowledge/quality/testing.md) | — |
| PRD (требования) | — | `ai-docs/docs/prd/*.md` |
| Запустить тесты | — | `pytest services/*/tests/` |
| Создать отчёт | — | `ai-docs/docs/reports/qa-report.md` |

**Чек-лист ворот QA_PASSED**:
- [ ] Все тесты проходят
- [ ] Coverage ≥75%
- [ ] Нет Critical/Blocker багов
- [ ] Требования верифицированы
- [ ] `.pipeline-state.json` обновлён

---

## Этап 7: Валидация

**Команда**: `/validate`
**Агент**: Валидатор
**Ворота**: `ALL_GATES_PASSED`

| Что делать | Читать (в генераторе) | Создавать (в целевом проекте) |
|------------|----------------------|-------------------------------|
| Изучить роль | [.claude/agents/validator.md](../.claude/agents/validator.md) | — |
| Проверить все артефакты | — | `ai-docs/docs/` |
| Проверить все ворота | — | `.pipeline-state.json` |
| Создать RTM | — | `ai-docs/docs/rtm.md` |
| Создать отчёт | — | `ai-docs/docs/reports/validation-report.md` |

**Чек-лист ворот ALL_GATES_PASSED**:
- [ ] PRD_READY ✓
- [ ] RESEARCH_DONE ✓
- [ ] PLAN_APPROVED ✓
- [ ] IMPLEMENT_OK ✓
- [ ] REVIEW_OK ✓
- [ ] QA_PASSED ✓
- [ ] RTM актуальна
- [ ] Все артефакты существуют

---

## Этап 8: Деплой

**Команда**: `/deploy`
**Агент**: Валидатор
**Ворота**: `DEPLOYED`

| Что делать | Читать (в генераторе) | Создавать (в целевом проекте) |
|------------|----------------------|-------------------------------|
| Изучить роль | [.claude/agents/validator.md](../.claude/agents/validator.md) | — |
| Docker | [knowledge/infrastructure/docker.md](../knowledge/infrastructure/docker.md) | — |
| Собрать | — | `make build` |
| Запустить | — | `make up` |
| Проверить | — | `make health` |

**Чек-лист ворот DEPLOYED**:
- [ ] Контейнеры собраны
- [ ] Приложение запущено
- [ ] Health-check проходит
- [ ] Базовые сценарии работают

---

## Сводная таблица

| # | Этап | Команда | Агент | Читает | Создаёт | Ворота |
|---|------|---------|-------|--------|---------|--------|
| 1 | Идея | `/idea` | Аналитик | CLAUDE, workflow, analyst, prd-template | PRD, state | PRD_READY |
| 2 | Исследование | `/research` | Исследователь | researcher, knowledge | (state) | RESEARCH_DONE |
| 3 | Архитектура | `/plan` | Архитектор | architect, ddd, http-only | План | PLAN_APPROVED |
| 4 | Реализация | `/generate` | Реализатор | implementer, conventions, templates | Код, тесты | IMPLEMENT_OK |
| 5 | Ревью | `/review` | Ревьюер | reviewer, conventions | Отчёт | REVIEW_OK |
| 6 | QA | `/test` | QA | qa, testing | Отчёт QA | QA_PASSED |
| 7 | Валидация | `/validate` | Валидатор | validator | RTM, отчёт | ALL_GATES_PASSED |
| 8 | Деплой | `/deploy` | Валидатор | docker | — | DEPLOYED |

---

## См. также

- [INDEX.md](INDEX.md) — Полный индекс файлов генератора
- [target-project-structure.md](target-project-structure.md) — Структура целевого проекта
- [workflow.md](../workflow.md) — Детальное описание процесса

---

**Версия**: 1.0
**Создан**: 2025-12-21
