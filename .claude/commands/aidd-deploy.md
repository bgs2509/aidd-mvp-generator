---
allowed-tools: Read(*), Glob(*), Grep(*), Bash(make :*), Bash(docker :*), Bash(curl :*), Bash(git :*), Bash(python3 :*)
description: Сборка и запуск Docker-контейнеров
---

# Команда: /deploy

> Запускает Валидатора для деплоя приложения.
> **Pipeline State v2**: Поддержка параллельных пайплайнов.

---

## Синтаксис

```bash
/deploy
```

---

## Описание

Команда `/aidd-deploy` выполняет:
- Сборку Docker-контейнеров
- Запуск приложения
- Проверку health-check
- Верификацию работоспособности

> **VERIFY BEFORE ACT**: Перед созданием файлов/директорий проверьте их
> существование (см. CLAUDE.md, раздел "Критические правила").

---

## Агент

**Валидатор** (`.claude/agents/validator.md`)

---

## Порядок чтения файлов

> **Принцип**: Сначала контекст ЦП, потом инструкции фреймворка.
> **Подробнее**: [docs/initialization.md](../../docs/initialization.md)

### Фаза 1: Контекст целевого проекта

| # | Файл | Условие | Зачем |
|---|------|---------|-------|
| 1 | `./CLAUDE.md` | Если существует | Специфика проекта |
| 2 | `./.pipeline-state.json` | Обязательно | ВСЕ ворота |
| 3 | `./docker-compose.yml` | Обязательно | Инфраструктура |
| 4 | `./Makefile` | Обязательно | Команды сборки |

### Фаза 2: Автомиграция и предусловия

> **Важно**: Перед выполнением команды проверить версию `.pipeline-state.json`
> и выполнить миграцию v1 → v2 если требуется (см. `knowledge/pipeline/automigration.md`).

| Ворота | Проверка (v2) |
|--------|---------------|
| `ALL_GATES_PASSED` | `active_pipelines[FID].gates.ALL_GATES_PASSED.passed == true` |
| Все предыдущие | `active_pipelines[FID].gates.*` — PRD_READY, RESEARCH_DONE, PLAN_APPROVED, IMPLEMENT_OK, REVIEW_OK, QA_PASSED |

> **Примечание v2**: FID определяется по текущей git ветке.

### Фаза 3: Инструкции фреймворка

| # | Файл | Зачем |
|---|------|-------|
| 5 | `.aidd/CLAUDE.md` | Правила фреймворка |
| 6 | `.aidd/workflow.md` | Процесс и ворота |
| 7 | `.aidd/.claude/commands/deploy.md` | Этот файл |
| 8 | `.aidd/.claude/agents/validator.md` | Инструкции роли |

### Фаза 4: База знаний

| # | Файл | Условие |
|---|------|---------|
| 9 | `.aidd/knowledge/infrastructure/docker.md` | Docker практики |

---

## Предусловия

| Ворота | Требование |
|--------|------------|
| `ALL_GATES_PASSED` | Все предыдущие ворота пройдены |

### Алгоритм проверки (v2)

```python
def check_deploy_preconditions() -> tuple[str, dict] | None:
    """
    Проверить предусловия для /deploy.

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

    gates = pipeline.get("gates", {})

    # 3. Проверить ALL_GATES_PASSED
    if not gates.get("ALL_GATES_PASSED", {}).get("passed"):
        print(f"❌ Ворота ALL_GATES_PASSED не пройдены для {fid}")
        print("   → Сначала выполните /aidd-validate")
        return None

    # 4. Двойная проверка всех предыдущих ворот
    required = ["PRD_READY", "RESEARCH_DONE", "PLAN_APPROVED",
                "IMPLEMENT_OK", "REVIEW_OK", "QA_PASSED"]
    missing = [g for g in required if not gates.get(g, {}).get("passed")]

    if missing:
        print(f"❌ Не все ворота пройдены для {fid}: {missing}")
        return None

    print(f"✓ Фича {fid}: {pipeline.get('title')}")
    print("  Все ворота пройдены, готово к деплою")
    return (fid, pipeline)
```

---

## Обновление статуса фичи (v2)

После успешного деплоя перенести фичу из `active_pipelines` в `features_registry`:

```python
def complete_feature_deploy(state: dict, fid: str):
    """
    Завершить деплой фичи и перенести в реестр.

    v2: Удаляем из active_pipelines, добавляем в features_registry
    """
    now = datetime.now().isoformat()
    today = now[:10]

    pipeline = state["active_pipelines"].pop(fid)

    # Отметить DEPLOYED
    pipeline["gates"]["DEPLOYED"] = {
        "passed": True,
        "passed_at": now
    }

    # Перенести в реестр
    state["features_registry"][fid] = {
        "name": pipeline["name"],
        "title": pipeline["title"],
        "status": "DEPLOYED",
        "created": pipeline["created"],
        "deployed": today,
        "artifacts": pipeline["artifacts"],
        "services": pipeline.get("services", [])
    }

    state["updated_at"] = now
```

### Пример после деплоя

```json
{
  "version": "2.0",
  "active_pipelines": {},  // Фича удалена после деплоя
  "features_registry": {
    "F001": {
      "name": "table-booking",
      "title": "Бронирование столиков",
      "status": "DEPLOYED",
      "created": "2024-12-23",
      "deployed": "2024-12-23",
      "artifacts": {
        "prd": "prd/2024-12-23_F001_table-booking-prd.md",
        "research": "research/2024-12-23_F001_table-booking-research.md",
        "plan": "architecture/2024-12-23_F001_table-booking-plan.md",
        "review": "reports/2024-12-23_F001_table-booking-review.md",
        "qa": "reports/2024-12-23_F001_table-booking-qa.md",
        "validation": "reports/2024-12-23_F001_table-booking-validation.md"
      },
      "services": ["booking_api", "booking_data"]
    }
  }
}
```

> **Примечание v2**: После деплоя фича удаляется из `active_pipelines` и
> переносится в `features_registry` со статусом `DEPLOYED`.

---

## Качественные ворота

### DEPLOYED

| Критерий | Описание |
|----------|----------|
| Контейнеры | Docker-контейнеры запущены |
| Health | Health-check проходит |
| Сценарии | Базовые сценарии работают |
| Логи | Нет ошибок в логах |

---

## Команды деплоя

```bash
# Сборка
make build

# Запуск
make up

# Проверка health
make health

# Просмотр логов
make logs

# Остановка
make down
```

---

## Docker Compose команды

```bash
# Сборка образов
docker-compose build

# Запуск в фоне
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Проверка статуса
docker-compose ps

# Остановка
docker-compose down
```

---

## Примеры использования

```bash
# После /validate
/deploy

# Результат:
# ✓ Контейнеры собраны
# ✓ Приложение запущено
# ✓ Health-check: OK
# ✓ DEPLOYED
```

---

## Проверка после деплоя

```bash
# API Health
curl http://localhost:8000/health

# Data API Health
curl http://localhost:8001/health

# Базовый сценарий
curl http://localhost:8000/api/v1/...
```

---

## Готово!

После прохождения ворот `DEPLOYED` MVP готов к использованию.

```
┌─────────────────────────────────────────────┐
│                                             │
│   MVP успешно создан и запущен!             │
│                                             │
│   Время: ~10 минут                          │
│   Покрытие: ≥75%                            │
│   Качество: Production-ready                │
│                                             │
└─────────────────────────────────────────────┘
```
