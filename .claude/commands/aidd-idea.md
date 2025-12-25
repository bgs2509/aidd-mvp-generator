---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**/*.md), Write(**/*.md), Bash(mkdir :*), Bash(git :*), Bash(python3 :*)
argument-hint: "[описание идеи проекта или фичи]"
description: Создать PRD документ из идеи пользователя
---

# Команда: /idea

> Запускает Аналитика для создания PRD документа из идеи.
> **Pipeline State v2**: Поддержка параллельных пайплайнов.

---

## Синтаксис

```bash
/idea "Описание идеи проекта или фичи"
```

---

## Описание

Команда `/aidd-idea` — точка входа в пайплайн AIDD-MVP. Преобразует текстовое
описание идеи в структурированный PRD (Product Requirements Document).

> **VERIFY BEFORE ACT**: Перед созданием файлов/директорий проверьте их
> существование (см. CLAUDE.md, раздел "Критические правила").

---

## Агент

**Аналитик** (`.claude/agents/analyst.md`)

---

## Порядок чтения файлов

> **Принцип**: Сначала контекст ЦП, потом инструкции фреймворка.
> **Подробнее**: [docs/initialization.md](../../docs/initialization.md)

### Фаза 1: Контекст целевого проекта

| # | Файл | Условие | Зачем |
|---|------|---------|-------|
| 1 | `./CLAUDE.md` | Если существует | Специфика проекта |
| 2 | `./.pipeline-state.json` | Если существует | Режим, этап, ворота |
| 3 | `./ai-docs/docs/prd/` | Если существует | Существующий PRD (для FEATURE) |

### Фаза 2: Предусловия и автомиграция

> **Важно**: Перед выполнением команды проверить версию `.pipeline-state.json`
> и выполнить миграцию v1 → v2 если требуется.

```python
# Автомиграция (выполнить в начале команды)
def ensure_v2_state():
    """
    Проверить и мигрировать .pipeline-state.json на v2.

    Подробнее: knowledge/pipeline/automigration.md
    """
    state_path = Path(".pipeline-state.json")

    if not state_path.exists():
        return None  # Будет создан новый

    state = json.loads(state_path.read_text())

    if state.get("version") != "2.0":
        print("⚠️  Обнаружен .pipeline-state.json v1.0")
        print("    Выполняется автоматическая миграция...")

        # Вызвать скрипт миграции
        result = subprocess.run(
            ["python3", ".aidd/scripts/migrate_pipeline_state.py"],
            capture_output=True, text=True
        )

        if result.returncode == 0:
            print("    ✓ Миграция завершена")
            state = json.loads(state_path.read_text())
        else:
            print(f"    ❌ Ошибка миграции: {result.stderr}")
            return None

    return state
```

Нет других предусловий — `/aidd-idea` это первый этап пайплайна.

### Фаза 3: Инструкции фреймворка

| # | Файл | Зачем |
|---|------|-------|
| 4 | `.aidd/CLAUDE.md` | Правила фреймворка |
| 5 | `.aidd/workflow.md` | Процесс и ворота |
| 6 | `.aidd/.claude/commands/aidd-idea.md` | Этот файл |
| 7 | `.aidd/.claude/agents/analyst.md` | Инструкции роли |

### Фаза 4: Шаблоны

| # | Файл | Условие |
|---|------|---------|
| 8 | `.aidd/templates/documents/prd-template.md` | Если PRD не существует |

---

## Bootstrap: Проверка и инициализация

> **Важно**: Перед созданием PRD команда `/aidd-idea` автоматически проверяет
> готовность окружения (Bootstrap Pipeline). При ошибках — предлагает `/aidd-init`.

### Алгоритм Bootstrap-проверок

```python
def auto_bootstrap() -> bool:
    """
    Автоматическая проверка и инициализация перед /aidd-idea.

    Returns:
        True если BOOTSTRAP_READY, False если нужен /init
    """
    # 1. Проверить, пройден ли уже BOOTSTRAP_READY
    if Path(".pipeline-state.json").exists():
        state = read_json(".pipeline-state.json")
        # v2: BOOTSTRAP_READY в global_gates
        # v1: BOOTSTRAP_READY в gates (для обратной совместимости)
        global_gates = state.get("global_gates", {})
        legacy_gates = state.get("gates", {})
        bootstrap_gate = global_gates.get("BOOTSTRAP_READY") or legacy_gates.get("BOOTSTRAP_READY")
        if bootstrap_gate and bootstrap_gate.get("passed"):
            return True  # Уже инициализирован

    # 2. Выполнить проверки окружения
    checks = {
        "git": run("git rev-parse --git-dir").ok,
        "framework": Path(".aidd/CLAUDE.md").exists(),
        "python": check_python_version() >= (3, 11),
        "docker": run("docker --version").ok,
    }

    # 3. Если все проверки пройдены — автоинициализация
    if all(checks.values()):
        # Создать структуру
        create_directory_structure()
        # Создать .pipeline-state.json
        create_pipeline_state()
        # Создать CLAUDE.md
        create_project_claude_md()
        return True

    # 4. Если есть ошибки — сообщить и предложить /init
    failed = [k for k, v in checks.items() if not v]
    print(f"❌ Проверки не пройдены: {failed}")
    print("→ Выполните /aidd-init для диагностики и исправления")
    return False
```

### Действия при первом запуске

> **VERIFY BEFORE ACT**: Перед созданием директорий и файлов проверяем их существование.

```bash
# 1. Определить режим
if [ -d "services" ] || [ -f "docker-compose.yml" ]; then
    MODE="FEATURE"
else
    MODE="CREATE"
fi

# 2. VERIFY: Проверить существующую структуру артефактов
if [ -d "ai-docs/docs" ]; then
    existing_count=$(ls -d ai-docs/docs/*/ 2>/dev/null | wc -l)
    echo "✓ Структура ai-docs/docs/ уже существует ($existing_count директорий)"
fi

# 3. ACT: Создать только недостающие директории
for dir in prd architecture plans reports research; do
    if [ ! -d "ai-docs/docs/$dir" ]; then
        mkdir -p "ai-docs/docs/$dir"
        echo "✓ Создана директория: ai-docs/docs/$dir"
    fi
done

# 4. Инициализировать состояние пайплайна (если не существует)
if [ ! -f ".pipeline-state.json" ]; then
    echo '{"project_name":"","mode":"'$MODE'","current_stage":1,"gates":{"BOOTSTRAP_READY":{"passed":true}}}' > .pipeline-state.json
    echo "✓ Создан .pipeline-state.json"
else
    echo "✓ .pipeline-state.json уже существует"
fi

# 5. Создать CLAUDE.md если не существует
if [ ! -f "CLAUDE.md" ]; then
    echo "# Project\n\nСм. .aidd/CLAUDE.md" > CLAUDE.md
    echo "✓ Создан CLAUDE.md"
else
    echo "✓ CLAUDE.md уже существует"
fi
```

### Предусловия

| Ворота | Проверка |
|--------|----------|
| `BOOTSTRAP_READY` | Авто-проверка при запуске `/aidd-idea` |

Если `BOOTSTRAP_READY` не пройден:
```
❌ Окружение не готово. Ошибки:
- framework: Фреймворк .aidd/ не найден
- docker: Docker не установлен

→ Выполните /aidd-init для детальной диагностики
```

---

## Режимы

| Режим | Условие | Поведение |
|-------|---------|-----------|
| **CREATE** | Нет `services/` или `docker-compose.yml` | Создаёт полный PRD для нового MVP |
| **FEATURE** | Есть существующий код | Создаёт FEATURE_PRD для новой функции |

---

## Предусловия

Нет — это первый этап пайплайна.

---

## Выходные артефакты (в целевом проекте)

| Артефакт | Путь |
|----------|------|
| PRD документ | `ai-docs/docs/prd/{YYYY-MM-DD}_{FID}_{slug}-prd.md` |
| Реестр фич | `ai-docs/docs/FEATURES.md` |
| Состояние | `.pipeline-state.json` |

---

## Генерация Feature ID (FID)

> **Спецификация**: [docs/artifact-naming.md](../../docs/artifact-naming.md)

### Алгоритм присвоения FID (v2: active_pipelines)

```python
def create_feature(state: dict, idea: str) -> dict:
    """
    Создаёт новую фичу с уникальным FID в active_pipelines.

    Args:
        state: Содержимое .pipeline-state.json (v2)
        idea: Описание идеи от пользователя

    Returns:
        dict: Данные новой фичи

    Изменения v2:
        - Фича создаётся в active_pipelines[fid] вместо current_feature
        - Ворота изолированы в active_pipelines[fid].gates
        - Создаётся git ветка feature/{fid}-{slug}
    """
    # 1. Сгенерировать FID
    next_id = state.get("next_feature_id", 1)
    fid = f"F{next_id:03d}"

    # 2. Создать slug из названия
    # "Система бронирования столиков" → "table-booking"
    slug = generate_slug(idea)  # kebab-case, ≤30 символов

    # 3. Получить текущую дату
    date = datetime.now().strftime("%Y-%m-%d")

    # 4. Сформировать имя файла и ветки
    filename = f"{date}_{fid}_{slug}-prd.md"
    branch = f"feature/{fid}-{slug}"

    # 5. Создать git ветку для фичи
    subprocess.run(["git", "checkout", "-b", branch], check=True)
    print(f"✓ Создана ветка: {branch}")

    # 6. Создать запись о фиче в active_pipelines (v2)
    state["active_pipelines"] = state.get("active_pipelines", {})
    state["active_pipelines"][fid] = {
        "branch": branch,
        "name": slug,
        "title": extract_title(idea),
        "stage": "IDEA",
        "created": date,
        "gates": {
            "PRD_READY": {"passed": False, "passed_at": None, "artifact": None},
            "RESEARCH_DONE": {"passed": False, "passed_at": None},
            "PLAN_APPROVED": {"passed": False, "passed_at": None, "artifact": None, "approved_by": None},
            "IMPLEMENT_OK": {"passed": False, "passed_at": None},
            "REVIEW_OK": {"passed": False, "passed_at": None, "artifact": None},
            "QA_PASSED": {"passed": False, "passed_at": None, "artifact": None, "coverage": None},
            "ALL_GATES_PASSED": {"passed": False, "passed_at": None, "artifact": None},
            "DEPLOYED": {"passed": False, "passed_at": None}
        },
        "artifacts": {}
    }

    # 7. Добавить в реестр фич
    state["features_registry"] = state.get("features_registry", {})
    state["features_registry"][fid] = {
        "name": slug,
        "title": extract_title(idea),
        "created": date,
        "status": "IN_PROGRESS",
        "services": []
    }

    # 8. Инкрементировать счётчик
    state["next_feature_id"] = next_id + 1

    # 9. Обновить updated_at
    state["updated_at"] = datetime.now().isoformat()

    return state["active_pipelines"][fid]
```

### Получение контекста текущей фичи

```python
def get_current_feature_context(state: dict) -> tuple[str, dict] | None:
    """
    Определить текущую фичу по git ветке.

    Returns:
        (fid, pipeline) или None если не в ветке фичи

    Алгоритм:
        1. Получить текущую git ветку
        2. Найти FID в active_pipelines по branch
        3. Если ветка не найдена, но есть только одна активная фича — использовать её
    """
    # Получить текущую ветку
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True
    )
    current_branch = result.stdout.strip()

    active_pipelines = state.get("active_pipelines", {})

    # Поиск по ветке
    for fid, pipeline in active_pipelines.items():
        if pipeline.get("branch") == current_branch:
            return (fid, pipeline)

    # Если только одна активная фича — использовать её
    if len(active_pipelines) == 1:
        fid = list(active_pipelines.keys())[0]
        return (fid, active_pipelines[fid])

    # Не в контексте фичи
    return None
```

### Формат имени файла

```
{YYYY-MM-DD}_{FID}_{slug}-{type}.md

Примеры:
- 2024-12-23_F001_table-booking-prd.md
- 2024-12-23_F002_email-notify-prd.md
```

### Обновление FEATURES.md

После создания PRD обновить реестр фич:

```markdown
# В ai-docs/docs/FEATURES.md добавить строку:

| F001 | Бронирование столиков | IN_PROGRESS | 2024-12-23 | — | [PRD](prd/2024-12-23_F001_table-booking-prd.md) |
```

### Обновление .pipeline-state.json (v2)

```json
{
  "version": "2.0",
  "global_gates": {
    "BOOTSTRAP_READY": { "passed": true, "passed_at": "2024-12-23T09:00:00Z" }
  },
  "active_pipelines": {
    "F001": {
      "branch": "feature/F001-table-booking",
      "name": "table-booking",
      "title": "Система бронирования столиков",
      "stage": "IDEA",
      "created": "2024-12-23",
      "gates": {
        "PRD_READY": {
          "passed": true,
          "passed_at": "2024-12-23T10:30:00Z",
          "artifact": "prd/2024-12-23_F001_table-booking-prd.md"
        },
        "RESEARCH_DONE": { "passed": false, "passed_at": null },
        "PLAN_APPROVED": { "passed": false, "passed_at": null, "artifact": null }
      },
      "artifacts": {
        "prd": "prd/2024-12-23_F001_table-booking-prd.md"
      }
    }
  },
  "features_registry": {
    "F001": {
      "name": "table-booking",
      "title": "Система бронирования столиков",
      "created": "2024-12-23",
      "status": "IN_PROGRESS",
      "services": []
    }
  },
  "next_feature_id": 2
}
```

> **Примечание v2**: Ворота теперь изолированы в `active_pipelines[FID].gates`,
> а не в общем `gates`. Это позволяет вести несколько фич параллельно.

---

## Качественные ворота

### PRD_READY

| Критерий | Описание |
|----------|----------|
| Все секции | PRD полностью заполнен |
| ID требований | Каждое требование имеет уникальный ID |
| Приоритеты | Must/Should/Could для всех требований |
| Критерии приёмки | Определены для всех FR |
| Открытые вопросы | Нет блокирующих вопросов |
| Состояние | `active_pipelines[FID].gates.PRD_READY` = true |

### Обновление ворот (v2)

```python
def pass_prd_ready_gate(state: dict, fid: str, artifact_path: str):
    """
    Отметить PRD_READY как пройденные для указанной фичи.

    v2: Ворота обновляются в active_pipelines[fid].gates
    """
    now = datetime.now().isoformat()

    state["active_pipelines"][fid]["gates"]["PRD_READY"] = {
        "passed": True,
        "passed_at": now,
        "artifact": artifact_path
    }

    state["active_pipelines"][fid]["stage"] = "RESEARCH"
    state["active_pipelines"][fid]["artifacts"]["prd"] = artifact_path

    state["updated_at"] = now
```

---

## Примеры использования

### Создание нового MVP

```bash
/idea "Создать сервис бронирования столиков в ресторанах.
Пользователи могут искать рестораны по кухне и локации,
смотреть свободные столики и бронировать на нужное время.
Рестораны получают уведомления о бронях в Telegram."
```

### Добавление фичи

```bash
/idea "Добавить систему email-уведомлений для подтверждения бронирования
и напоминания за 2 часа до визита."
```

### Краткое описание

```bash
/idea "Сервис учёта личных финансов с категоризацией расходов"
```

---

## Следующий шаг

После прохождения ворот `PRD_READY`:

```bash
/research
```
