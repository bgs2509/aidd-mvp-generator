---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**), Write(**), Bash(make :*), Bash(docker :*), Bash(pytest :*), Bash(git :*), Bash(python3 :*)
description: Генерация кода на основе утверждённого плана
---

# Команда: /generate

> Запускает Реализатора для генерации кода.
> **Pipeline State v2**: Поддержка параллельных пайплайнов.

---

## Синтаксис

```bash
/generate
```

---

## Описание

Команда `/aidd-generate` создаёт код на основе утверждённого плана:
- Инфраструктуру (Docker, CI/CD)
- Data Services
- Business Services
- Тесты

> **VERIFY BEFORE ACT**: Перед созданием файлов/директорий проверьте их
> существование (см. CLAUDE.md, раздел "Критические правила").

---

## Агент

**Реализатор** (`.claude/agents/implementer.md`)

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
| 4 | `./ai-docs/docs/architecture/*.md` | Для CREATE | Архитектурный план |
| 5 | `./ai-docs/docs/plans/*.md` | Для FEATURE | План фичи |
| 6 | `./services/` | Для FEATURE | Существующий код |

### Фаза 2: Автомиграция и предусловия

> **Важно**: Перед выполнением команды проверить версию `.pipeline-state.json`
> и выполнить миграцию v1 → v2 если требуется (см. `knowledge/pipeline/automigration.md`).

| Ворота | Проверка (v2) |
|--------|---------------|
| `PLAN_APPROVED` | `active_pipelines[FID].gates.PLAN_APPROVED.passed == true` |
| `approved_by` | `active_pipelines[FID].gates.PLAN_APPROVED.approved_by != null` |

> **Примечание v2**: FID определяется по текущей git ветке (см. алгоритм ниже).

### Фаза 3: Инструкции фреймворка

| # | Файл | Зачем |
|---|------|-------|
| 7 | `.aidd/CLAUDE.md` | Правила фреймворка |
| 8 | `.aidd/workflow.md` | Процесс и ворота |
| 9 | `.aidd/conventions.md` | Соглашения о коде |
| 10 | `.aidd/.claude/commands/generate.md` | Этот файл |
| 11 | `.aidd/.claude/agents/implementer.md` | Инструкции роли |

### Фаза 4: Шаблоны

| # | Файл | Условие |
|---|------|---------|
| 12 | `.aidd/templates/services/*.md` | Шаблоны сервисов |
| 13 | `.aidd/templates/infrastructure/*.md` | Инфраструктура |

---

## Режимы

| Режим | Поведение |
|-------|-----------|
| **CREATE** | Создаёт полную структуру проекта |
| **FEATURE** | Добавляет код в существующий проект |

---

## Предусловия

| Ворота | Требование |
|--------|------------|
| `PLAN_APPROVED` | План утверждён пользователем |

### Алгоритм проверки (v2)

```python
def check_generate_preconditions() -> tuple[str, dict] | None:
    """
    Проверить предусловия для /generate.

    Returns:
        (fid, pipeline) или None при ошибке

    Алгоритм v2:
        1. Проверить .pipeline-state.json и мигрировать если нужно
        2. Определить FID по git ветке
        3. Проверить active_pipelines[fid].gates.PLAN_APPROVED
    """
    # 1. Проверить существование и версию
    state_path = Path(".pipeline-state.json")
    if not state_path.exists():
        print("❌ Пайплайн не инициализирован")
        print("   → Сначала выполните /aidd-idea")
        return None

    state = json.loads(state_path.read_text())

    # 2. Автомиграция v1 → v2
    if state.get("version") != "2.0":
        print("⚠️  Обнаружен v1, выполняется миграция...")
        subprocess.run(["python3", ".aidd/scripts/migrate_pipeline_state.py"])
        state = json.loads(state_path.read_text())

    # 3. Определить FID по текущей git ветке
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True
    )
    current_branch = result.stdout.strip()

    active_pipelines = state.get("active_pipelines", {})
    fid, pipeline = None, None

    # Поиск по ветке
    for f, p in active_pipelines.items():
        if p.get("branch") == current_branch:
            fid, pipeline = f, p
            break

    # Если одна фича — использовать её
    if not fid and len(active_pipelines) == 1:
        fid = list(active_pipelines.keys())[0]
        pipeline = active_pipelines[fid]

    if not fid:
        print("❌ Не удалось определить контекст фичи")
        print(f"   Текущая ветка: {current_branch}")
        print("   → Переключитесь на ветку фичи: git checkout feature/F00X-...")
        return None

    # 4. Проверить PLAN_APPROVED
    gates = pipeline.get("gates", {})
    plan_gate = gates.get("PLAN_APPROVED", {})

    if not plan_gate.get("passed"):
        print(f"❌ Ворота PLAN_APPROVED не пройдены для {fid}")
        print("   → Сначала выполните /aidd-plan или /aidd-feature-plan")
        return None

    if not plan_gate.get("approved_by"):
        print(f"⚠️  План {fid} требует явного утверждения пользователем")
        return None

    print(f"✓ Фича {fid}: {pipeline.get('title')}")
    print(f"  Ветка: {pipeline.get('branch')}")
    return (fid, pipeline)
```

---

## Выходные артефакты (в целевом проекте)

| Артефакт | Путь |
|----------|------|
| Сервисы | `services/{name}_api/`, `services/{name}_data/` |
| Инфраструктура | `docker-compose.yml`, `Makefile` |
| CI/CD | `.github/workflows/` |
| Тесты | `services/*/tests/` |
| Состояние | `.pipeline-state.json` (обновляется) |

### Обновление .pipeline-state.json (v2)

После генерации кода обновить `active_pipelines[fid]`:

```python
def update_after_generate(state: dict, fid: str, services: list[str]):
    """
    Обновить состояние после успешной генерации кода.

    v2: Обновляем active_pipelines[fid], а не current_feature
    """
    now = datetime.now().isoformat()

    pipeline = state["active_pipelines"][fid]

    # Обновить ворота IMPLEMENT_OK
    pipeline["gates"]["IMPLEMENT_OK"] = {
        "passed": True,
        "passed_at": now
    }

    # Обновить этап
    pipeline["stage"] = "REVIEW"

    # Добавить сервисы
    pipeline["services"] = services

    state["updated_at"] = now
```

```json
{
  "version": "2.0",
  "active_pipelines": {
    "F001": {
      "branch": "feature/F001-table-booking",
      "name": "table-booking",
      "stage": "REVIEW",
      "gates": {
        "PRD_READY": { "passed": true, "passed_at": "..." },
        "RESEARCH_DONE": { "passed": true, "passed_at": "..." },
        "PLAN_APPROVED": { "passed": true, "passed_at": "...", "approved_by": "user" },
        "IMPLEMENT_OK": { "passed": true, "passed_at": "2024-12-23T12:00:00Z" }
      },
      "artifacts": {
        "prd": "prd/2024-12-23_F001_table-booking-prd.md",
        "research": "research/2024-12-23_F001_table-booking-research.md",
        "plan": "architecture/2024-12-23_F001_table-booking-plan.md"
      },
      "services": ["booking_api", "booking_data"]
    }
  }
}
```

> **Примечание**: Сервисы и инфраструктурные файлы не следуют
> паттерну FID-именования, т.к. это код, а не документы.

---

## Качественные ворота

### IMPLEMENT_OK

| Критерий | Описание |
|----------|----------|
| Код | Написан согласно плану |
| Структура | DDD/Hexagonal соблюдена |
| Типы | Type hints везде |
| Документация | Docstrings на русском |
| Тесты | Unit-тесты проходят |

---

## Порядок генерации

```
1. Инфраструктура (docker-compose, Makefile, CI/CD)
2. Data Service (модели, репозитории, API)
3. Business API (сервисы, API, HTTP клиенты)
4. Background Worker (если нужен)
5. Telegram Bot (если нужен)
6. Тесты
```

---

## Примеры использования

```bash
# После утверждения плана
/generate
```

---

## Следующий шаг

После прохождения ворот `IMPLEMENT_OK`:

```bash
/review
```
