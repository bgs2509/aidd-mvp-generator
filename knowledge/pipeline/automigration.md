# Автомиграция Pipeline State

> **Для AI-агентов**: Этот документ содержит инструкции по автоматической миграции `.pipeline-state.json`.

---

## Когда выполнять

**ПРИ ЗАПУСКЕ ЛЮБОЙ SLASH-КОМАНДЫ** (кроме `/aidd-init`):

1. Прочитать `.pipeline-state.json`
2. Проверить поле `version`
3. Если `version != "2.0"` — выполнить миграцию

---

## Алгоритм проверки

```python
import json
from pathlib import Path

def check_and_migrate() -> dict | None:
    """
    Проверить версию state и мигрировать если нужно.

    Returns:
        Состояние в формате v2 или None если файл не найден
    """
    state_path = Path(".pipeline-state.json")

    if not state_path.exists():
        return None

    state = json.loads(state_path.read_text())

    if state.get("version") != "2.0":
        print("⚠️  Обнаружен .pipeline-state.json v1.0")
        print("    Выполняется автоматическая миграция...")

        # Вызвать скрипт миграции
        import subprocess
        result = subprocess.run(
            ["python", ".aidd/scripts/migrate_pipeline_state.py"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("    ✓ Миграция завершена")
            # Перечитать обновлённый файл
            state = json.loads(state_path.read_text())
        else:
            print("    ❌ Ошибка миграции:")
            print(result.stderr)
            return None

    return state
```

---

## Для AI-агента (текстовая инструкция)

### Шаг 1: Проверка версии

```bash
# Прочитать файл и проверить версию
cat .pipeline-state.json | grep '"version"'
```

Ожидаемый результат: `"version": "2.0"`

### Шаг 2: Миграция (если версия != 2.0)

```bash
# Показать план миграции
python .aidd/scripts/migrate_pipeline_state.py --dry-run

# Выполнить миграцию
python .aidd/scripts/migrate_pipeline_state.py
```

### Шаг 3: Продолжить выполнение команды

После успешной миграции продолжить выполнение запрошенной команды.

---

## Что делает миграция

1. **Создаёт резервную копию**: `.pipeline-state.json.v1.backup`

2. **Переносит глобальные ворота**:
   ```
   gates.BOOTSTRAP_READY → global_gates.BOOTSTRAP_READY
   ```

3. **Создаёт active_pipelines** (если есть активная работа):
   - Переносит `current_feature` в `active_pipelines[FID]`
   - Переносит локальные ворота в `active_pipelines[FID].gates`
   - Определяет ветку по текущей git branch

4. **Сохраняет features_registry** без изменений

5. **Устанавливает version**: `"2.0"`

---

## Пример вывода миграции

```
Обнаружена версия: 1.0
Требуется миграция на v2.0

============================================================
ПЛАН МИГРАЦИИ
============================================================

Структурные изменения:
  • gates → global_gates (только BOOTSTRAP_READY)
  • Локальные ворота → active_pipelines[FID].gates
  • current_feature → active_pipelines
  • Добавлено: parallel_mode, version 2.0

Активные пайплайны после миграции:
  F001: OAuth авторизация
       Ветка: feature/F001-oauth
       Этап: IMPLEMENT
       Ворота: PRD_READY, RESEARCH_DONE, PLAN_APPROVED

next_feature_id: 2

✓ Создана резервная копия: .pipeline-state.json.v1.backup
✓ Сохранено: .pipeline-state.json

============================================================
МИГРАЦИЯ ЗАВЕРШЕНА
============================================================
```

---

## Обработка ошибок

### Файл не найден

```
Файл .pipeline-state.json не найден
```

**Действие**: Продолжить выполнение команды (команда сама создаст файл если нужно).

### Невалидный JSON

```
Ошибка чтения JSON: ...
```

**Действие**: Сообщить пользователю об ошибке, предложить проверить файл вручную.

### Уже v2.0

```
✓ Файл уже в формате v2.0, миграция не требуется
```

**Действие**: Продолжить выполнение команды.
