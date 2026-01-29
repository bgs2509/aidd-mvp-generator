---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**/*.md), Write(**/*.md), Bash(git :*), Bash(python3 :*), Bash(pytest :*), Bash(make :*), Bash(docker :*), Bash(docker-compose :*), Bash(curl :*)
description: Quality & Deploy — полный цикл проверки качества и деплоя
---

> ⚠️ **ENFORCEMENT**: Перед завершением этой команды AI ОБЯЗАН:
> 1. Найти секцию "Чеклист ворот" в конце этого файла
> 2. Создать TodoWrite со ВСЕМИ пунктами (особенно 🔴)
> 3. Выполнить ВСЕ пункты и отметить completed
> 4. Команда завершена ТОЛЬКО когда все 🔴 пункты ✅
>
> Правила: `.aidd/CLAUDE.md` → "Выполнение команд /aidd-*"

# Команда: /finalize

> Запускает Валидатора для полного цикла: Review → Test → Validate → Deploy.
> **Pipeline State v2**: Поддержка параллельных пайплайнов.

---

## Синтаксис

```bash
/finalize
```

---

## Описание

Команда `/aidd-validate` завершает разработку фичи. Поддерживает **два режима**:

### 1. Полный режим (Рекомендуется)

Объединяет 4 последовательных этапа пайплайна:
1. **Code Review** — проверка архитектуры, соглашений, качества
2. **Testing** — запуск тестов, проверка покрытия ≥75%
3. **Validation** — финальная проверка всех ворот
4. **Deploy** — сборка Docker-контейнеров, запуск, health-check

**Результат**: MVP готов к production, все ворота пройдены.

### 2. Быстрый режим (Только документация)

Создаёт **ТОЛЬКО** Completion Report с пометкой `DRAFT`:
- Пропускает Code Review, Testing, Validation, Deploy
- Запускает только статический анализ (mypy, ruff, bandit)
- Отчёт помечается как `DRAFT` (не production-ready)
- Новый gate: `DOCUMENTED` (вместо `DEPLOYED`)

**Когда использовать**:
- Документационные фичи (README, guides)
- Застопорившаяся фича (нужно переключиться на другую)
- Временный коммит без полного QA

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  Быстрый режим НЕ делает фичу production-ready!              │
├─────────────────────────────────────────────────────────────────┤
│  • QA не выполнено → не гарантируется работоспособность         │
│  • Отчёт помечен DRAFT → явный маркер незавершённости           │
│  • Gate: DOCUMENTED (не DEPLOYED)                               │
└─────────────────────────────────────────────────────────────────┘
```

### Единственный артефакт (оба режима)

```
ai-docs/docs/_validation/{YYYY-MM-DD}_{FID}_{slug}-completion.md
```

Completion Report содержит:
- Executive Summary
- Code Review Summary (полный) или Static Analysis (быстрый)
- Testing Summary (полный) или "Skipped (Quick mode)" (быстрый)
- Requirements Traceability (вместо RTM)
- ADR, Scope Changes, Known Limitations, Metrics

> **VERIFY BEFORE ACT**: Перед созданием файлов/директорий проверьте их
> существование (см. CLAUDE.md, раздел "Критические правила").

---

## Агент

**Валидатор** (`.claude/agents/validator.md`) выполняет полный цикл:
- Code Review (см. библиотеку: `.claude/agents/code-review-library.md`)
- Testing (см. библиотеку: `.claude/agents/testing-library.md`)
- Validation (собственная логика)
- Deploy & Completion Report (собственная логика)

---

## Порядок чтения файлов

> **Принцип**: Сначала контекст ЦП, потом инструкции фреймворка.
> **Подробнее**: [docs/initialization.md](../../docs/initialization.md)

### Фаза 1: Контекст целевого проекта

| # | Файл | Условие | Зачем |
|---|------|---------|-------|
| 1 | `./CLAUDE.md` | Если существует | Специфика проекта |
| 2 | `./.pipeline-state.json` | Обязательно | Состояние, ворота |
| 3 | `./ai-docs/docs/_analysis/*.md` | Обязательно | Требования для верификации |
| 4 | `./ai-docs/docs/_plans/mvp/*.md` | Обязательно | План для сверки |
| 5 | `./services/` | Обязательно | Код для проверки |
| 6 | `./docker-compose.yml` | Обязательно | Инфраструктура |
| 7 | `./Makefile` | Обязательно | Команды сборки |

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
| 8 | `.aidd/CLAUDE.md` | Правила фреймворка |
| 9 | `.aidd/workflow.md` | Процесс и ворота |
| 10 | `.aidd/conventions.md` | Соглашения для проверки |
| 11 | `.aidd/.claude/commands/finalize.md` | Этот файл |
| 12 | `.aidd/.claude/agents/validator.md` | Инструкции роли |

### Фаза 4: Шаблоны и база знаний

| # | Файл | Условие |
|---|------|---------|
| 13 | `.aidd/templates/documents/completion-report-template.md` | Для создания Completion Report |
| 14 | `.aidd/knowledge/architecture/*.md` | Архитектурные принципы |
| 15 | `.aidd/knowledge/quality/*.md` | Практики качества |
| 16 | `.aidd/knowledge/infrastructure/docker.md` | Docker практики |

---

## Предусловия

| Ворота | Требование |
|--------|------------|
| `IMPLEMENT_OK` | Код сгенерирован, unit-тесты проходят |

### Алгоритм проверки (v2)

```python
def check_finalize_preconditions() -> tuple[str, dict] | None:
    """
    Проверить предусловия для /finalize.

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

    gates = pipeline.get("gates", {})

    # 3. Проверить IMPLEMENT_OK
    if not gates.get("IMPLEMENT_OK", {}).get("passed"):
        print(f"❌ Ворота IMPLEMENT_OK не пройдены для {fid}")
        print("   → Сначала выполните /aidd-code")
        return None

    print(f"✓ Фича {fid}: {pipeline.get('title')}")
    print("  Готов к финализации (review → test → validate → deploy)")
    return (fid, pipeline)
```

---

## Выбор режима

После проверки предусловий AI ОБЯЗАН запросить у пользователя выбор режима:

```python
def ask_finalize_mode() -> str:
    """
    Запросить у пользователя режим выполнения /finalize.

    Returns:
        "full" или "quick"
    """
    # Использовать AskUserQuestion
    answers = AskUserQuestion(
        questions=[{
            "question": "Какой режим финализации выполнить?",
            "header": "Режим",
            "multiSelect": False,
            "options": [
                {
                    "label": "Полный (Review + Test + Validate + Deploy)",
                    "description": "Рекомендуется. Production-ready результат с полной проверкой качества."
                },
                {
                    "label": "Быстрый (Только Completion Report)",
                    "description": "Создаёт DRAFT отчёт без QA. Используйте для документации или временных коммитов."
                }
            ]
        }]
    )

    # Получить ответ
    selected = answers["Какой режим финализации выполнить?"]

    if "Полный" in selected:
        return "full"
    else:
        return "quick"
```

### Алгоритм выполнения по режиму

```python
def execute_finalize(fid: str, pipeline: dict, mode: str):
    """
    Выполнить финализацию в выбранном режиме.
    """
    if mode == "full":
        # Полный режим (как сейчас)
        step1_code_review(fid, pipeline)      # → REVIEW_OK
        step2_testing(fid, pipeline)          # → QA_PASSED
        step3_validation(fid, pipeline)       # → ALL_GATES_PASSED
        step4_deploy(fid, pipeline)           # → DEPLOYED
        create_completion_report(fid, pipeline, draft=False)
        move_to_features_registry(fid, status="DEPLOYED")

    elif mode == "quick":
        # Быстрый режим (новый)
        step0_static_analysis(fid, pipeline)  # mypy, ruff, bandit
        create_completion_report(fid, pipeline, draft=True)  # DRAFT маркер

        # Отметить DOCUMENTED (не DEPLOYED)
        pipeline["gates"]["DOCUMENTED"] = {
            "passed": True,
            "passed_at": datetime.now().isoformat(),
            "mode": "quick"
        }

        # НЕ переносим в features_registry (остаётся в active_pipelines)
        # Пользователь должен будет выполнить полный /finalize позже
```

---

## Выходные артефакты (в целевом проекте)

| Артефакт | Путь (v2) | Путь (v3) |
|----------|-----------|-----------|
| **Completion Report** | `ai-docs/docs/_validation/{YYYY-MM-DD}_{FID}_{slug}-completion.md` | `ai-docs/docs/_validation/{YYYY-MM-DD}_{FID}_{slug}.md` |

> **Примечание (v2.4+)**:
> - **v2** (по умолчанию): Старая структура `reports/`, имя с дублированием `{name}-completion.md`
> - **v3** (после миграции): Новая структура `_validation/`, имя без дублирования `{name}.md`
> - Режим определяется из `.pipeline-state.json → naming_version`
> - Миграция: `python .aidd/scripts/migrate-naming-v3.py`

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
    artifact_dir = "ai-docs/docs/_validation"
    filename = f"{date}_{fid}_{slug}.md"  # без дублирования -completion
else:  # v2 (по умолчанию)
    artifact_dir = "ai-docs/docs/reports"
    filename = f"{date}_{fid}_{slug}-completion.md"

# Пример: 2024-12-23_F001_table-booking-completion.md (v2)
# Пример: 2024-12-23_F001_table-booking.md (v3)
```

### Обновление .pipeline-state.json

После создания отчёта обновить `active_pipelines[FID]` (v2).

**Пример для naming_version = "v2" (по умолчанию)**:

```json
{
  "naming_version": "v2",
  "active_pipelines": {
    "F001": {
      "branch": "feature/F001-table-booking",
      "name": "table-booking",
      "title": "Бронирование столиков",
      "stage": "DEPLOYED",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "2024-12-23T10:00:00Z"},
        "RESEARCH_DONE": {"passed": true, "passed_at": "2024-12-23T11:00:00Z"},
        "PLAN_APPROVED": {"passed": true, "passed_at": "2024-12-23T12:00:00Z"},
        "IMPLEMENT_OK": {"passed": true, "passed_at": "2024-12-23T14:00:00Z"},
        "REVIEW_OK": {"passed": true, "passed_at": "2024-12-23T15:30:00Z"},
        "QA_PASSED": {"passed": true, "passed_at": "2024-12-23T16:00:00Z", "coverage": 82},
        "ALL_GATES_PASSED": {"passed": true, "passed_at": "2024-12-23T16:15:00Z"},
        "DEPLOYED": {"passed": true, "passed_at": "2024-12-23T17:00:00Z"}
      },
      "artifacts": {
        "prd": "prd/2024-12-23_F001_table-booking-prd.md",
        "research": "research/2024-12-23_F001_table-booking-research.md",
        "plan": "architecture/2024-12-23_F001_table-booking-plan.md",
        "completion": "reports/2024-12-23_F001_table-booking-completion.md"
      }
    }
  }
}
```

**Пример для naming_version = "v3" (после миграции)**:

```json
{
  "naming_version": "v3",
  "active_pipelines": {
    "F001": {
      "branch": "feature/F001-table-booking",
      "name": "table-booking",
      "title": "Бронирование столиков",
      "stage": "DEPLOYED",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "2024-12-23T10:00:00Z"},
        "RESEARCH_DONE": {"passed": true, "passed_at": "2024-12-23T11:00:00Z"},
        "PLAN_APPROVED": {"passed": true, "passed_at": "2024-12-23T12:00:00Z"},
        "IMPLEMENT_OK": {"passed": true, "passed_at": "2024-12-23T14:00:00Z"},
        "REVIEW_OK": {"passed": true, "passed_at": "2024-12-23T15:30:00Z"},
        "QA_PASSED": {"passed": true, "passed_at": "2024-12-23T16:00:00Z", "coverage": 82},
        "ALL_GATES_PASSED": {"passed": true, "passed_at": "2024-12-23T16:15:00Z"},
        "DEPLOYED": {"passed": true, "passed_at": "2024-12-23T17:00:00Z"}
      },
      "artifacts": {
        "prd": "_analysis/2024-12-23_F001_table-booking.md",
        "research": "_research/2024-12-23_F001_table-booking.md",
        "plan": "_plans/mvp/2024-12-23_F001_table-booking.md",
        "completion": "_validation/2024-12-23_F001_table-booking.md"
      }
    }
  }
}
```

---

## Качественные ворота

### Шаг 1: REVIEW_OK

| Критерий | Описание |
|----------|----------|
| Архитектура | Соответствует плану (DDD, HTTP-only) |
| Соглашения | conventions.md соблюдён |
| Quality Cascade | QC-1 до QC-17 пройдены |
| Log-Driven Design | Middleware, tracing, JSON logs настроены |
| Security | Нет секретов в логах, input validation |

#### Проверка Log-Driven Design

| Проверка | Команда |
|----------|---------|
| Middleware | `Grep: "RequestLoggingMiddleware" in services/*/src/main.py` |
| Tracing | `Grep: "setup_tracing_context" in services/` |
| JSON logs | `Grep: "json_logs.*True\|JSONRenderer" in services/` |
| No secrets | `Grep: "logger.*(password\|secret\|token)" in services/` → должно быть 0 |

### Шаг 2: QA_PASSED

| Критерий | Описание |
|----------|----------|
| Тесты | Все тесты проходят (0 failed) |
| Покрытие | Coverage ≥75% |
| FR-* | Все функциональные требования верифицированы |
| Баги | Нет Critical/Blocker багов |

#### Команды тестирования

```bash
# Unit-тесты с покрытием
pytest --cov=src --cov-report=html --cov-fail-under=75

# Через Makefile (если есть)
make test
```

### Шаг 3: ALL_GATES_PASSED

| Ворота | Статус |
|--------|--------|
| PRD_READY | ✓ |
| RESEARCH_DONE | ✓ |
| PLAN_APPROVED | ✓ |
| IMPLEMENT_OK | ✓ |
| REVIEW_OK | ✓ (из шага 1) |
| QA_PASSED | ✓ (из шага 2) |

Дополнительно:
- [ ] Все артефакты существуют
- [ ] Требования прослеживаемы

### Шаг 4: DEPLOYED

| Критерий | Описание |
|----------|----------|
| Контейнеры | Docker-контейнеры собраны и запущены |
| Health | Health-check проходит |
| Сценарии | Базовые сценарии работают |
| Логи | Нет ошибок в логах |
| **Completion Report** | Создан и заполнен полностью |

---

## Шаги выполнения

### Режим: Быстрый (Quick Mode)

> **Используется когда**: Пользователь выбрал "Быстрый режим"

#### Шаг 0: Static Analysis Only

**Цель**: Выполнить минимальные проверки без полного QA.

##### 0.1. Запуск статического анализа

```bash
# Перейти в каждый сервис
cd services/{service_name}

# Type checking
mypy src/ --strict

# Code style
ruff check src/

# Security scan
bandit -r src/ -ll
```

##### 0.2. Проверка результатов

- [ ] `mypy` — 0 errors
- [ ] `ruff` — 0 errors (или только warnings)
- [ ] `bandit` — 0 high/critical issues

**Если есть ошибки**: Записать в Known Issues секцию отчёта.

##### 0.3. Создание DRAFT Completion Report

```python
def create_draft_completion_report(fid: str, pipeline: dict):
    """
    Создать Completion Report с пометкой DRAFT.

    Отличия от полного:
    - Frontmatter: status: "DRAFT"
    - Executive Summary: ⚠️ DRAFT — QA не выполнено
    - Code Review: Static Analysis результаты
    - Testing: "Skipped (Quick mode)"
    - Validation: "Skipped (Quick mode)"
    - Deploy: "Skipped (Quick mode)"
    """
    # Шаблон тот же, но с маркерами DRAFT
    template = read_template("completion-report-template.md")

    # Заполнить секции
    content = fill_draft_template(
        template=template,
        fid=fid,
        pipeline=pipeline,
        static_analysis_results=get_static_analysis_results()
    )

    # Сохранить
    path = f"ai-docs/docs/_validation/{date}_{fid}_{slug}-completion.md"
    write_file(path, content)

    return path
```

##### 0.4. Обновить pipeline state

```python
# Отметить DOCUMENTED (новый gate)
pipeline["gates"]["DOCUMENTED"] = {
    "passed": True,
    "passed_at": datetime.now().isoformat(),
    "mode": "quick",
    "artifact": completion_path
}

# Добавить completion в artifacts
pipeline["artifacts"]["completion"] = completion_path

# НЕ переносим в features_registry!
# Фича остаётся в active_pipelines с gate=DOCUMENTED
```

**Результат быстрого режима**:
- ✅ Completion Report создан (DRAFT)
- ✅ Gate DOCUMENTED пройден
- ⚠️ Фича НЕ production-ready
- ⚠️ Останется в `active_pipelines` (не переносится в `features_registry`)

---

### Режим: Полный (Full Mode)

> **Используется когда**: Пользователь выбрал "Полный режим" (рекомендуется)

### Шаг 1: Code Review

**Цель**: Проверить качество кода перед тестированием.

#### 1.1. Проверка архитектуры

```bash
# Убедиться, что бизнес-сервисы не обращаются к БД
grep -r "psycopg\|sqlalchemy\|asyncpg" services/*_api/src/ --exclude-dir=tests

# Должен быть пустой результат для *_api (только *_data может иметь)
```

Проверить:
- [ ] Слои DDD (`api/application/domain/infrastructure`)
- [ ] HTTP-only доступ к данным (Business API → Data API)
- [ ] Нет прямых обращений к БД из бизнес-логики

#### 1.2. Проверка соглашений

Читать `.aidd/conventions.md` и проверить:
- [ ] Именование переменных (`snake_case`)
- [ ] Именование классов (`PascalCase`)
- [ ] Структура модулей
- [ ] Docstrings для публичных функций
- [ ] Type hints везде

#### 1.3. Quality Cascade (QC-1 до QC-17)

Документация: `.aidd/knowledge/quality/quality-cascade.md`

Ключевые проверки:
- [ ] QC-1: SOLID principles
- [ ] QC-4: DRY — нет дублирования
- [ ] QC-5: KISS — простые решения
- [ ] QC-6: YAGNI — нет лишнего кода
- [ ] QC-13: Security — нет SQL injection, XSS
- [ ] QC-17: HTTP-only Data Access

#### 1.4. Log-Driven Design

Проверить наличие:
```python
# В main.py каждого сервиса
app.add_middleware(RequestLoggingMiddleware)

# В каждом HTTP client
log_external_call_start(...)
log_external_call_end(...)

# В каждом repository
log_db_operation(...)
```

#### 1.5. Security checklist

- [ ] Нет секретов в логах (`logger.*(password|token|secret)`)
- [ ] Input validation на границах системы
- [ ] Нет SQL injection (используется ORM/параметризованные запросы)
- [ ] Нет XSS (escaping в шаблонах, если есть)

**Если найдены проблемы** → вернуться к `/aidd-code` для исправления.

**Если всё ОК** → отметить `REVIEW_OK`:

```python
gates["REVIEW_OK"] = {
    "passed": True,
    "passed_at": datetime.now().isoformat()
}
```

---

### Шаг 2: Testing

**Цель**: Запустить все тесты и проверить покрытие ≥75%.

#### 2.1. Запуск unit-тестов

```bash
# Перейти в директорию каждого сервиса
cd services/{service_name}

# Запустить тесты с покрытием
pytest --cov=src --cov-report=term-missing --cov-fail-under=75 -v
```

#### 2.2. Анализ результатов

Проверить:
- [ ] Все тесты проходят (`0 failed`)
- [ ] Coverage ≥75%
- [ ] Нет пропущенных тестов (`0 skipped` или обоснованы)

Если coverage < 75%:
```bash
# Посмотреть, какие файлы не покрыты
pytest --cov=src --cov-report=html
# Открыть htmlcov/index.html
```

#### 2.3. Верификация требований

Прочитать PRD (`ai-docs/docs/_analysis/{name}-prd.md`) и проверить:
- [ ] Все FR-* требования имеют тесты
- [ ] Acceptance criteria выполнены

**Если тесты не проходят** → вернуться к `/aidd-code` для исправления.

**Если всё ОК** → отметить `QA_PASSED`:

```python
gates["QA_PASSED"] = {
    "passed": True,
    "passed_at": datetime.now().isoformat(),
    "coverage": 82  # Реальное значение из pytest
}
```

---

### Шаг 3: Validation

**Цель**: Финальная проверка всех ворот и артефактов.

#### 3.1. Проверка всех ворот

```python
required_gates = [
    "PRD_READY",
    "RESEARCH_DONE",
    "PLAN_APPROVED",
    "IMPLEMENT_OK",
    "REVIEW_OK",
    "QA_PASSED"
]

missing = [g for g in required_gates if not gates.get(g, {}).get("passed")]

if missing:
    print(f"❌ Не все ворота пройдены: {missing}")
    return False
```

#### 3.2. Проверка артефактов

```python
artifacts = pipeline.get("artifacts", {})
required_artifacts = ["prd", "research", "plan"]

missing_artifacts = [a for a in required_artifacts if a not in artifacts]

if missing_artifacts:
    print(f"❌ Отсутствуют артефакты: {missing_artifacts}")
    return False

# Проверить, что файлы существуют
for artifact_type, path in artifacts.items():
    full_path = f"ai-docs/docs/{path}"
    if not os.path.exists(full_path):
        print(f"❌ Артефакт не найден: {full_path}")
        return False
```

**Если всё ОК** → отметить `ALL_GATES_PASSED`:

```python
gates["ALL_GATES_PASSED"] = {
    "passed": True,
    "passed_at": datetime.now().isoformat()
}
```

---

### Шаг 4: Deploy & Completion Report

**Цель**: Запустить приложение и создать итоговый Completion Report.

#### 4.1 Docker Deploy

##### 4.1.1. Сборка Docker-контейнеров

```bash
# Сборка
make build
# или
docker-compose build

# Проверить, что все образы собраны без ошибок
docker images | grep {project_name}
```

##### 4.1.2. Запуск приложения

```bash
# Запуск в фоне
make up
# или
docker-compose up -d

# Проверить статус
docker-compose ps
```

##### 4.1.3. Health-check

```bash
# Проверить health endpoint каждого сервиса
curl http://localhost:8000/health
curl http://localhost:8001/health

# Ожидаемый результат: {"status": "ok"}
```

##### 4.1.4. Базовые сценарии

Выполнить базовые API запросы из PRD:

```bash
# Пример для booking системы
curl -X POST http://localhost:8000/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{"restaurant_id": 1, "date": "2024-12-25", "time": "18:00", "guests": 4}'
```

#### 4.2 Create Completion Report (ОБЯЗАТЕЛЬНО!)

**КРИТИЧЕСКИ ВАЖНО**: Этот шаг ОБЯЗАТЕЛЕН.

**Путь**: `ai-docs/docs/_validation/{YYYY-MM-DD}_{FID}_{slug}-completion.md`

**Использовать шаблон**: `.aidd/templates/documents/completion-report-template.md`

**Содержание**:
- Executive Summary
- Реализованные компоненты
- ADR (Architecture Decision Records)
- Scope Changes (план vs факт)
- Known Limitations
- Метрики качества
- Ссылки на все артефакты

##### 4.2.1. Прочитать все артефакты

```python
# 1. PRD → извлечь требования, scope, acceptance criteria
prd_path = artifacts.get("prd")
prd_content = read_file(f"ai-docs/docs/{prd_path}")

# 2. Architecture Plan → извлечь ADR (архитектурные решения)
plan_path = artifacts.get("plan")
plan_content = read_file(f"ai-docs/docs/{plan_path}")

# 3. Research → извлечь контекст
research_path = artifacts.get("research")
research_content = read_file(f"ai-docs/docs/{research_path}")
```

##### 4.2.2. Собрать информацию о реализации

```python
# Сервисы (из pipeline.services)
services = pipeline.get("services", [])

# Endpoints (из кода)
endpoints = extract_endpoints_from_code("services/*/src/api/v1/")

# Модели данных (из кода)
models = extract_models_from_code("services/*/src/domain/entities/")
```

##### 4.2.3. Сформировать ADR

Architecture Decision Records — ключевые решения с обоснованием:

```markdown
## 3. Architecture Decision Records (ADR)

### ADR-001: HTTP-only Data Access
**Дата**: 2024-12-23
**Статус**: Принято

**Контекст**: Бизнес-логика должна быть изолирована от БД.

**Решение**: Business API → HTTP → Data API → БД.

**Обоснование**:
- Упрощает тестирование (mock HTTP)
- Позволяет масштабировать data layer независимо
- Соответствует архитектуре Level 2 (MVP)

**Альтернативы**:
- Прямой доступ к БД — нарушает изоляцию
- gRPC — избыточно для MVP

**Trade-offs**:
- Небольшая задержка на HTTP call
- Дополнительный сервис для поддержки
```

##### 4.2.4. Документировать Scope Changes

Сравнить PRD (план) vs реализация (факт):

```markdown
## 4. Отклонения от плана (Scope Changes)

### 4.1. План vs Факт

| Компонент | План (PRD) | Факт (Реализация) | Причина |
|-----------|------------|-------------------|---------|
| Email уведомления | Планировались | Отложены | Нет интеграции с SMTP |
| Отмена бронирования | В scope | Реализовано | - |

### 4.2. Deferred Items
- Email уведомления → следующая итерация
- SMS подтверждения → требует внешнего сервиса
```

##### 4.2.5. Записать Known Limitations

```markdown
## 5. Известные ограничения

### 5.1. Known Limitations
- Нет поддержки recurring bookings (еженедельные бронирования)
- Максимум 10 гостей на бронирование (ограничение БД)

### 5.2. Technical Debt
- TODO: Добавить кеширование для списка ресторанов
- TODO: Оптимизировать запрос доступности столиков
```

##### 4.2.6. Записать метрики

```markdown
## 6. Метрики качества

| Метрика | Значение | Статус |
|---------|----------|--------|
| Test Coverage | 82% | ✅ (≥75%) |
| Unit Tests | 45 passed | ✅ |
| Integration Tests | 12 passed | ✅ |
| Security Scan | 0 Critical | ✅ |
| Code Quality | A (SonarQube) | ✅ |
```

##### 4.2.7. Создать файл

```bash
# Путь к файлу
completion_path="ai-docs/docs/_validation/{date}_{FID}_{slug}-completion.md"

# Использовать шаблон
template_path=".aidd/templates/documents/completion-report-template.md"
```

Заполнить все секции из шаблона:
1. Executive Summary
2. Реализованные компоненты
3. ADR
4. Scope Changes
5. Known Limitations
6. Метрики
7. Зависимости
8. Ссылки
9. Timeline
10. Рекомендации
11. Quick Reference

##### 4.2.8. Обновить pipeline state

```python
# Добавить completion report в artifacts
pipeline["artifacts"]["completion"] = completion_path

# Отметить DEPLOYED
gates["DEPLOYED"] = {
    "passed": True,
    "passed_at": datetime.now().isoformat()
}

# Обновить stage
pipeline["stage"] = "DEPLOYED"
```

#### 4.3 Перенести в features_registry

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

    # Перенести в реестр
    state["features_registry"][fid] = {
        "name": pipeline["name"],
        "title": pipeline["title"],
        "status": "DEPLOYED",
        "created": pipeline["created"],
        "deployed": today,
        "artifacts": pipeline["artifacts"],  # Включает completion
        "services": pipeline.get("services", [])
    }

    state["updated_at"] = now
```

---

## Проверка после деплоя

```bash
# API Health
curl http://localhost:8000/health

# Data API Health
curl http://localhost:8001/health

# Базовый сценарий (из PRD)
curl http://localhost:8000/api/v1/...

# Просмотр логов
docker-compose logs -f
```

---

## Примеры использования

### Пример 1: Полный режим (Production-ready)

```bash
# После /generate
/finalize

# AI спрашивает режим
Какой режим финализации выполнить?
[1] Полный (Review + Test + Validate + Deploy)  ← Выбираем
[2] Быстрый (Только Completion Report)

# Результат:
# ✓ Step 1: Code Review → REVIEW_OK
# ✓ Step 2: Testing (Coverage 82%) → QA_PASSED
# ✓ Step 3: Validation → ALL_GATES_PASSED
# ✓ Step 4: Deploy → DEPLOYED
# ✓ Completion Report: ai-docs/docs/_validation/2024-12-23_F001_table-booking-completion.md
# ✓ Фича перенесена в features_registry
```

### Пример 2: Быстрый режим (DRAFT документация)

```bash
# После /generate, но фича застопорилась
/finalize

# AI спрашивает режим
Какой режим финализации выполнить?
[1] Полный (Review + Test + Validate + Deploy)
[2] Быстрый (Только Completion Report)  ← Выбираем

# Результат:
# ✓ Step 0: Static Analysis (mypy, ruff, bandit)
# ✓ Completion Report (DRAFT): ai-docs/docs/_validation/2024-12-23_F042_oauth-auth-completion.md
# ✓ Gate: DOCUMENTED (не DEPLOYED)
# ⚠️ Фича остаётся в active_pipelines (не production-ready)

# Теперь можно начать новую фичу
/aidd-analyze "Добавить систему платежей"
```

---

## Чеклист ворот (итоговый)

> ⚠️ AI ОБЯЗАН создать TodoWrite с этими пунктами.
> Выбор пунктов зависит от режима (быстрый или полный).

### Общие шаги (для обоих режимов)

- [ ] 🔴 Проверить предусловия (`IMPLEMENT_OK` пройден)
- [ ] 🔴 Определить FID по текущей git ветке
- [ ] 🔴 Запросить у пользователя режим (Quick / Full)
- [ ] 🔴 Прочитать артефакты PRD, Research, Plan

---

### Режим: Быстрый (Quick Mode)

> Используется когда: документационная фича, застопорившаяся фича, временный коммит

#### Шаг 0: Static Analysis

- [ ] 🔴 Запустить mypy на всех сервисах (0 errors)
- [ ] 🔴 Запустить ruff на всех сервисах (0 errors)
- [ ] 🔴 Запустить bandit на всех сервисах (0 critical)
- [ ] 🟡 Записать результаты статического анализа

#### Completion Report (DRAFT)

- [ ] 🔴 **Создать DRAFT Completion Report**
  - [ ] Frontmatter: `status: "DRAFT"`
  - [ ] Executive Summary: "⚠️ DRAFT — QA не выполнено"
  - [ ] Code Review: Static Analysis результаты
  - [ ] Testing: "Skipped (Quick mode)"
  - [ ] Validation: "Skipped (Quick mode)"
  - [ ] Deploy: "Skipped (Quick mode)"
  - [ ] ADR: Извлечь из Architecture Plan
  - [ ] Scope Changes: Сравнить PRD vs факт (если доступно)
  - [ ] Known Limitations: Список ограничений
  - [ ] Метрики: Только static analysis результаты
- [ ] 🔴 `.pipeline-state.json` обновлён
  - [ ] Gate `DOCUMENTED` отмечен как passed
  - [ ] Completion Report добавлен в `artifacts.completion`
  - [ ] `stage` остаётся в active_pipelines (НЕ переносить в features_registry)

---

### Режим: Полный (Full Mode)

> Рекомендуется. Production-ready результат.

#### Шаг 1: Code Review

- [ ] 🔴 Архитектура соответствует плану (DDD, HTTP-only)
- [ ] 🔴 Security checklist пройден (нет уязвимостей)
- [ ] 🟡 Code style соблюдён (conventions.md)
- [ ] 🟡 Log-Driven Design проверен
- [ ] 🟡 Quality Cascade (QC-1 до QC-17) пройден
- [ ] 🔴 Gate `REVIEW_OK` отмечен как passed

#### Шаг 2: Testing

- [ ] 🔴 Все тесты проходят (0 failed)
- [ ] 🔴 Coverage ≥ 75%
- [ ] 🟡 Integration тесты пройдены
- [ ] 🟡 Все FR-* требования верифицированы
- [ ] 🔴 Gate `QA_PASSED` отмечен как passed (с coverage)

#### Шаг 3: Validation

- [ ] 🔴 Все предыдущие ворота пройдены (PRD→QA)
- [ ] 🔴 Все артефакты существуют и актуальны
- [ ] 🔴 Gate `ALL_GATES_PASSED` отмечен как passed

#### Шаг 4: Deploy & Completion Report

- [ ] 🔴 Docker-контейнеры собраны (`make build`)
- [ ] 🔴 Приложение запущено (`make up`)
- [ ] 🔴 Health-check проходит (`make health`)
- [ ] 🔴 Базовые сценарии работают (API запросы успешны)
- [ ] 🔴 **Completion Report создан** (Production-ready)
  - [ ] Executive Summary заполнен
  - [ ] Code Review Summary (из шага 1)
  - [ ] Testing Summary (из шага 2)
  - [ ] Requirements Traceability (RTM)
  - [ ] ADR задокументированы
  - [ ] Scope Changes описаны
  - [ ] Known Limitations перечислены
  - [ ] Метрики записаны (coverage, tests, security)
  - [ ] Timeline заполнен
- [ ] 🔴 `.pipeline-state.json` обновлён
  - [ ] Gate `DEPLOYED` отмечен как passed
  - [ ] Completion Report добавлен в `artifacts.completion`
  - [ ] Фича перенесена в `features_registry` (из active_pipelines)
- [ ] 🟡 Логи проверены (нет ошибок)

---

## Чеклист ворот DEPLOYED (BLOCKER)

> ⚠️ **КРИТИЧЕСКАЯ СЕКЦИЯ**: Без выполнения ВСЕХ 🔴 пунктов команда НЕ завершена!

```
┌─────────────────────────────────────────────────────────────────┐
│  🔴 BLOCKER (без этого команда НЕ завершена):                    │
├─────────────────────────────────────────────────────────────────┤
│  □ Docker-контейнеры собраны и запущены                         │
│  □ Health-check проходит                                         │
│  □ Базовые сценарии работают (API запросы успешны)              │
│  □ **Completion Report создан** в reports/{date}_{FID}_{slug}   │
│  □ Фича перенесена из active_pipelines в features_registry      │
│  □ .pipeline-state.json обновлён                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Автоматическая проверка Completion Report

AI ОБЯЗАН выполнить эту проверку перед завершением команды:

```python
from pathlib import Path
from datetime import datetime

def verify_completion_report_exists(fid: str, slug: str, naming_version: str = "v2") -> bool:
    """
    Проверить, что Completion Report существует.

    ❌ BLOCKER: Если файл не существует, команда НЕ завершена!

    Args:
        fid: Feature ID (например, "F001")
        slug: Feature slug (например, "table-booking")
        naming_version: "v2" (по умолчанию) или "v3"

    Returns:
        True если файл существует, False иначе
    """
    date = datetime.now().strftime("%Y-%m-%d")

    if naming_version == "v3":
        completion_path = Path(f"ai-docs/docs/_validation/{date}_{fid}_{slug}.md")
    else:  # v2 (по умолчанию)
        completion_path = Path(f"ai-docs/docs/_validation/{date}_{fid}_{slug}-completion.md")

    if not completion_path.exists():
        print("❌ BLOCKER: Completion Report не создан!")
        print(f"   Ожидается: {completion_path}")
        print("   ")
        print("   Необходимо:")
        print("   1. Использовать шаблон: .aidd/templates/documents/completion-report-template.md")
        print("   2. Заполнить ВСЕ обязательные секции")
        print("   3. Сохранить в указанный путь")
        return False

    print(f"✅ Completion Report существует: {completion_path}")
    return True


# Использование в конце /aidd-validate:
if not verify_completion_report_exists(fid, slug, naming_version):
    raise RuntimeError("BLOCKER: Completion Report не создан! Команда не может быть завершена.")
```

### Что должен содержать Completion Report

| Секция | Статус | Описание |
|--------|--------|----------|
| Executive Summary | 🔴 BLOCKER | 2-3 предложения о результате |
| Реализованные компоненты | 🔴 BLOCKER | Сервисы, endpoints, модели |
| ADR | 🔴 BLOCKER | Архитектурные решения с обоснованием |
| Scope Changes | 🟡 REQUIRED | План vs Факт |
| Known Limitations | 🟡 REQUIRED | Ограничения и workarounds |
| Метрики | 🟡 REQUIRED | Coverage, tests, security |
| Timeline | ⚪ OPTIONAL | История прохождения ворот |
| Рекомендации | ⚪ OPTIONAL | Для следующих итераций |

---

## Готово!

После прохождения всех ворот MVP готов к использованию.

```
┌─────────────────────────────────────────────┐
│                                             │
│   MVP успешно создан и запущен!             │
│                                             │
│   Время: ~10 минут                          │
│   Покрытие: ≥75%                            │
│   Качество: Production-ready                │
│   Артефакт: 1 Completion Report             │
│                                             │
└─────────────────────────────────────────────┘
```
