---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**/*.md), Write(**/*.md), Bash(git :*), Bash(python3 :*)
description: Создать архитектурный план для нового MVP проекта
---

**Примечание (Migration Mode v2.4):** Фреймворк поддерживает обе версии команд — legacy naming (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`) и new naming (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`) работают идентично.


> ⚠️ **ENFORCEMENT**: Перед завершением этой команды AI ОБЯЗАН:
> 1. Найти секцию "Чеклист ворот" в конце этого файла
> 2. Создать TodoWrite со ВСЕМИ пунктами (особенно 🔴)
> 3. Выполнить ВСЕ пункты и отметить completed
> 4. Команда завершена ТОЛЬКО когда все 🔴 пункты ✅
>
> Правила: `.aidd/CLAUDE.md` → "Выполнение команд /aidd-*"

# Команда: /plan

> Запускает Планировщика для проектирования системы (режим CREATE).
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

**Планировщик** (`.claude/agents/planner.md`)

---

## Порядок чтения файлов

> **Принцип**: Сначала контекст ЦП, потом инструкции фреймворка.
> **Подробнее**: [docs/initialization.md](../../docs/initialization.md)

### Фаза 1: Контекст целевого проекта

| # | Файл | Условие | Зачем |
|---|------|---------|-------|
| 1 | `./CLAUDE.md` | Если существует | Специфика проекта |
| 2 | `./.pipeline-state.json` | Обязательно | Режим, этап, ворота |
| 3 | `./ai-docs/docs/_analysis/*.md` | Обязательно | Требования из PRD |

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
| 7 | `.aidd/.claude/agents/planner.md` | Инструкции роли |

### Фаза 4: Шаблоны и база знаний

| # | Файл | Условие |
|---|------|---------|
| 8 | `.aidd/templates/documents/architecture-template.md` | Для создания плана |
| 9 | `.aidd/knowledge/architecture/ddd-hexagonal.md` | Архитектурные паттерны |
| 10 | `.aidd/knowledge/architecture/http-only.md` | HTTP-only доступ |

---

## Режимы

Только **CREATE** — для новых проектов.

Для добавления фичи в существующий проект используйте `/aidd-plan-feature`.

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
        print("❌ Пайплайн не инициализирован → /aidd-analyze")
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
        print("   → Сначала выполните /aidd-analyze")
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

| Артефакт | Путь (v2) | Путь (v3) |
|----------|-----------|-----------|
| Архитектурный план (MVP) | `ai-docs/docs/_plans/mvp/{YYYY-MM-DD}_{FID}_{slug}-plan.md` | `ai-docs/docs/_plans/mvp/{YYYY-MM-DD}_{FID}_{slug}.md` |

> **Примечание (v2.4+)**:
> - **v2** (по умолчанию): Старая структура `architecture/`, имя с дублированием `{name}-plan.md`
> - **v3** (после миграции): Новая структура `_plans/mvp/`, имя без дублирования `{name}.md`
> - Режим определяется из `.pipeline-state.json → naming_version`

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

# Определить naming_version и структуру артефактов
naming_version = state.get("naming_version", "v2")

if naming_version == "v3":
    folder = "_plans/mvp"
    filename = f"{date}_{fid}_{slug}.md"  # Без дублирования
else:
    folder = "architecture"
    filename = f"{date}_{fid}_{slug}-plan.md"  # С дублированием

artifact_path = f"{folder}/{filename}"
# v2: architecture/2024-12-23_F001_table-booking-plan.md
# v3: _plans/mvp/2024-12-23_F001_table-booking.md
```

### Обновление .pipeline-state.json

После создания плана обновить `active_pipelines[FID].artifacts` (v2):

**Пример для v2 (по умолчанию)**:
```json
{
  "naming_version": "v2",
  "active_pipelines": {
    "F001": {
      "branch": "feature/F001-table-booking",
      "name": "table-booking",
      "title": "Бронирование столиков",
      "stage": "PLAN",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "2024-12-23T10:00:00Z"},
        "RESEARCH_DONE": {"passed": true, "passed_at": "2024-12-23T11:00:00Z"},
        "PLAN_APPROVED": {"passed": false}
      },
      "artifacts": {
        "prd": "prd/2024-12-23_F001_table-booking-prd.md",
        "research": "research/2024-12-23_F001_table-booking-research.md",
        "plan": "architecture/2024-12-23_F001_table-booking-plan.md"
      }
    }
  }
}
```

**Пример для v3 (после миграции)**:
```json
{
  "naming_version": "v3",
  "active_pipelines": {
    "F001": {
      "artifacts": {
        "prd": "_analysis/2024-12-23_F001_table-booking.md",
        "research": "_research/2024-12-23_F001_table-booking.md",
        "plan": "_plans/mvp/2024-12-23_F001_table-booking.md"
      }
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

## Чеклист ворот PLAN_APPROVED

> ⚠️ AI ОБЯЗАН создать TodoWrite с этими пунктами.

- [ ] 🔴 Architecture Plan создан в правильной папке:
  - v2: `ai-docs/docs/_plans/mvp/{name}-plan.md`
  - v3: `ai-docs/docs/_plans/mvp/{name}.md`
- [ ] 🔴 Все сервисы определены с типами
- [ ] 🔴 API контракты описаны
- [ ] 🔴 **Пользователь утвердил план** ← КРИТИЧЕСКИ ВАЖНО
- [ ] 🔴 `.pipeline-state.json` обновлён (gate: PLAN_APPROVED, artifact path соответствует naming_version)
- [ ] 🟡 ADR задокументированы

---

## Следующий шаг

После прохождения ворот `PLAN_APPROVED`:

```bash
/generate
```
