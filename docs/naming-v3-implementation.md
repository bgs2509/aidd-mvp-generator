# Naming v3: Implementation Guide for Commands

> **Статус**: ✅ Phase 2.3 Complete (Migration mode active)
> **Дата**: 2026-01-19
> **Завершено**: 2026-01-19

## Обзор

Каждая команда должна поддерживать оба режима:
- **v2** (старая структура): `prd/`, `architecture/`, `plans/`, `reports/`
- **v3** (новая структура): `_analysis/`, `_research/`, `_plans/mvp/`, `_plans/features/`, `_validation/`

## Алгоритм для команд

### 1. Читать naming_version из .pipeline-state.json

```python
def get_artifact_folder(state: dict, artifact_type: str) -> str:
    """
    Определить путь к папке артефакта на основе naming_version.

    Args:
        state: Содержимое .pipeline-state.json
        artifact_type: Тип артефакта ("prd", "plan", "validation", etc.)

    Returns:
        Путь к папке (относительно ai-docs/docs/)
    """
    naming_version = state.get("naming_version", "v2")

    # Mapping для v2 → v3
    folder_map = {
        "v2": {
            "prd": "prd",
            "research": "research",
            "plan_mvp": "architecture",
            "plan_feature": "plans",
            "validation": "reports",
        },
        "v3": {
            "prd": "_analysis",
            "research": "_research",
            "plan_mvp": "_plans/mvp",
            "plan_feature": "_plans/features",
            "validation": "_validation",
        },
    }

    return folder_map[naming_version].get(artifact_type, artifact_type)
```

### 2. Использовать в командах

```python
# Пример для /aidd-analyze (создаёт PRD)
state = json.loads(Path(".pipeline-state.json").read_text())
folder = get_artifact_folder(state, "prd")
# folder = "prd" (v2) или "_analysis" (v3)

artifact_path = f"ai-docs/docs/{folder}/{date}_{FID}_{slug}-prd.md"  # v2
# ИЛИ
artifact_path = f"ai-docs/docs/{folder}/{date}_{FID}_{slug}.md"  # v3 (без дублирования)
```

## Команды для обновления

| # | Команда | Артефакт (v2) | Артефакт (v3) | Статус | Commit |
|---|---------|--------------|--------------|--------|--------|
| 1 | `/aidd-analyze` | `prd/{name}-prd.md` | `_analysis/{name}.md` | ✅ DONE | ea568ca |
| 2 | `/aidd-research` | `research/{name}-research.md` | `_research/{name}.md` | ✅ DONE | c0ec969 |
| 3 | `/aidd-plan` | `architecture/{name}-plan.md` | `_plans/mvp/{name}.md` | ✅ DONE | f9c810e |
| 4 | `/aidd-plan-feature` | `plans/{name}-plan.md` | `_plans/features/{name}.md` | ✅ DONE | 6e84bbc |
| 5 | `/aidd-code` | `services/` | `services/` | ✅ No changes | — |
| 6 | `/aidd-validate` | `reports/{name}-completion.md` | `_validation/{name}.md` | ✅ DONE | e56630d |

## Шаблон для обновления команды

### Шаг 1: Найти секцию создания артефакта

Искать строки типа:
```python
artifact_path = f"ai-docs/docs/_analysis/{date}_{FID}_{slug}-prd.md"
```

### Шаг 2: Заменить на динамический выбор

```python
# 1. Прочитать .pipeline-state.json
state = json.loads(Path(".pipeline-state.json").read_text())

# 2. Определить naming_version
naming_version = state.get("naming_version", "v2")

# 3. Выбрать папку
if naming_version == "v3":
    folder = "_analysis"
    filename = f"{date}_{FID}_{slug}.md"  # Без дублирования
else:
    folder = "prd"
    filename = f"{date}_{FID}_{slug}-prd.md"  # С дублированием

artifact_path = f"ai-docs/docs/{folder}/{filename}"
```

### Шаг 3: Обновить комментарии

```markdown
## Выходные артефакты (в целевом проекте)

| Режим | Артефакт | Путь |
|-------|----------|------|
| v2 | PRD | `prd/{YYYY-MM-DD}_{FID}_{slug}-prd.md` |
| v3 | Analysis | `_analysis/{YYYY-MM-DD}_{FID}_{slug}.md` |

> **Примечание**: Режим определяется из `.pipeline-state.json → naming_version`
```

## Тестирование

### Тест v2 (backward compatible)

```bash
# 1. Создать проект с v2
/aidd-init
# → .pipeline-state.json: naming_version = "v2"

# 2. Создать PRD
/aidd-analyze "test idea"
# → ai-docs/docs/_analysis/2026-01-19_F001_test-idea-prd.md ✓
```

### Тест v3 (после миграции)

```bash
# 1. Мигрировать проект
python .aidd/scripts/migrate-naming-v3.py

# 2. Проверить naming_version
cat .pipeline-state.json | grep naming_version
# → "naming_version": "v3"

# 3. Создать новую фичу
/aidd-analyze "new feature"
# → ai-docs/docs/_analysis/2026-01-19_F002_new-feature.md ✓
```

## Checklist для каждой команды

- [ ] Прочитать `.pipeline-state.json`
- [ ] Получить `naming_version`
- [ ] Определить папку артефакта через `get_artifact_folder()`
- [ ] Определить имя файла (с/без дублирования)
- [ ] Создать артефакт в правильной папке
- [ ] Обновить `artifacts` в pipeline state
- [ ] Обновить документацию команды

## Приоритет обновления

1. **Критические** (создают артефакты): `/aidd-analyze`, `/aidd-plan`, `/aidd-validate`
2. **Важные**: `/aidd-research`, `/aidd-plan-feature`
3. **Низкий**: `/aidd-code` (не меняется)

## См. также

- [План миграции](../../../.claude/plans/idempotent-drifting-wirth.md)
- [Migration script](../scripts/migrate-naming-v3.py)
- [Pipeline State v2](../knowledge/pipeline/state-v2.md)
