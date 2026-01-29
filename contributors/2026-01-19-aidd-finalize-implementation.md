# План реализации команды /aidd-validate

**Примечание:** В этом документе встречаются устаревшие команды `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`. Актуальные команды: `/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`.


**Дата**: 2026-01-19
**Цель**: Объединить 4 этапа пайплайна (review/test/validate/deploy) в одну команду
**Артефакт**: Один итоговый `reports/{date}_{FID}_{slug}-completion.md` вместо 4 отдельных отчётов
**Экономия**: ~900 строк кода команд, ~180 токенов на проект, упрощение с 9 этапов до 6

---

## 1. Анализ текущих команд

### 1.1 Структура существующих команд

| Команда | Строк | Агент | Ворота IN | Ворота OUT | Ключевые действия |
|---------|-------|-------|-----------|------------|-------------------|
| `aidd-review.md` | ~350 | Ревьюер | IMPLEMENT_OK | REVIEW_OK | Проверка архитектуры, conventions, DRY/KISS/YAGNI |
| `aidd-test.md` | ~320 | QA | REVIEW_OK | QA_PASSED | Запуск тестов, проверка coverage ≥75% |
| `aidd-validate.md` | ~380 | Валидатор | QA_PASSED | ALL_GATES_PASSED | RTM, проверка всех артефактов |
| `aidd-deploy.md` | ~420 | Валидатор | ALL_GATES_PASSED | DEPLOYED | docker-compose up, health checks, completion report |

**Итого**: ~1,470 строк, 4 файла, 4 ворот

### 1.2 Проблемы текущего подхода

1. **Избыточность артефактов**: 4 отчёта разбросаны по папкам
   - ❌ `reports/review-report.md`
   - ❌ `reports/qa-report.md`
   - ❌ `architecture/{name}-rtm.md`
   - ✅ `reports/{date}_{FID}_{slug}-completion.md` (остаётся)

2. **Дублирование контента**: ~180 строк повторяются в каждой команде
   - Front matter, ENFORCEMENT блок, синтаксис, порядок чтения

3. **Сложность для пользователя**: 4 команды вместо 1

---

## 2. Архитектура новой команды /aidd-validate

### 2.1 Концепция

**Идея**: Одна команда выполняет 4 последовательных шага:
```
IMPLEMENT_OK → [Review] → [Test] → [Validate] → [Deploy + Report] → DEPLOYED
```

**Ключевое изменение**:
```
Было: 4 команды → 4 отчёта (review-report, qa-report, RTM, completion)
Стало: 1 команда → 1 отчёт (completion report со всей информацией)
```

**Преимущества**:
- ✅ Атомарность: всё или ничего
- ✅ Упрощение для пользователя: 1 команда вместо 4
- ✅ Один файл истории: вся информация о фиче в одном месте
- ✅ Меньше дублирования: ~900 строк экономии

**Компромиссы**:
- ⚠️ Потеря гранулярности: нельзя остановиться между этапами
- ⚠️ Длительное выполнение: 5-10 минут

---

### 2.2 Ворота (gates)

**Новая логика**:
```json
{
  "gates": {
    "REVIEW_OK": {
      "passed": false,
      "timestamp": null,
      "internal": true  // Промежуточное ворота внутри /aidd-validate
    },
    "QA_PASSED": {
      "passed": false,
      "timestamp": null,
      "internal": true
    },
    "ALL_GATES_PASSED": {
      "passed": false,
      "timestamp": null,
      "internal": true
    },
    "DEPLOYED": {
      "passed": false,
      "timestamp": null,
      "internal": false  // Финальное ворота
    }
  }
}
```

**Поведение**:
- AI устанавливает промежуточные ворота (REVIEW_OK, QA_PASSED, ALL_GATES_PASSED) внутри команды
- Только DEPLOYED gate видим пользователю как "команда завершена"
- Если fail на любом шаге → откат, gate не устанавливается

---

## 3. Структура Completion Report (единственный артефакт)

**Путь**: `ai-docs/docs/_validation/{date}_{FID}_{slug}-completion.md`

**Содержит всю информацию о фиче**:

```markdown
# Completion Report: {project_name}

## Executive Summary
- Дата: {date}
- Режим: CREATE/FEATURE
- Статус: DEPLOYED ✅

## Code Review Summary
- ✅ Architecture: HTTP-only, DDD/Hexagonal
- ✅ Conventions: naming, type hints, docstrings
- ✅ Quality Cascade: QC-1 (DRY), QC-2 (KISS), QC-3 (YAGNI), QC-17 (Security)
- ⚠️ Issues found: [если есть]

## Testing Summary
- Total tests: {count}
- Passed: {passed}
- Coverage: {coverage}% (≥75% required)
- Services tested: {list}

## Requirements Traceability
| Req ID | PRD Requirement | Implemented In | Test Coverage | Status |
|--------|----------------|----------------|---------------|--------|
| REQ-1  | ...            | ...            | ...           | ✅     |

## Реализованные компоненты
- Services: business_api, data_api
- Models: User, Task
- API Endpoints: POST /api/v1/tasks, ...

## Architecture Decision Records (ADR)
### ADR-1: [название]
**Обоснование**: [почему]

## Scope Changes
[Если были отклонения от плана]

## Known Limitations
[Ограничения и workarounds]

## Deployment
- Status: ✅ SUCCESS
- Health checks: ✅ All passed
- Commands:
  ```bash
  docker-compose up -d
  curl http://localhost:8000/health
  ```

## Метрики
- Test coverage: {coverage}%
- Services: {count}
- API endpoints: {count}

## Ссылки
- PRD: [link]
- Architecture: [link]
```

**Зачем нужен**:
- ✅ Single source of truth для фичи
- ✅ ADR документированы
- ✅ Scope changes отслеживаются
- ✅ Known issues не теряются

---

## 4. План реализации (краткий)

### Шаг 1: Создать команду aidd-finalize.md

**Файл**: `.claude/commands/aidd-validate.md`

**Ключевые секции**:
- Front matter с allowed-tools
- ENFORCEMENT блок
- 4 последовательных шага (Review → Test → Validate → Deploy)
- Инструкции по генерации Completion Report
- Чеклист ворот (все 4 шага)

**Агент**: Валидатор (расширенная роль — выполняет все 4 этапа)

---

### Шаг 2: Обновить агента validator.md

**Файл**: `.claude/agents/validator.md`

**Добавить ответственности**:
- Code Review (как Ревьюер)
- QA Testing (как QA)
- Validation (родная роль)
- Deploy + Completion Report (родная роль)

---

### Шаг 3: Обновить workflow.md

**Изменения в `workflow.md`**:

#### Таблица этапов (было 9 → стало 6):

```markdown
| # | Этап | Команда | Агент | Ворота | Артефакт |
|---|------|---------|-------|--------|----------|
| 0 | Bootstrap | /aidd-init | — | BOOTSTRAP_READY | Структура ЦП |
| 1 | Идея | /aidd-analyze | Аналитик | PRD_READY | prd/{name}-prd.md |
| 2 | Исследование | /aidd-research | Исследователь | RESEARCH_DONE | research/{name}-research.md |
| 3 | Архитектура | /aidd-plan | Архитектор | PLAN_APPROVED | architecture/{name}-plan.md |
| 4 | Реализация | /aidd-code | Реализатор | IMPLEMENT_OK | services/, тесты |
| 5 | Quality & Deploy | /aidd-validate | Валидатор | DEPLOYED | reports/, RTM, running app |
```

#### Описание этапа 5:

```markdown
### Этап 5: Quality & Deploy

**Команда**: `/aidd-validate`
**Агент**: Валидатор
**Вход**: `IMPLEMENT_OK` gate passed
**Выход**: `DEPLOYED` gate passed

**Описание**:
Комплексная проверка качества и деплой в 4 шага:
1. Code Review — проверка архитектуры и стандартов
2. Testing — запуск тестов, coverage ≥75%
3. Validation — RTM, проверка артефактов
4. Deploy — docker-compose up, health checks, completion report

**Артефакты**:
- `reports/review-report.md`
- `reports/qa-report.md`
- `architecture/{name}-rtm.md`
- `reports/{date}_{FID}_{slug}-completion.md`
- Работающее приложение (docker-compose)

**Время выполнения**: 5-10 минут
```

---

### Шаг 6: Обновить CLAUDE.md

**Изменения в `CLAUDE.md`**:

#### 1. Обновить ASCII пайплайн:

```markdown
┌──────────────────────────────────────────────────────────────────────┐
│                       PIPELINE (этапы 0-5)                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────┐  ┌──────────────┐  ┌───────────┐  ┌──────────────┐  │
│  │/aidd-init  │─▶│/aidd-research│─▶│/aidd-plan │─▶│/aidd-code│  │
│  │  Этап 0    │  │   Этап 2     │  │  Этап 3   │  │   Этап 4     │  │
│  └─────┬──────┘  └──────┬───────┘  └─────┬─────┘  └──────┬───────┘  │
│        │                │                │               │           │
│  BOOTSTRAP_READY  RESEARCH_DONE    PLAN_APPROVED   IMPLEMENT_OK     │
│                                          ⚠️                          │
│                                 Требует подтверждения                │
│                                    пользователя!                     │
│                                                                      │
│  ┌────────────────────────┐                                          │
│  │ /aidd-validate         │                                          │
│  │   Этап 5               │                                          │
│  │ (Quality & Deploy)     │                                          │
│  └──────┬─────────────────┘                                          │
│       │                                                              │
│  DEPLOYED                                                            │
│  ├─ Code Review (REVIEW_OK)                                          │
│  ├─ Testing (QA_PASSED)                                              │
│  ├─ Validation (ALL_GATES_PASSED)                                    │
│  └─ Deploy (docker, health checks)                                   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

#### 2. Обновить таблицу команд:

```markdown
| # | Этап | Команда | Агент | Ворота | Артефакт |
|---|------|---------|-------|--------|----------|
| 0 | Bootstrap | `/aidd-init` | — | `BOOTSTRAP_READY` | Структура ЦП |
| 1 | Идея | `/aidd-analyze` | Аналитик | `PRD_READY` | `prd/{name}-prd.md` |
| 2 | Исследование | `/aidd-research` | Исследователь | `RESEARCH_DONE` | `research/{name}-research.md` |
| 3 | Архитектура (CREATE) | `/aidd-plan` | Архитектор | `PLAN_APPROVED` | `architecture/{name}-plan.md` |
| 3 | Архитектура (FEATURE) | `/aidd-plan-feature` | Архитектор | `PLAN_APPROVED` | `plans/{feature}-plan.md` |
| 4 | Реализация | `/aidd-code` | Реализатор | `IMPLEMENT_OK` | `services/`, тесты |
| 5 | Quality & Deploy | `/aidd-validate` | Валидатор | `DEPLOYED` | reports/, RTM, app |
```

---

### Шаг 7: Удалить старые команды

**Файлы к удалению**:
```
.claude/commands/aidd-review.md
.claude/commands/aidd-test.md
.claude/commands/aidd-validate.md
.claude/commands/aidd-deploy.md
```

**⚠️ ВАЖНО**: Сделать это ПОСЛЕ того как aidd-finalize.md создан и протестирован!

**Процесс**:
1. Создать backup старых команд (git commit перед удалением)
2. Удалить 4 файла
3. Протестировать /aidd-validate на тестовом проекте
4. Если проблемы — откатить через git revert

---

### Шаг 8: Обновить docs/INDEX.md

**Изменения**:

```markdown
## Команды (.claude/commands/)

| Файл | Описание | Этап | Агент |
|------|----------|------|-------|
| aidd-init.md | Bootstrap пайплайна | 0 | — |
| aidd-idea.md | Создание PRD | 1 | Аналитик |
| aidd-research.md | Исследование кодовой базы | 2 | Исследователь |
| aidd-plan.md | Архитектура (CREATE) | 3 | Архитектор |
| aidd-feature-plan.md | Архитектура (FEATURE) | 3 | Архитектор |
| aidd-generate.md | Генерация кода | 4 | Реализатор |
| aidd-finalize.md | Quality & Deploy | 5 | Валидатор |
```

Удалить строки:
```markdown
❌ aidd-review.md
❌ aidd-test.md
❌ aidd-validate.md
❌ aidd-deploy.md
```

---

### Шаг 9: Создать тестовый проект

**Цель**: Протестировать /aidd-validate на реальном проекте

**План теста**:
```bash
# 1. Создать тестовый проект
mkdir test-finalize
cd test-finalize
git init
git submodule add <aidd-mvp-generator> .aidd

# 2. Выполнить этапы 0-4
/aidd-init
/aidd-analyze "Простой CRUD API для задач"
/aidd-research
/aidd-plan
# Утвердить план
/aidd-code

# 3. Запустить /aidd-validate
/aidd-validate

# 4. Проверить результаты
- [ ] REVIEW_OK gate установлен
- [ ] QA_PASSED gate установлен
- [ ] ALL_GATES_PASSED gate установлен
- [ ] DEPLOYED gate установлен
- [ ] review-report.md создан
- [ ] qa-report.md создан
- [ ] RTM создан
- [ ] completion-report.md создан
- [ ] docker-compose up работает
- [ ] health checks возвращают 200
```

---

### Шаг 7: Удалить старые команды

**⚠️ ТОЛЬКО ПОСЛЕ создания и тестирования aidd-finalize.md!**

Удалить файлы:
- `.claude/commands/aidd-review.md`
- `.claude/commands/aidd-test.md`
- `.claude/commands/aidd-validate.md`
- `.claude/commands/aidd-deploy.md`

---

## 5. Чеклист выполнения плана

### Подготовка
- [ ] План прочитан и понят
- [ ] Создан backup текущего состояния (git commit)

### Реализация
- [ ] Шаг 1: Создан файл `.claude/commands/aidd-validate.md` (с 4 шагами + Completion Report)
- [ ] Шаг 2: Обновлен файл `.claude/agents/validator.md` (расширенные ответственности)
- [ ] Шаг 3: Обновлен файл `workflow.md` (6 этапов вместо 9)
- [ ] Шаг 4: Обновлен файл `CLAUDE.md` (ASCII пайплайн, таблица команд)
- [ ] Шаг 5: Обновлен файл `docs/INDEX.md` (список команд)
- [ ] Шаг 6: Протестирована команда `/aidd-validate` на тестовом проекте
- [ ] Шаг 7: Удалены 4 старые команды (review/test/validate/deploy)

### Валидация
- [ ] `/aidd-validate` завершается без ошибок
- [ ] Единственный артефакт: `reports/{date}_{FID}_{slug}-completion.md`
- [ ] Completion Report содержит все секции (Executive Summary, Code Review, Testing, Traceability, ADR, Deployment, Metrics)
- [ ] docker-compose up работает
- [ ] Health checks возвращают 200 OK
- [ ] Все 4 ворота установлены (REVIEW_OK, QA_PASSED, ALL_GATES_PASSED, DEPLOYED)

### Финализация
- [ ] Git commit с изменениями
- [ ] Документация обновлена
- [ ] План завершён

---

## 6. Метрики успеха

| Метрика | До | После | Улучшение |
|---------|-----|-------|-----------|
| Количество команд | 10 | 7 | -3 команды |
| Количество этапов | 9 | 6 | -3 этапа |
| Артефактов на проект | 7 | 4 | -3 файла |
| Строк в командах | ~1,470 (4 файла) | ~600 (1 файл) | -870 строк (-59%) |
| Токенов на проект | ~20,000 | ~19,820 | -180 токенов |
| Шагов для пользователя | 4 команды | 1 команда | -3 шага |

**Ключевые улучшения**:
- ✅ Один Completion Report вместо 4 отдельных отчётов
- ✅ Single source of truth для истории фичи
- ✅ Упрощение пайплайна для пользователя
- ✅ Меньше дублирования кода

---

**Статус плана**: Готов к реализации
**Приоритет**: Высокий (упрощение и оптимизация)
