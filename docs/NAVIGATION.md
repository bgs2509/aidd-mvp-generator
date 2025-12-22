# Навигационная матрица AIDD-MVP Generator

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

**Команда**: `/init` (ручной) или авто с `/idea`
**Агент**: — (системный)
**Ворота**: `BOOTSTRAP_READY`

| Фаза | # | Проверка/Чтение | Условие |
|------|---|-----------------|---------|
| **Проверки** | 1 | `git rev-parse --git-dir` | Должен быть git репо |
| **Проверки** | 2 | `.aidd/CLAUDE.md` | Фреймворк подключен |
| **Проверки** | 3 | `python3 --version` | >= 3.11 |
| **Проверки** | 4 | `docker --version` | Docker установлен |
| **Фреймворк** | 5 | `.aidd/.claude/commands/init.md` | Всегда |
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

**Команда**: `/idea`
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
| **3. Фреймворк** | 6 | `.aidd/.claude/commands/idea.md` | Всегда |
| **3. Фреймворк** | 7 | `.aidd/.claude/agents/analyst.md` | Всегда |
| **4. Шаблоны** | 8 | `.aidd/templates/documents/prd-template.md` | Если PRD не существует |

**Создавать (в ЦП)**:
- `ai-docs/docs/prd/{name}-prd.md`
- `.pipeline-state.json`

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

| Фаза | # | Читать | Условие |
|------|---|--------|---------|
| **1. ЦП** | 1 | `./CLAUDE.md` | Если существует |
| **1. ЦП** | 2 | `./.pipeline-state.json` | Обязательно |
| **1. ЦП** | 3 | `./ai-docs/docs/prd/*.md` | Обязательно |
| **1. ЦП** | 4 | `./services/` | Для FEATURE режима |
| **2. Ворота** | — | `gates.PRD_READY.passed == true` | Обязательно |
| **3. Фреймворк** | 5 | `.aidd/CLAUDE.md` | Всегда |
| **3. Фреймворк** | 6 | `.aidd/workflow.md` | Всегда |
| **3. Фреймворк** | 7 | `.aidd/.claude/commands/research.md` | Всегда |
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

**Команда**: `/plan` (CREATE) или `/feature-plan` (FEATURE)
**Агент**: Архитектор
**Ворота**: `PLAN_APPROVED`

### Режим CREATE (`/plan`)

| Фаза | # | Читать | Условие |
|------|---|--------|---------|
| **1. ЦП** | 1 | `./CLAUDE.md` | Если существует |
| **1. ЦП** | 2 | `./.pipeline-state.json` | Обязательно |
| **1. ЦП** | 3 | `./ai-docs/docs/prd/*.md` | Обязательно |
| **1. ЦП** | 4 | `./ai-docs/docs/research/*.md` | Обязательно |
| **2. Ворота** | — | `gates.PRD_READY + RESEARCH_DONE` | Обязательно |
| **3. Фреймворк** | 5 | `.aidd/.claude/commands/plan.md` | Всегда |
| **3. Фреймворк** | 6 | `.aidd/.claude/agents/architect.md` | Всегда |
| **4. Шаблоны** | 7 | `.aidd/templates/documents/architecture-template.md` | Всегда |
| **4. База знаний** | 8 | `.aidd/knowledge/architecture/*.md` | Всегда |

### Режим FEATURE (`/feature-plan`)

| Фаза | # | Читать | Условие |
|------|---|--------|---------|
| **1. ЦП** | 1 | `./CLAUDE.md` | Если существует |
| **1. ЦП** | 2 | `./.pipeline-state.json` | Обязательно |
| **1. ЦП** | 3 | `./ai-docs/docs/prd/*.md` | Обязательно |
| **1. ЦП** | 4 | `./ai-docs/docs/research/*.md` | Обязательно |
| **1. ЦП** | 5 | `./ai-docs/docs/architecture/*.md` | Обязательно |
| **1. ЦП** | 6 | `./services/` | Обязательно |
| **2. Ворота** | — | `mode == FEATURE + gates` | Обязательно |
| **3. Фреймворк** | 7 | `.aidd/.claude/commands/feature-plan.md` | Всегда |
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

**Команда**: `/generate`
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
| **3. Фреймворк** | 8 | `.aidd/.claude/commands/generate.md` | Всегда |
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

## Этап 5: Ревью

**Команда**: `/review`
**Агент**: Ревьюер
**Ворота**: `REVIEW_OK`

| Фаза | # | Читать | Условие |
|------|---|--------|---------|
| **1. ЦП** | 1 | `./CLAUDE.md` | Если существует |
| **1. ЦП** | 2 | `./.pipeline-state.json` | Обязательно |
| **1. ЦП** | 3 | `./ai-docs/docs/prd/*.md` | Обязательно |
| **1. ЦП** | 4 | `./ai-docs/docs/architecture/*.md` | Обязательно |
| **1. ЦП** | 5 | `./services/` | Обязательно |
| **2. Ворота** | — | `gates.IMPLEMENT_OK.passed` | Обязательно |
| **3. Фреймворк** | 6 | `.aidd/conventions.md` | Всегда |
| **3. Фреймворк** | 7 | `.aidd/.claude/commands/review.md` | Всегда |
| **3. Фреймворк** | 8 | `.aidd/.claude/agents/reviewer.md` | Всегда |
| **4. База знаний** | 9 | `.aidd/knowledge/architecture/*.md` | По необходимости |

**Создавать (в ЦП)**:
- `ai-docs/docs/reports/review-report.md`

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

| Фаза | # | Читать | Условие |
|------|---|--------|---------|
| **1. ЦП** | 1 | `./CLAUDE.md` | Если существует |
| **1. ЦП** | 2 | `./.pipeline-state.json` | Обязательно |
| **1. ЦП** | 3 | `./ai-docs/docs/prd/*.md` | Обязательно |
| **1. ЦП** | 4 | `./services/*/tests/` | Обязательно |
| **2. Ворота** | — | `gates.REVIEW_OK.passed` | Обязательно |
| **3. Фреймворк** | 5 | `.aidd/.claude/commands/test.md` | Всегда |
| **3. Фреймворк** | 6 | `.aidd/.claude/agents/qa.md` | Всегда |
| **4. База знаний** | 7 | `.aidd/knowledge/quality/testing.md` | По необходимости |

**Создавать (в ЦП)**:
- `ai-docs/docs/reports/qa-report.md`

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

| Фаза | # | Читать | Условие |
|------|---|--------|---------|
| **1. ЦП** | 1 | `./CLAUDE.md` | Если существует |
| **1. ЦП** | 2 | `./.pipeline-state.json` | ВСЕ ворота |
| **1. ЦП** | 3 | `./ai-docs/docs/` | ВСЕ артефакты |
| **1. ЦП** | 4 | `./services/` | Весь код |
| **2. Ворота** | — | `gates.QA_PASSED.passed + coverage >= 75` | Обязательно |
| **3. Фреймворк** | 5 | `.aidd/.claude/commands/validate.md` | Всегда |
| **3. Фреймворк** | 6 | `.aidd/.claude/agents/validator.md` | Всегда |
| **4. Шаблоны** | 7 | `.aidd/templates/documents/rtm-template.md` | Если RTM не существует |

**Создавать (в ЦП)**:
- `ai-docs/docs/rtm.md`
- `ai-docs/docs/reports/validation-report.md`

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

| Фаза | # | Читать | Условие |
|------|---|--------|---------|
| **1. ЦП** | 1 | `./CLAUDE.md` | Если существует |
| **1. ЦП** | 2 | `./.pipeline-state.json` | ВСЕ ворота |
| **1. ЦП** | 3 | `./docker-compose.yml` | Обязательно |
| **1. ЦП** | 4 | `./Makefile` | Обязательно |
| **2. Ворота** | — | `gates.ALL_GATES_PASSED + все предыдущие` | Обязательно |
| **3. Фреймворк** | 5 | `.aidd/.claude/commands/deploy.md` | Всегда |
| **3. Фреймворк** | 6 | `.aidd/.claude/agents/validator.md` | Всегда |
| **4. База знаний** | 7 | `.aidd/knowledge/infrastructure/docker.md` | По необходимости |

**Выполнять**:
- `make build`
- `make up`
- `make health`

**Чек-лист ворот DEPLOYED**:
- [ ] Контейнеры собраны
- [ ] Приложение запущено
- [ ] Health-check проходит
- [ ] Базовые сценарии работают

---

## Сводная таблица

| # | Этап | Команда | Агент | Читает | Создаёт | Ворота |
|---|------|---------|-------|--------|---------|--------|
| 0 | Bootstrap | `/init` | — | init.md, target-structure | Структура ЦП | BOOTSTRAP_READY |
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

- [initialization.md](initialization.md) — Алгоритм инициализации (4 фазы)
- [INDEX.md](INDEX.md) — Полный индекс файлов генератора
- [PIPELINE-TREE.md](PIPELINE-TREE.md) — Дерево всех пайплайнов
- [target-project-structure.md](target-project-structure.md) — Структура целевого проекта
- [workflow.md](../workflow.md) — Детальное описание процесса

---

**Версия**: 2.0
**Обновлён**: 2025-12-21
