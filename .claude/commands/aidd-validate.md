---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**/*.md), Write(**/*.md), Bash(git :*), Bash(python3 :*)
description: Финальная проверка всех качественных ворот
---

# Команда: /validate

> Запускает Валидатора для финальной проверки.
> **Pipeline State v2**: Поддержка параллельных пайплайнов.

---

## Синтаксис

```bash
/validate
```

---

## Описание

Команда `/aidd-validate` выполняет:
- Проверку всех предыдущих ворот
- Верификацию всех артефактов
- Обновление RTM
- Формирование итогового отчёта

> **VERIFY BEFORE ACT**: Перед созданием файлов/директорий проверьте их
> существование (см. CLAUDE.md, раздел "Критические правила").

---

## Агент

**Валидатор** (`.claude/agents/validator.md`)

---

## Порядок чтения файлов

> **Принцип**: Сначала контекст ЦП, потом инструкции фреймворка.
> **Подробнее**: [docs/initialization.md](../../docs/initialization.md)

### Фаза 1: Контекст целевого проекта

| # | Файл | Условие | Зачем |
|---|------|---------|-------|
| 1 | `./CLAUDE.md` | Если существует | Специфика проекта |
| 2 | `./.pipeline-state.json` | Обязательно | ВСЕ ворота |
| 3 | `./ai-docs/docs/` | Обязательно | ВСЕ артефакты |
| 4 | `./services/` | Обязательно | Весь код |

### Фаза 2: Автомиграция и предусловия

> **Важно**: Перед выполнением команды проверить версию `.pipeline-state.json`
> и выполнить миграцию v1 → v2 если требуется (см. `knowledge/pipeline/automigration.md`).

| Ворота | Проверка (v2) |
|--------|---------------|
| `QA_PASSED` | `active_pipelines[FID].gates.QA_PASSED.passed == true` |
| `coverage` | `active_pipelines[FID].gates.QA_PASSED.coverage >= 75` |

> **Примечание v2**: FID определяется по текущей git ветке.

### Фаза 3: Инструкции фреймворка

| # | Файл | Зачем |
|---|------|-------|
| 5 | `.aidd/CLAUDE.md` | Правила фреймворка |
| 6 | `.aidd/workflow.md` | Процесс и ворота |
| 7 | `.aidd/.claude/commands/validate.md` | Этот файл |
| 8 | `.aidd/.claude/agents/validator.md` | Инструкции роли |

### Фаза 4: Шаблоны

| # | Файл | Условие |
|---|------|---------|
| 9 | `.aidd/templates/documents/rtm-template.md` | Для создания RTM |

---

## Предусловия

| Ворота | Требование |
|--------|------------|
| `QA_PASSED` | Тесты пройдены, покрытие ≥75% |

### Алгоритм проверки (v2)

```python
def check_validate_preconditions() -> tuple[str, dict] | None:
    """
    Проверить предусловия для /validate.

    v2: Определяем FID по git ветке, проверяем active_pipelines[fid].gates
    """
    # 1. Проверить и мигрировать state
    state = ensure_v2_state()  # см. knowledge/pipeline/automigration.md
    if not state:
        print("❌ Пайплайн не инициализирован → /aidd-idea")
        return None

    # 2. Определить FID по текущей git ветке
    fid, pipeline = get_current_feature_context(state)
    if not fid:
        print("❌ Не удалось определить контекст фичи")
        return None

    gates = pipeline.get("gates", {})

    # 3. Проверить QA_PASSED
    qa_gate = gates.get("QA_PASSED", {})
    if not qa_gate.get("passed"):
        print(f"❌ Ворота QA_PASSED не пройдены для {fid}")
        print("   → Сначала выполните /aidd-test")
        return None

    # 4. Проверить покрытие
    coverage = qa_gate.get("coverage", 0)
    if coverage < 75:
        print(f"⚠️  Coverage {coverage}% < 75%, добавьте тесты")
        return None

    print(f"✓ Фича {fid}: {pipeline.get('title')}")
    print(f"  Coverage: {coverage}%")
    return (fid, pipeline)
```

---

## Выходные артефакты (в целевом проекте)

| Артефакт | Путь |
|----------|------|
| Отчёт валидации | `ai-docs/docs/reports/{YYYY-MM-DD}_{FID}_{slug}-validation.md` |
| RTM | `ai-docs/docs/rtm.md` |

### Именование артефакта

FID и slug берутся из `active_pipelines[FID]` в `.pipeline-state.json` (v2):

```python
# Получить данные из state (v2)
fid, pipeline = get_current_feature_context(state)
if not fid:
    print("❌ Не удалось определить контекст фичи")
    return None

slug = pipeline["name"]  # table-booking
date = datetime.now().strftime("%Y-%m-%d")  # 2024-12-23

# Сформировать имя файла
filename = f"{date}_{fid}_{slug}-validation.md"
# → 2024-12-23_F001_table-booking-validation.md
```

### Обновление .pipeline-state.json

После создания отчёта обновить `active_pipelines[FID].artifacts` и `stage` (v2):

```json
{
  "active_pipelines": {
    "F001": {
      "branch": "feature/F001-table-booking",
      "name": "table-booking",
      "title": "Бронирование столиков",
      "stage": "VALIDATED",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "2024-12-23T10:00:00Z"},
        "RESEARCH_DONE": {"passed": true, "passed_at": "2024-12-23T11:00:00Z"},
        "PLAN_APPROVED": {"passed": true, "passed_at": "2024-12-23T12:00:00Z"},
        "IMPLEMENT_OK": {"passed": true, "passed_at": "2024-12-23T14:00:00Z"},
        "REVIEW_OK": {"passed": true, "passed_at": "2024-12-23T15:00:00Z"},
        "QA_PASSED": {"passed": true, "passed_at": "2024-12-23T16:00:00Z"},
        "ALL_GATES_PASSED": {"passed": false}
      },
      "artifacts": {
        "prd": "prd/2024-12-23_F001_table-booking-prd.md",
        "research": "research/2024-12-23_F001_table-booking-research.md",
        "plan": "architecture/2024-12-23_F001_table-booking-plan.md",
        "review": "reports/2024-12-23_F001_table-booking-review.md",
        "qa": "reports/2024-12-23_F001_table-booking-qa.md",
        "validation": "reports/2024-12-23_F001_table-booking-validation.md"
      }
    }
  }
}
```

> **Примечание**: RTM (`rtm.md`) остаётся общим файлом для всего проекта
> и не привязывается к конкретной фиче.

---

## Качественные ворота

### ALL_GATES_PASSED

| Ворота | Статус |
|--------|--------|
| PRD_READY | ✓ |
| RESEARCH_DONE | ✓ |
| PLAN_APPROVED | ✓ |
| IMPLEMENT_OK | ✓ |
| REVIEW_OK | ✓ |
| QA_PASSED | ✓ |

Дополнительно:
- [ ] Все артефакты существуют
- [ ] RTM актуальна
- [ ] **Log-Driven Design проверен** (см. ниже)

### Проверка Log-Driven Design

> Финальная валидация логирования перед деплоем.

| Проверка | Команда |
|----------|---------|
| Middleware | `Grep: "RequestLoggingMiddleware" in services/*/src/main.py` |
| Tracing | `Grep: "setup_tracing_context" in services/` |
| JSON logs | `Grep: "json_logs.*True\|JSONRenderer" in services/` |
| No secrets | `Grep: "logger.*(password\|secret\|token)" in services/` → должно быть 0 |

**При нарушении** — вернуться к `/aidd-generate` для исправления.

---

## Примеры использования

```bash
# После /test
/validate
```

---

## Следующий шаг

После прохождения ворот `ALL_GATES_PASSED`:

```bash
/deploy
```
