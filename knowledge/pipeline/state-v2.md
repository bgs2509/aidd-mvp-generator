# Pipeline State v2: Параллельные пайплайны

> **Версия**: 2.0
> **Дата**: 2025-12-25

---

## Обзор

Pipeline State v2 поддерживает **параллельную разработку нескольких фич** через изоляцию состояния каждой фичи в отдельном пайплайне.

---

## Структура `.pipeline-state.json` v2

```json
{
  "$schema": "pipeline-state-schema",
  "version": "2.0",
  "project_name": "my-project",
  "mode": "FEATURE",
  "parallel_mode": true,

  "global_gates": {
    "BOOTSTRAP_READY": { "passed": true, ... }
  },

  "active_pipelines": {
    "F042": {
      "branch": "feature/F042-oauth",
      "name": "oauth-auth",
      "title": "OAuth авторизация",
      "stage": "IMPLEMENT",
      "created": "2025-12-25",
      "gates": { ... },
      "artifacts": { ... }
    },
    "F043": { ... }
  },

  "features_registry": {
    "F001": { "status": "DEPLOYED", ... }
  },

  "next_feature_id": 44,
  "services": []
}
```

---

## Ключевые изменения v1 → v2

| Аспект | v1 | v2 |
|--------|----|----|
| Активные фичи | 1 (`current_feature`) | N (`active_pipelines`) |
| Ворота | Общие (`gates`) | Изолированные (`active_pipelines[FID].gates`) |
| Глобальные ворота | Смешаны с локальными | Отдельно (`global_gates`) |
| Контекст фичи | Неявный | По git ветке |

---

## Автомиграция

### При запуске любой slash-команды

AI-агент ОБЯЗАН проверить версию `.pipeline-state.json`:

```python
# Псевдокод проверки
state = read_json(".pipeline-state.json")

if state.get("version") != "2.0":
    # Выполнить миграцию
    run("python .aidd/scripts/migrate_pipeline_state.py")
    # Или сообщить пользователю
    print("⚠️ Требуется миграция. Выполните:")
    print("   python .aidd/scripts/migrate_pipeline_state.py")
```

### Команда миграции

```bash
# Показать план миграции
python .aidd/scripts/migrate_pipeline_state.py --dry-run

# Выполнить миграцию
python .aidd/scripts/migrate_pipeline_state.py
```

---

## Определение контекста фичи

### Алгоритм

1. **Проверить текущую git ветку**
   ```bash
   git rev-parse --abbrev-ref HEAD
   # → feature/F042-oauth
   ```

2. **Найти FID в active_pipelines по branch**
   ```python
   for fid, pipeline in state["active_pipelines"].items():
       if pipeline["branch"] == current_branch:
           return fid  # → "F042"
   ```

3. **Если только одна активная фича** — использовать её

4. **Если несколько фич и ветка не совпадает** — запросить у пользователя

### Пример для AI-агента

```markdown
При выполнении команды:

1. Прочитать .pipeline-state.json
2. Проверить версию (должна быть "2.0")
3. Получить текущую git ветку: `git rev-parse --abbrev-ref HEAD`
4. Найти FID по ветке в active_pipelines
5. Использовать active_pipelines[FID].gates для проверки ворот
6. Обновлять active_pipelines[FID] при прохождении этапов
```

---

## Работа с воротами

### Глобальные ворота

Проверяются один раз на проект:
- `BOOTSTRAP_READY` — окружение настроено

### Локальные ворота (для каждой фичи)

```
PRD_READY → RESEARCH_DONE → PLAN_APPROVED → IMPLEMENT_OK →
→ REVIEW_OK → QA_PASSED → ALL_GATES_PASSED → DEPLOYED
```

### Проверка ворот

```python
def check_gate(fid: str, gate: str) -> bool:
    state = read_json(".pipeline-state.json")

    # Глобальные ворота
    if gate == "BOOTSTRAP_READY":
        return state["global_gates"]["BOOTSTRAP_READY"]["passed"]

    # Локальные ворота
    pipeline = state["active_pipelines"].get(fid)
    if not pipeline:
        return False

    return pipeline["gates"].get(gate, {}).get("passed", False)
```

### Обновление ворот

```python
def pass_gate(fid: str, gate: str, artifact: str = None) -> None:
    state = read_json(".pipeline-state.json")

    state["active_pipelines"][fid]["gates"][gate] = {
        "passed": True,
        "passed_at": datetime.now().isoformat(),
        "artifact": artifact
    }

    write_json(".pipeline-state.json", state)
```

---

## Жизненный цикл фичи

### 1. Создание (`/aidd-idea`)

```python
def create_feature(title: str) -> str:
    state = read_json(".pipeline-state.json")

    fid = f"F{state['next_feature_id']:03d}"
    state['next_feature_id'] += 1

    slug = slugify(title)[:30]
    branch = f"feature/{fid}-{slug}"

    # Создать git ветку
    run(f"git checkout -b {branch}")

    state["active_pipelines"][fid] = {
        "branch": branch,
        "name": slug,
        "title": title,
        "stage": "IDEA",
        "created": today(),
        "gates": create_empty_gates(),
        "artifacts": {}
    }

    write_json(".pipeline-state.json", state)
    return fid
```

### 2. Прогресс по этапам

При каждом успешном этапе:
1. Обновить `active_pipelines[FID].stage`
2. Отметить ворота как пройденные
3. Записать путь к артефакту

### 3. Завершение (`/aidd-deploy`)

```python
def complete_feature(fid: str) -> None:
    state = read_json(".pipeline-state.json")

    pipeline = state["active_pipelines"].pop(fid)

    state["features_registry"][fid] = {
        "name": pipeline["name"],
        "title": pipeline["title"],
        "status": "DEPLOYED",
        "created": pipeline["created"],
        "deployed": today(),
        "artifacts": pipeline["artifacts"],
        "services": pipeline.get("services", [])
    }

    write_json(".pipeline-state.json", state)
```

---

## Чек-лист для AI-агента

При выполнении любой команды:

- [ ] Проверить существование `.pipeline-state.json`
- [ ] Проверить версию (мигрировать если v1)
- [ ] Определить контекст фичи по git ветке
- [ ] Проверить предусловия (ворота) для команды
- [ ] Выполнить команду
- [ ] Обновить ворота и артефакты в `active_pipelines[FID]`
- [ ] Обновить `updated_at`

---

## Совместимость

### parallel_mode

- `false` (по умолчанию) — последовательный режим, как в v1
- `true` — параллельный режим

При `parallel_mode: false`:
- Допускается только один активный пайплайн
- При попытке создать второй — предупреждение

### Deprecated поля

Эти поля сохраняются для совместимости, но НЕ используются:
- `current_feature` — заменён на `active_pipelines`
- `current_stage` — заменён на `active_pipelines[FID].stage`
- `gates` (корневой) — заменён на `global_gates` + `active_pipelines[FID].gates`
- `artifacts` (корневой) — заменён на `active_pipelines[FID].artifacts`
