---
allowed-tools: Read(*), Glob(*), Grep(*), Bash(git :*), Bash(python3 :*)
description: Анализ кодовой базы и технологий
---

> ⚠️ **ENFORCEMENT**: Перед завершением этой команды AI ОБЯЗАН:
> 1. Найти секцию "Чеклист ворот" в конце этого файла
> 2. Создать TodoWrite со ВСЕМИ пунктами (особенно 🔴)
> 3. Выполнить ВСЕ пункты и отметить completed
> 4. Команда завершена ТОЛЬКО когда все 🔴 пункты ✅
>
> Правила: `.aidd/CLAUDE.md` → "Выполнение команд /aidd-*"

# Команда: /research

> Запускает Исследователя для анализа кодовой базы и технологий.
> **Pipeline State v2**: Поддержка параллельных пайплайнов.

---

## Синтаксис

```bash
/research
```

---

## Описание

Команда `/aidd-research` выполняет анализ существующего кода (для FEATURE)
или анализ требований и технологий (для CREATE).

> **VERIFY BEFORE ACT**: Перед созданием файлов/директорий проверьте их
> существование (см. CLAUDE.md, раздел "Критические правила").

---

## Агент

**Исследователь** (`.claude/agents/researcher.md`)

---

## Порядок чтения файлов

> **Принцип**: Сначала контекст ЦП, потом инструкции фреймворка.
> **Подробнее**: [docs/initialization.md](../../docs/initialization.md)

### Фаза 1: Контекст целевого проекта

| # | Файл | Условие | Зачем |
|---|------|---------|-------|
| 1 | `./CLAUDE.md` | Если существует | Специфика проекта |
| 2 | `./.pipeline-state.json` | Обязательно | Режим, этап, ворота |
| 3 | `./ai-docs/docs/_analysis/*.md` | Обязательно | PRD для анализа |
| 4 | `./services/` | Для FEATURE | Существующий код |

### Фаза 2: Автомиграция и предусловия

> **Важно**: Перед выполнением команды проверить версию `.pipeline-state.json`
> и выполнить миграцию v1 → v2 если требуется (см. `knowledge/pipeline/automigration.md`).

| Ворота | Проверка (v2) |
|--------|---------------|
| `PRD_READY` | `active_pipelines[FID].gates.PRD_READY.passed == true` |

> **Примечание v2**: FID определяется по текущей git ветке.

### Фаза 3: Инструкции фреймворка

| # | Файл | Зачем |
|---|------|-------|
| 5 | `.aidd/CLAUDE.md` | Правила фреймворка |
| 6 | `.aidd/workflow.md` | Процесс и ворота |
| 7 | `.aidd/.claude/commands/research.md` | Этот файл |
| 8 | `.aidd/.claude/agents/researcher.md` | Инструкции роли |

### Фаза 4: База знаний

| # | Файл | Условие |
|---|------|---------|
| 9 | `.aidd/knowledge/architecture/*.md` | По необходимости |

---

## Режимы

| Режим | Поведение |
|-------|-----------|
| **CREATE** | Анализ требований из PRD, выбор технологий |
| **FEATURE** | Анализ существующего кода, выявление паттернов |

---

## Предусловия

| Ворота | Требование |
|--------|------------|
| `PRD_READY` | PRD документ должен существовать |

### Алгоритм проверки (v2)

```python
def check_research_preconditions() -> tuple[str, dict] | None:
    """
    Проверить предусловия для /research.

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

    # 3. Проверить PRD_READY
    if not pipeline["gates"].get("PRD_READY", {}).get("passed"):
        print(f"❌ Ворота PRD_READY не пройдены для {fid}")
        print("   → Сначала выполните /aidd-analyze")
        return None

    print(f"✓ Фича {fid}: {pipeline.get('title')}")
    return (fid, pipeline)
```

---

## Выходные артефакты

| Артефакт | Путь (v2) | Путь (v3) |
|----------|-----------|-----------|
| Research Report | `ai-docs/docs/research/{YYYY-MM-DD}_{FID}_{slug}-research.md` | `ai-docs/docs/_research/{YYYY-MM-DD}_{FID}_{slug}.md` |

> **Примечание (v2.4+)**:
> - **v2** (по умолчанию): Старая структура `research/`, имя с дублированием `{name}-research.md`
> - **v3** (после миграции): Новая структура `_research/`, имя без дублирования `{name}.md`
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
    folder = "_research"
    filename = f"{date}_{fid}_{slug}.md"  # Без дублирования
else:
    folder = "research"
    filename = f"{date}_{fid}_{slug}-research.md"  # С дублированием

artifact_path = f"{folder}/{filename}"
# v2: research/2024-12-23_F001_table-booking-research.md
# v3: _research/2024-12-23_F001_table-booking.md
```

### Обновление .pipeline-state.json

После создания отчёта обновить `active_pipelines[FID].artifacts` (v2):

**Пример для v2 (по умолчанию)**:
```json
{
  "naming_version": "v2",
  "active_pipelines": {
    "F001": {
      "branch": "feature/F001-table-booking",
      "name": "table-booking",
      "title": "Бронирование столиков",
      "stage": "RESEARCH",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "2024-12-23T10:00:00Z"},
        "RESEARCH_DONE": {"passed": false}
      },
      "artifacts": {
        "prd": "prd/2024-12-23_F001_table-booking-prd.md",
        "research": "research/2024-12-23_F001_table-booking-research.md"
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
        "research": "_research/2024-12-23_F001_table-booking.md"
      }
    }
  }
}
```

---

## Качественные ворота

### RESEARCH_DONE

| Критерий | Описание |
|----------|----------|
| Анализ кода | Существующий код изучен (для FEATURE) |
| Паттерны | Архитектурные паттерны выявлены |
| Ограничения | Технические ограничения определены |
| Рекомендации | Сформулированы рекомендации |
| Файл сохранён | Отчёт сохранён в правильной папке:<br>v2: `research/{YYYY-MM-DD}_{FID}_{slug}-research.md`<br>v3: `_research/{YYYY-MM-DD}_{FID}_{slug}.md` |

---

## Примеры использования

```bash
# После /idea
/research
```

---

## Чеклист ворот RESEARCH_DONE

> ⚠️ AI ОБЯЗАН создать TodoWrite с этими пунктами.

- [ ] 🔴 Research отчёт создан в правильной папке:
  - v2: `ai-docs/docs/research/{name}-research.md`
  - v3: `ai-docs/docs/_research/{name}.md`
- [ ] 🔴 Существующий код проанализирован
- [ ] 🔴 Зависимости определены
- [ ] 🔴 `.pipeline-state.json` обновлён (gate: RESEARCH_DONE, artifact path соответствует naming_version)
- [ ] 🟡 Риски идентифицированы
- [ ] 🟡 Технические ограничения описаны

---

## Следующий шаг

После прохождения ворот `RESEARCH_DONE`:

```bash
/plan          # для CREATE
/feature-plan  # для FEATURE
```
