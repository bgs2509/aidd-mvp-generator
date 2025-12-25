---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**/*.md), Write(**/*.md), Bash(git :*), Bash(python3 :*)
description: Создать архитектурный план для нового MVP проекта
---

# Команда: /plan

> Запускает Архитектора для проектирования системы (режим CREATE).
> **Pipeline State v2**: Поддержка параллельных пайплайнов.

---

## Синтаксис

```bash
/plan
```

---

## Описание

Команда `/aidd-plan` создаёт полный архитектурный план для нового MVP проекта.
Используется в режиме CREATE для проектирования системы с нуля.

> **VERIFY BEFORE ACT**: Перед созданием файлов/директорий проверьте их
> существование (см. CLAUDE.md, раздел "Критические правила").

---

## Агент

**Архитектор** (`.claude/agents/architect.md`)

---

## Порядок чтения файлов

> **Принцип**: Сначала контекст ЦП, потом инструкции фреймворка.
> **Подробнее**: [docs/initialization.md](../../docs/initialization.md)

### Фаза 1: Контекст целевого проекта

| # | Файл | Условие | Зачем |
|---|------|---------|-------|
| 1 | `./CLAUDE.md` | Если существует | Специфика проекта |
| 2 | `./.pipeline-state.json` | Обязательно | Режим, этап, ворота |
| 3 | `./ai-docs/docs/prd/*.md` | Обязательно | Требования из PRD |

### Фаза 2: Автомиграция и предусловия

> **Важно**: Перед выполнением команды проверить версию `.pipeline-state.json`
> и выполнить миграцию v1 → v2 если требуется (см. `knowledge/pipeline/automigration.md`).

| Ворота | Проверка (v2) |
|--------|---------------|
| `PRD_READY` | `active_pipelines[FID].gates.PRD_READY.passed == true` |
| `RESEARCH_DONE` | `active_pipelines[FID].gates.RESEARCH_DONE.passed == true` |

> **Примечание v2**: FID определяется по текущей git ветке.

### Фаза 3: Инструкции фреймворка

| # | Файл | Зачем |
|---|------|-------|
| 4 | `.aidd/CLAUDE.md` | Правила фреймворка |
| 5 | `.aidd/workflow.md` | Процесс и ворота |
| 6 | `.aidd/.claude/commands/plan.md` | Этот файл |
| 7 | `.aidd/.claude/agents/architect.md` | Инструкции роли |

### Фаза 4: Шаблоны и база знаний

| # | Файл | Условие |
|---|------|---------|
| 8 | `.aidd/templates/documents/architecture-template.md` | Для создания плана |
| 9 | `.aidd/knowledge/architecture/ddd-hexagonal.md` | Архитектурные паттерны |
| 10 | `.aidd/knowledge/architecture/http-only.md` | HTTP-only доступ |

---

## Режимы

Только **CREATE** — для новых проектов.

Для добавления фичи в существующий проект используйте `/aidd-feature-plan`.

---

## Предусловия

| Ворота | Требование |
|--------|------------|
| `PRD_READY` | PRD документ существует |
| `RESEARCH_DONE` | Исследование завершено |

### Алгоритм проверки (v2)

```python
def check_plan_preconditions() -> tuple[str, dict] | None:
    """
    Проверить предусловия для /plan.

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

    # 3. Проверить PRD_READY
    if not gates.get("PRD_READY", {}).get("passed"):
        print(f"❌ Ворота PRD_READY не пройдены для {fid}")
        print("   → Сначала выполните /aidd-idea")
        return None

    # 4. Проверить RESEARCH_DONE
    if not gates.get("RESEARCH_DONE", {}).get("passed"):
        print(f"❌ Ворота RESEARCH_DONE не пройдены для {fid}")
        print("   → Сначала выполните /aidd-research")
        return None

    print(f"✓ Фича {fid}: {pipeline.get('title')}")
    return (fid, pipeline)
```

---

## Выходные артефакты (в целевом проекте)

| Артефакт | Путь |
|----------|------|
| Архитектурный план | `ai-docs/docs/architecture/{YYYY-MM-DD}_{FID}_{slug}-plan.md` |

### Именование артефакта

FID и slug берутся из `current_feature` в `.pipeline-state.json`:

```python
# Получить данные из state
fid = state["current_feature"]["id"]      # F001
slug = state["current_feature"]["name"]    # table-booking
date = datetime.now().strftime("%Y-%m-%d") # 2024-12-23

# Сформировать имя файла
filename = f"{date}_{fid}_{slug}-plan.md"
# → 2024-12-23_F001_table-booking-plan.md
```

### Обновление .pipeline-state.json

После создания плана обновить `current_feature.artifacts`:

```json
{
  "current_feature": {
    "id": "F001",
    "name": "table-booking",
    "stage": "PLAN",
    "artifacts": {
      "prd": "prd/2024-12-23_F001_table-booking-prd.md",
      "research": "research/2024-12-23_F001_table-booking-research.md",
      "plan": "architecture/2024-12-23_F001_table-booking-plan.md"
    }
  }
}
```

---

## Качественные ворота

### PLAN_APPROVED

| Критерий | Описание |
|----------|----------|
| Компоненты | Все компоненты системы определены |
| API контракты | Эндпоинты и схемы описаны |
| NFR | Нефункциональные требования учтены |
| **Утверждение** | План утверждён пользователем |

**ВАЖНО**: Требуется явное подтверждение от пользователя!

---

## Примеры использования

```bash
# После /research
/plan
```

---

## Следующий шаг

После прохождения ворот `PLAN_APPROVED`:

```bash
/generate
```
