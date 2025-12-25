---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**/*.md), Write(**/*.md), Bash(git :*), Bash(python3 :*)
description: Код-ревью сгенерированного кода
---

# Команда: /review

> Запускает Ревьюера для код-ревью.
> **Pipeline State v2**: Поддержка параллельных пайплайнов.

---

## Синтаксис

```bash
/review
```

---

## Описание

Команда `/aidd-review` выполняет код-ревью сгенерированного кода:
- Проверка соответствия архитектуре
- Проверка соглашений (conventions.md)
- Проверка DRY/KISS/YAGNI

> **VERIFY BEFORE ACT**: Перед созданием файлов/директорий проверьте их
> существование (см. CLAUDE.md, раздел "Критические правила").

---

## Агент

**Ревьюер** (`.claude/agents/reviewer.md`)

---

## Порядок чтения файлов

> **Принцип**: Сначала контекст ЦП, потом инструкции фреймворка.
> **Подробнее**: [docs/initialization.md](../../docs/initialization.md)

### Фаза 1: Контекст целевого проекта

| # | Файл | Условие | Зачем |
|---|------|---------|-------|
| 1 | `./CLAUDE.md` | Если существует | Специфика проекта |
| 2 | `./.pipeline-state.json` | Обязательно | Режим, этап, ворота |
| 3 | `./ai-docs/docs/prd/*.md` | Обязательно | Требования |
| 4 | `./ai-docs/docs/architecture/*.md` | Обязательно | План для сверки |
| 5 | `./services/` | Обязательно | Код для ревью |

### Фаза 2: Автомиграция и предусловия

> **Важно**: Перед выполнением команды проверить версию `.pipeline-state.json`
> и выполнить миграцию v1 → v2 если требуется (см. `knowledge/pipeline/automigration.md`).

| Ворота | Проверка (v2) |
|--------|---------------|
| `IMPLEMENT_OK` | `active_pipelines[FID].gates.IMPLEMENT_OK.passed == true` |

> **Примечание v2**: FID определяется по текущей git ветке.

### Фаза 3: Инструкции фреймворка

| # | Файл | Зачем |
|---|------|-------|
| 6 | `.aidd/CLAUDE.md` | Правила фреймворка |
| 7 | `.aidd/workflow.md` | Процесс и ворота |
| 8 | `.aidd/conventions.md` | Соглашения для проверки |
| 9 | `.aidd/.claude/commands/review.md` | Этот файл |
| 10 | `.aidd/.claude/agents/reviewer.md` | Инструкции роли |

### Фаза 4: База знаний

| # | Файл | Условие |
|---|------|---------|
| 11 | `.aidd/knowledge/architecture/*.md` | Архитектурные принципы |

---

## Предусловия

| Ворота | Требование |
|--------|------------|
| `IMPLEMENT_OK` | Код сгенерирован, тесты проходят |

### Алгоритм проверки (v2)

```python
def check_review_preconditions() -> tuple[str, dict] | None:
    """
    Проверить предусловия для /review.

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

    # 3. Проверить IMPLEMENT_OK
    if not pipeline["gates"].get("IMPLEMENT_OK", {}).get("passed"):
        print(f"❌ Ворота IMPLEMENT_OK не пройдены для {fid}")
        print("   → Сначала выполните /aidd-generate")
        return None

    print(f"✓ Фича {fid}: {pipeline.get('title')}")
    return (fid, pipeline)
```

---

## Выходные артефакты (в целевом проекте)

| Артефакт | Путь |
|----------|------|
| Отчёт ревью | `ai-docs/docs/reports/{YYYY-MM-DD}_{FID}_{slug}-review.md` |

### Именование артефакта

FID и slug берутся из `current_feature` в `.pipeline-state.json`:

```python
# Получить данные из state
fid = state["current_feature"]["id"]      # F001
slug = state["current_feature"]["name"]    # table-booking
date = datetime.now().strftime("%Y-%m-%d") # 2024-12-23

# Сформировать имя файла
filename = f"{date}_{fid}_{slug}-review.md"
# → 2024-12-23_F001_table-booking-review.md
```

### Обновление .pipeline-state.json

После создания отчёта обновить `current_feature.artifacts`:

```json
{
  "current_feature": {
    "id": "F001",
    "name": "table-booking",
    "stage": "REVIEW",
    "artifacts": {
      "prd": "prd/2024-12-23_F001_table-booking-prd.md",
      "research": "research/2024-12-23_F001_table-booking-research.md",
      "plan": "architecture/2024-12-23_F001_table-booking-plan.md",
      "review": "reports/2024-12-23_F001_table-booking-review.md"
    }
  }
}
```

---

## Качественные ворота

### REVIEW_OK

| Критерий | Описание |
|----------|----------|
| Архитектура | Соответствует плану |
| Соглашения | conventions.md соблюдён |
| DRY | Нет дублирования |
| KISS | Решения простые |
| YAGNI | Нет лишнего кода |
| Замечания | Нет Blocker/Critical |

---

## Примеры использования

```bash
# После /generate
/review
```

---

## Следующий шаг

После прохождения ворот `REVIEW_OK`:

```bash
/test
```
