# Enhancement: Поддержка параллельных пайплайнов для разных фич

> **Дата**: 2025-12-25
> **Автор**: bgs
> **Контекст**: Необходимость одновременной разработки нескольких фич разными AI-агентами
> **Тип**: Enhancement (улучшение архитектуры)

---

## Проблема

Текущая архитектура фреймворка предполагает **последовательную разработку** одной фичи за раз. Это создаёт критические ограничения при командной работе или при необходимости вести параллельную разработку нескольких независимых фич.

### Точки конфликтов

#### 1. Единственный `current_feature` в `.pipeline-state.json`

```json
{
  "current_feature": {      // ← ТОЛЬКО ОДНА активная фича!
    "id": "F001",
    "stage": "IMPLEMENT"
  }
}
```

При параллельной работе:
- Оба AI-агента перезаписывают `current_feature`
- Состояние фичи теряется
- Невозможно отследить прогресс каждой фичи отдельно

#### 2. Гонка за `next_feature_id`

```python
# Агент A: читает next_feature_id = 42
# Агент B: читает next_feature_id = 42  (одновременно!)
# Оба создают F042 → КОНФЛИКТ имён артефактов
```

#### 3. Смешивание ворот (Gates)

| Сценарий | Проблема |
|----------|----------|
| Фича A проходит `PLAN_APPROVED` | Записывает `gates.PLAN_APPROVED.passed = true` |
| Фича B на этапе `/aidd-idea` | Видит `PLAN_APPROVED = true` — думает, что можно `/aidd-generate` |
| Результат | Генерация кода без утверждённого плана! |

#### 4. Перезапись артефактов

При совпадении FID (из-за гонки):
```
ai-docs/docs/prd/2024-12-25_F042_auth-prd.md      # Фича A
ai-docs/docs/prd/2024-12-25_F042_payments-prd.md  # Фича B — перезапишет!
```

---

## Предлагаемое решение

### Концепция: Multiple Active Pipelines

Заменить одиночный `current_feature` на множественные `active_pipelines`:

```json
{
  "active_pipelines": {
    "F042": {
      "branch": "feature/F042-auth",
      "name": "oauth-auth",
      "title": "OAuth авторизация",
      "stage": "IMPLEMENT",
      "created": "2025-12-25",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "..."},
        "RESEARCH_DONE": {"passed": true, "passed_at": "..."},
        "PLAN_APPROVED": {"passed": true, "passed_at": "...", "approved_by": "user"},
        "IMPLEMENT_OK": {"passed": false}
      },
      "artifacts": {
        "prd": "prd/2025-12-25_F042_oauth-auth-prd.md",
        "research": "research/2025-12-25_F042_oauth-auth-research.md",
        "plan": "plans/2025-12-25_F042_oauth-auth-plan.md"
      }
    },
    "F043": {
      "branch": "feature/F043-payments",
      "name": "payments-integration",
      "title": "Интеграция платежей",
      "stage": "RESEARCH",
      "created": "2025-12-25",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "..."},
        "RESEARCH_DONE": {"passed": false}
      },
      "artifacts": {
        "prd": "prd/2025-12-25_F043_payments-integration-prd.md"
      }
    }
  },
  "next_feature_id": 44,
  "features_registry": { ... }
}
```

---

## Новая архитектура

### Структура `.pipeline-state.json` v2

```json
{
  "$schema": "pipeline-state-schema",
  "version": "2.0",
  "project_name": "my-project",
  "mode": "FEATURE",

  "parallel_mode": true,

  "active_pipelines": {
    "F042": { ... },
    "F043": { ... }
  },

  "next_feature_id": 44,

  "features_registry": {
    "F001": { "status": "DEPLOYED", ... },
    "F041": { "status": "DEPLOYED", ... }
  },

  "global_gates": {
    "BOOTSTRAP_READY": {"passed": true, ...}
  }
}
```

### Разделение ворот

```
┌─────────────────────────────────────────────────────────────────┐
│  ВОРОТА: Глобальные vs Локальные                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ГЛОБАЛЬНЫЕ (один раз на проект):                               │
│  ├── BOOTSTRAP_READY                                            │
│  └── (проверка окружения)                                       │
│                                                                 │
│  ЛОКАЛЬНЫЕ (для каждой фичи отдельно):                          │
│  ├── PRD_READY                                                  │
│  ├── RESEARCH_DONE                                              │
│  ├── PLAN_APPROVED                                              │
│  ├── IMPLEMENT_OK                                               │
│  ├── REVIEW_OK                                                  │
│  ├── QA_PASSED                                                  │
│  ├── ALL_GATES_PASSED                                           │
│  └── DEPLOYED                                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Алгоритм работы с параллельными пайплайнами

### Инициализация новой фичи

```python
def start_feature(title: str, branch: str = None) -> str:
    """
    Начинает новую фичу в параллельном режиме.

    Args:
        title: Название фичи
        branch: Git ветка (опционально, создаётся автоматически)

    Returns:
        Feature ID (F042, F043, ...)
    """
    state = read_pipeline_state()

    # Атомарное получение следующего FID
    fid = f"F{state['next_feature_id']:03d}"
    state['next_feature_id'] += 1

    # Генерация slug из title
    slug = slugify(title)[:30]

    # Создание ветки если не указана
    if not branch:
        branch = f"feature/{fid}-{slug}"
        git_create_branch(branch)

    # Инициализация пайплайна
    state['active_pipelines'][fid] = {
        "branch": branch,
        "name": slug,
        "title": title,
        "stage": "IDEA",
        "created": datetime.now().isoformat()[:10],
        "gates": {},
        "artifacts": {}
    }

    write_pipeline_state(state)
    return fid
```

### Контекст выполнения команды

```python
def get_current_feature_context() -> str | None:
    """
    Определяет текущую фичу по git ветке или явному указанию.

    Returns:
        Feature ID или None если не в контексте фичи
    """
    state = read_pipeline_state()

    # 1. Проверить текущую git ветку
    current_branch = git_current_branch()

    for fid, pipeline in state['active_pipelines'].items():
        if pipeline['branch'] == current_branch:
            return fid

    # 2. Если только одна активная фича — использовать её
    if len(state['active_pipelines']) == 1:
        return list(state['active_pipelines'].keys())[0]

    # 3. Несколько фич — требуется явное указание
    return None
```

### Обновление ворот для конкретной фичи

```python
def pass_gate(fid: str, gate: str, artifact_path: str = None) -> None:
    """
    Отмечает прохождение ворот для конкретной фичи.

    Args:
        fid: Feature ID (F042)
        gate: Название ворот (PRD_READY, PLAN_APPROVED, ...)
        artifact_path: Путь к артефакту (опционально)
    """
    state = read_pipeline_state()

    if fid not in state['active_pipelines']:
        raise ValueError(f"Фича {fid} не найдена в активных пайплайнах")

    state['active_pipelines'][fid]['gates'][gate] = {
        "passed": True,
        "passed_at": datetime.now().isoformat(),
        "artifact": artifact_path
    }

    write_pipeline_state(state)
```

---

## Изменения в slash-командах

### Явное указание фичи

```bash
# Вариант 1: Автоопределение по git ветке
git checkout feature/F042-oauth
/aidd-generate
# → Генерирует код для F042

# Вариант 2: Явное указание
/aidd-generate --feature=F042

# Вариант 3: Интерактивный выбор (если несколько фич)
/aidd-generate
# → "Обнаружено 2 активные фичи. Выберите:
#    [1] F042 — OAuth авторизация (stage: IMPLEMENT)
#    [2] F043 — Интеграция платежей (stage: RESEARCH)"
```

### Модификация команд

| Команда | Изменения |
|---------|-----------|
| `/aidd-idea` | Создаёт запись в `active_pipelines`, возвращает FID |
| `/aidd-research` | Требует контекст фичи, обновляет `gates[fid]` |
| `/aidd-plan` | Требует контекст фичи |
| `/aidd-generate` | Требует контекст фичи |
| `/aidd-review` | Требует контекст фичи |
| `/aidd-test` | Требует контекст фичи |
| `/aidd-validate` | Требует контекст фичи |
| `/aidd-deploy` | Перемещает фичу в `features_registry` |

### Почему НЕ нужны новые команды

```
┌─────────────────────────────────────────────────────────────────┐
│  ПРИНЦИП: Использовать существующие инструменты                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ❌ /aidd-pipelines     →  ✅ git branch                        │
│  ❌ /aidd-switch F042   →  ✅ git checkout feature/F042-xxx     │
│  ❌ /aidd-status F042   →  ✅ AI читает .pipeline-state.json    │
│                                                                 │
│  Контекст фичи определяется АВТОМАТИЧЕСКИ по git ветке.         │
│  AI сообщает статус при запуске любой команды.                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Дополнительные команды создают избыточность и усложняют фреймворк.

---

## Интеграция с Git

### Рекомендуемый workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  ПАРАЛЛЕЛЬНЫЙ WORKFLOW                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  main                                                           │
│    │                                                            │
│    ├──┬── feature/F042-oauth ─────────────────────▶ merge       │
│    │  │     ├── /aidd-idea                                      │
│    │  │     ├── /aidd-research                                  │
│    │  │     ├── /aidd-plan                                      │
│    │  │     ├── /aidd-generate                                  │
│    │  │     ├── /aidd-review                                    │
│    │  │     ├── /aidd-test                                      │
│    │  │     ├── /aidd-validate                                  │
│    │  │     └── /aidd-deploy ──────────▶ DEPLOYED               │
│    │  │                                                         │
│    │  └── feature/F043-payments ──────────────────▶ merge       │
│    │        ├── /aidd-idea     (параллельно с F042!)           │
│    │        ├── /aidd-research                                  │
│    │        ├── ...                                             │
│    │        └── /aidd-deploy ──────────▶ DEPLOYED               │
│    │                                                            │
│    ▼                                                            │
│  main (с обеими фичами)                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Merge-стратегия для `.pipeline-state.json`

```python
def merge_pipeline_states(main_state: dict, feature_state: dict, fid: str) -> dict:
    """
    Объединяет состояния после merge feature ветки в main.

    Args:
        main_state: Состояние из main
        feature_state: Состояние из feature ветки
        fid: Feature ID завершённой фичи

    Returns:
        Объединённое состояние
    """
    result = main_state.copy()

    # 1. Перенести фичу в registry
    if fid in feature_state.get('active_pipelines', {}):
        pipeline = feature_state['active_pipelines'][fid]
        result['features_registry'][fid] = {
            "name": pipeline['name'],
            "title": pipeline['title'],
            "status": "DEPLOYED",
            "created": pipeline['created'],
            "deployed": datetime.now().isoformat()[:10],
            "artifacts": pipeline['artifacts']
        }

    # 2. Удалить из active_pipelines
    if fid in result.get('active_pipelines', {}):
        del result['active_pipelines'][fid]

    # 3. Синхронизировать next_feature_id (взять максимум)
    result['next_feature_id'] = max(
        main_state.get('next_feature_id', 1),
        feature_state.get('next_feature_id', 1)
    )

    return result
```

---

## Блокировки и конфликты

### Обнаружение конфликтов файлов

```python
def check_file_conflicts(fid_a: str, fid_b: str) -> List[str]:
    """
    Проверяет, редактируют ли две фичи одни и те же файлы.

    Returns:
        Список конфликтующих файлов
    """
    state = read_pipeline_state()

    files_a = get_modified_files(state['active_pipelines'][fid_a]['branch'])
    files_b = get_modified_files(state['active_pipelines'][fid_b]['branch'])

    conflicts = set(files_a) & set(files_b)

    return list(conflicts)
```

### Предупреждение при конфликтах

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️ ПРЕДУПРЕЖДЕНИЕ: Обнаружены потенциальные конфликты          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Фичи F042 и F043 редактируют одни файлы:                       │
│  • services/auth_api/domain/models.py                           │
│  • docker-compose.yml                                           │
│                                                                 │
│  Рекомендации:                                                  │
│  1. Завершить и смержить одну фичу перед продолжением другой    │
│  2. Разделить изменения на разные модули                        │
│  3. Координировать merge с командой                             │
│                                                                 │
│  Продолжить? [y/N]                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Backward Compatibility

### Миграция v1 → v2

```python
def migrate_pipeline_state_v1_to_v2(state_v1: dict) -> dict:
    """
    Мигрирует .pipeline-state.json с v1 на v2.
    """
    state_v2 = {
        "$schema": "pipeline-state-schema",
        "version": "2.0",
        "project_name": state_v1.get("project_name"),
        "mode": state_v1.get("mode"),
        "parallel_mode": False,  # По умолчанию выключен
        "active_pipelines": {},
        "next_feature_id": state_v1.get("next_feature_id", 1),
        "features_registry": state_v1.get("features_registry", {}),
        "global_gates": {
            "BOOTSTRAP_READY": state_v1.get("gates", {}).get("BOOTSTRAP_READY", {})
        }
    }

    # Перенести current_feature в active_pipelines
    if current := state_v1.get("current_feature"):
        fid = current.get("id", f"F{state_v2['next_feature_id']:03d}")
        state_v2["active_pipelines"][fid] = {
            "branch": f"feature/{fid}-{current.get('name', 'unnamed')}",
            "name": current.get("name"),
            "title": current.get("title"),
            "stage": current.get("stage"),
            "created": current.get("created"),
            "gates": {
                k: v for k, v in state_v1.get("gates", {}).items()
                if k != "BOOTSTRAP_READY"
            },
            "artifacts": current.get("artifacts", {})
        }

    return state_v2
```

### Автоматическая миграция

При запуске любой команды:
```python
def ensure_state_v2():
    """Автоматически мигрирует state если нужно."""
    state = read_pipeline_state()

    if state.get("version") != "2.0":
        state_v2 = migrate_pipeline_state_v1_to_v2(state)
        write_pipeline_state(state_v2)
        print("✓ .pipeline-state.json мигрирован на версию 2.0")
```

---

## Затрагиваемые файлы

| Файл | Изменения |
|------|-----------|
| `templates/documents/pipeline-state-template.json` | Новая схема v2 |
| `.claude/commands/aidd-idea.md` | Создание в `active_pipelines` |
| `.claude/commands/aidd-*.md` | Контекст фичи по git branch, работа с `gates[fid]` |
| `CLAUDE.md` | Документация параллельного режима |
| `workflow.md` | Описание параллельного workflow |
| `docs/artifact-naming.md` | Атомарность FID |
| `knowledge/parallel-pipelines.md` | База знаний |

---

## План реализации

### Фаза 1: Схема и миграция ✅ ЗАВЕРШЕНА

- [x] Обновить `pipeline-state-template.json` на v2
  - Файл: `templates/documents/pipeline-state-template.json`
- [x] Написать скрипт миграции v1 → v2
  - Файл: `scripts/migrate_pipeline_state.py`
- [x] Добавить автоматическую миграцию при запуске
  - Файл: `knowledge/pipeline/automigration.md`
  - Файл: `knowledge/pipeline/state-v2.md`

### Фаза 2: Модификация команд
- [ ] Модифицировать `/aidd-idea` для создания в `active_pipelines`
- [ ] Добавить определение контекста фичи по git branch
- [ ] Обновить все команды для работы с `gates[fid]`

### Фаза 3: Интеграция с Git
- [ ] Автосоздание веток при `/aidd-idea`
- [ ] Merge-хелперы для `.pipeline-state.json`
- [ ] Детекция конфликтов файлов

### Фаза 4: Документация
- [ ] Обновить CLAUDE.md
- [ ] Обновить workflow.md
- [x] Создать knowledge/parallel-pipelines.md → `knowledge/pipeline/state-v2.md`

---

## Приоритет

**Средний** — полезно для командной работы, но текущий sequential workflow работает.

---

## Альтернативные решения

### Вариант A: Отдельные state-файлы (проще)

```
.pipeline-state.json           # Главный (features_registry, next_feature_id)
.pipeline-state.F042.json      # Фича A
.pipeline-state.F043.json      # Фича B
```

**Плюсы**: Проще реализовать, нет конфликтов
**Минусы**: Много файлов, сложнее отслеживать

### Вариант B: Git-based state (сложнее)

Хранить состояние каждой фичи только в её ветке, синхронизировать при merge.

**Плюсы**: Максимальная изоляция
**Минусы**: Сложная логика merge

### Рекомендация

Начать с **Варианта A** (отдельные файлы) как MVP, затем перейти к полноценному решению с `active_pipelines`.

---

## Статус

| Этап | Статус |
|------|--------|
| Проектирование | ✅ Завершено (этот документ) |
| Обсуждение | ⏳ Ожидает |
| Реализация | ⏳ Ожидает |
| Тестирование | ⏳ Ожидает |
| Документация | ⏳ Ожидает |

---

*Создано: 2025-12-25*
*Автор: bgs (с помощью Claude Code)*
