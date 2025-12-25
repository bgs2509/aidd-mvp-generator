# Git интеграция для параллельных пайплайнов

> **Версия**: Pipeline State v2
> **Связанные файлы**:
> - `scripts/git_helpers.py` — утилиты командной строки
> - `knowledge/pipeline/state-v2.md` — спецификация v2
> - `knowledge/pipeline/automigration.md` — автомиграция

---

## Концепция

Каждая фича разрабатывается в отдельной git ветке. Это обеспечивает:

- **Изоляцию**: Изменения одной фичи не влияют на другие
- **Параллельность**: Несколько фич могут разрабатываться одновременно
- **Трассируемость**: История изменений привязана к конкретной фиче
- **Безопасность**: Merge через Pull Request с ревью

---

## Именование веток

### Формат

```
feature/{FID}-{slug}
```

### Примеры

| FID | Slug | Ветка |
|-----|------|-------|
| F001 | table-booking | `feature/F001-table-booking` |
| F042 | oauth-auth | `feature/F042-oauth-auth` |
| F043 | payments | `feature/F043-payments` |

### Правила для slug

- Только латинские буквы, цифры и дефисы
- Без пробелов и специальных символов
- Максимум 30 символов
- kebab-case (слова через дефис)

---

## Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ПАРАЛЛЕЛЬНЫЙ WORKFLOW                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  main                                                                   │
│    │                                                                    │
│    ├──┬── feature/F042-oauth ─────────────────────────▶ merge           │
│    │  │     ├── /aidd-idea      ← Создаёт ветку автоматически          │
│    │  │     ├── /aidd-research                                          │
│    │  │     ├── /aidd-plan                                              │
│    │  │     ├── /aidd-generate                                          │
│    │  │     ├── /aidd-review                                            │
│    │  │     ├── /aidd-test                                              │
│    │  │     ├── /aidd-validate                                          │
│    │  │     └── /aidd-deploy ──────────────▶ DEPLOYED                   │
│    │  │                                                                 │
│    │  └── feature/F043-payments ──────────────────────▶ merge           │
│    │        ├── /aidd-idea      (параллельно с F042!)                  │
│    │        ├── /aidd-research                                          │
│    │        ├── ...                                                     │
│    │        └── /aidd-deploy ──────────────▶ DEPLOYED                   │
│    │                                                                    │
│    ▼                                                                    │
│  main (с обеими фичами)                                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Автосоздание веток

### При выполнении `/aidd-idea`

Команда `/aidd-idea` автоматически создаёт ветку:

```python
# Из aidd-idea.md, функция create_feature():

# 5. Создать git ветку для фичи
branch = f"feature/{fid}-{slug}"
subprocess.run(["git", "checkout", "-b", branch], check=True)
print(f"✓ Создана ветка: {branch}")
```

### Результат

```bash
$ /aidd-idea "Добавить OAuth авторизацию"

✓ Создана ветка: feature/F042-oauth-auth
✓ Фича F042 добавлена в active_pipelines
✓ PRD создан: ai-docs/docs/prd/2025-12-25_F042_oauth-auth-prd.md
```

---

## Определение контекста фичи

### Алгоритм

```python
def get_current_feature_context(state: dict) -> tuple[str, dict] | None:
    """
    1. Получить текущую git ветку
    2. Найти FID в active_pipelines по branch
    3. Если не найдено — извлечь FID из имени ветки
    4. Если одна активная фича — использовать её
    5. Иначе — вернуть None (требуется явное указание)
    """
```

### Примеры

```bash
# Ветка feature/F042-oauth → автоматически F042
$ git checkout feature/F042-oauth
$ /aidd-generate
# → Генерирует код для F042

# Ветка main, одна активная фича → используется она
$ git checkout main
$ /aidd-research
# → ⚠️ Используется единственная активная фича: F042

# Ветка main, несколько фич → ошибка
$ git checkout main
$ /aidd-generate
# → ❌ Несколько активных фич. Переключитесь на ветку фичи:
#   git checkout feature/F042-oauth
#   git checkout feature/F043-payments
```

---

## Git-хелперы

### Скрипт `scripts/git_helpers.py`

```bash
# Показать текущий контекст
python3 scripts/git_helpers.py context

# Создать ветку
python3 scripts/git_helpers.py branch F042 oauth-auth

# Проверить конфликты между фичами
python3 scripts/git_helpers.py conflicts F042 F043

# Завершить фичу и подготовить к merge
python3 scripts/git_helpers.py merge F042
```

### Команда `context`

```
$ python3 scripts/git_helpers.py context

✓ Текущая фича: F042
  Название: OAuth авторизация
  Ветка: feature/F042-oauth-auth
  Этап: IMPLEMENT
  Ворота пройдены: PRD_READY, RESEARCH_DONE, PLAN_APPROVED
```

### Команда `conflicts`

```
$ python3 scripts/git_helpers.py conflicts F042 F043

┌─────────────────────────────────────────────────────────────────┐
│  ⚠️ ПРЕДУПРЕЖДЕНИЕ: Обнаружены потенциальные конфликты          │
├─────────────────────────────────────────────────────────────────┤
│  Фичи F042 и F043 редактируют одни файлы:                       │
│  • services/auth_api/domain/models.py                           │
│  • docker-compose.yml                                           │
│                                                                 │
│  Рекомендации:                                                  │
│  1. Завершить и смержить одну фичу перед продолжением другой    │
│  2. Разделить изменения на разные модули                        │
│  3. Координировать merge с командой                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Merge стратегия

### Завершение фичи

После прохождения всех ворот и `/aidd-deploy`:

```bash
# 1. Завершить фичу (перемещает в features_registry)
python3 scripts/git_helpers.py merge F042

# 2. Переключиться на main
git checkout main

# 3. Выполнить merge
git merge feature/F042-oauth-auth

# 4. Разрешить конфликты в .pipeline-state.json (если есть)
# AI автоматически объединяет состояния

# 5. Push
git push origin main
```

### Объединение `.pipeline-state.json`

При merge веток конфликты в `.pipeline-state.json` разрешаются автоматически:

```python
def merge_pipeline_states(main_state, feature_state, fid):
    """
    1. Перенести завершённую фичу в features_registry
    2. Удалить из active_pipelines
    3. Взять максимум next_feature_id
    4. Обновить timestamp
    """
```

### Пример объединения

**main/.pipeline-state.json:**
```json
{
  "active_pipelines": {
    "F043": { "stage": "RESEARCH" }
  },
  "next_feature_id": 44,
  "features_registry": {}
}
```

**feature/F042-oauth/.pipeline-state.json:**
```json
{
  "active_pipelines": {
    "F042": { "stage": "DEPLOYED", "gates": { "DEPLOYED": { "passed": true } } }
  },
  "next_feature_id": 43,
  "features_registry": {}
}
```

**После merge:**
```json
{
  "active_pipelines": {
    "F043": { "stage": "RESEARCH" }
  },
  "next_feature_id": 44,
  "features_registry": {
    "F042": {
      "status": "DEPLOYED",
      "deployed": "2025-12-25"
    }
  }
}
```

---

## Детекция конфликтов

### Автоматическая проверка

AI автоматически проверяет конфликты при:
- Запуске `/aidd-generate` (если есть другие активные фичи)
- Запуске `/aidd-deploy` (перед завершением)

### Ручная проверка

```bash
# Получить список изменённых файлов в ветке
git diff --name-only main...feature/F042-oauth

# Сравнить с другой фичей
python3 scripts/git_helpers.py conflicts F042 F043
```

### Рекомендации при конфликтах

1. **Приоритизировать фичи**: Завершить одну перед продолжением другой
2. **Разделить изменения**: Вынести общий код в отдельный модуль
3. **Координация**: При командной работе согласовать порядок merge
4. **Частые sync**: Регулярно синхронизировать feature-ветку с main

---

## Интеграция с командами

### Проверка контекста в каждой команде

Все команды `/aidd-*` проверяют контекст фичи:

```python
def check_preconditions():
    state = ensure_v2_state()

    # Определить FID по текущей git ветке
    fid, pipeline = get_current_feature_context(state)
    if not fid:
        print("❌ Не удалось определить контекст фичи")
        print("   → Переключитесь на ветку фичи: git checkout feature/FXXX-...")
        return None

    print(f"✓ Фича {fid}: {pipeline.get('title')}")
    return (fid, pipeline)
```

### Ворота изолированы по фичам

```python
# v2: Каждая фича имеет свои ворота
gates = state["active_pipelines"][fid]["gates"]

if not gates.get("PLAN_APPROVED", {}).get("passed"):
    print(f"❌ PLAN_APPROVED не пройдены для {fid}")
```

---

## Troubleshooting

### Ветка не определяется

```
❌ Не удалось определить контекст фичи
```

**Решение**: Переключитесь на ветку фичи:
```bash
git checkout feature/F042-oauth-auth
```

### Несколько активных фич

```
❌ Несколько активных фич. Укажите контекст.
```

**Решение**: Либо переключитесь на ветку, либо используйте явное указание:
```bash
git checkout feature/F042-oauth-auth
# или
/aidd-generate --feature=F042  # если поддерживается
```

### Ветка не существует

```
❌ Ветка feature/F042-oauth-auth уже существует
```

**Решение**: Используйте существующую ветку:
```bash
git checkout feature/F042-oauth-auth
```

---

## См. также

- `knowledge/pipeline/state-v2.md` — Спецификация Pipeline State v2
- `knowledge/pipeline/automigration.md` — Автомиграция v1 → v2
- `contributors/2025-12-25-aidd-enhancement-parallel-pipelines.md` — Проектный документ
