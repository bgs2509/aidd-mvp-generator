# workflow.md — Процесс разработки AIDD-MVP

> **Назначение**: Описание 9-этапного процесса разработки MVP (этапы 0-8).
> AI-агент ОБЯЗАН следовать этому процессу и проходить качественные ворота.
>
> **Философия**: Артефакты = Память. Не полагаемся на память чата.

---

## Обзор процесса

AIDD-MVP Generator использует 9-этапный конвейер разработки (Этапы 0-8)
с обязательными качественными воротами между этапами. Переход на следующий
этап возможен ТОЛЬКО после прохождения ворот текущего этапа.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AIDD-MVP DEVELOPMENT PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────┐                                                               │
│  │ BOOTSTRAP │  Этап 0: Инициализация целевого проекта                      │
│  │   /init   │  ─────────────────────────────────────────────────────────── │
│  └─────┬─────┘                                                               │
│        │ BOOTSTRAP_READY                                                     │
│        ▼                                                                     │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐                  │
│  │  ИДЕЯ   │───▶│ИССЛЕДО- │───▶│АРХИТЕК- │───▶│РЕАЛИЗА- │                  │
│  │         │    │ ВАНИЕ   │    │  ТУРА   │    │   ЦИЯ   │                  │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘                  │
│       │              │              │              │                        │
│  ┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐                  │
│  │PRD_READY│    │RESEARCH │    │  PLAN   │    │IMPLEMENT│                  │
│  │         │    │  _DONE  │    │APPROVED │    │   _OK   │                  │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘                  │
│                                                                              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐                  │
│  │  РЕВЬЮ  │───▶│   QA    │───▶│ВАЛИДА-  │───▶│ ДЕПЛОЙ  │                  │
│  │         │    │         │    │   ЦИЯ   │    │         │                  │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘                  │
│       │              │              │              │                        │
│  ┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐                  │
│  │ REVIEW  │    │   QA    │    │ALL_GATES│    │DEPLOYED │                  │
│  │   _OK   │    │ PASSED  │    │ PASSED  │    │         │                  │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Два режима работы

### CREATE — Создание нового MVP

Полный 9-этапный процесс (этапы 0-8) для создания проекта с нуля.

```bash
/idea "Создать сервис бронирования столиков в ресторанах"
```

### FEATURE — Добавление функционала

Адаптированный процесс для добавления фичи в существующий проект.

```bash
/idea "Добавить систему уведомлений по email"
```

**Отличия режима FEATURE**:
- Этап 2 (Исследование) — анализ существующего кода
- Этап 3 (Архитектура) — `/feature-plan` вместо `/plan`
- Интеграция с существующими компонентами

---

## Bootstrap: Инициализация целевого проекта

> **ВАЖНО**: Артефакты создаются в ЦЕЛЕВОМ ПРОЕКТЕ, не в генераторе!
> Фреймворк должен быть подключен как Git Submodule в `.aidd/`
>
> **Полный алгоритм инициализации**: [docs/initialization.md](docs/initialization.md)

### Принцип инициализации

```
┌─────────────────────────────────────────────────────────────────────┐
│  Сначала понять ГДЕ мы (контекст ЦП),                               │
│  потом КАК действовать (инструкции фреймворка)                      │
├─────────────────────────────────────────────────────────────────────┤
│  ФАЗА 1: ./CLAUDE.md → ./.pipeline-state.json → ./ai-docs/docs/     │
│  ФАЗА 2: Проверка предусловий (ворот)                               │
│  ФАЗА 3: .aidd/CLAUDE.md → .aidd/workflow.md → команда → роль       │
│  ФАЗА 4: Шаблоны (если артефакт не существует)                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Предварительные условия

Перед запуском `/idea` фреймворк должен быть подключен:

```bash
# Если фреймворк ещё не подключен
git submodule add https://github.com/your-org/aidd-mvp-generator.git .aidd
git submodule update --init --recursive
```

### Автоматическая инициализация при `/idea`

При первом запуске `/idea` AI-агент выполняет:

```bash
# 1. Создание структуры артефактов
mkdir -p ai-docs/docs/{prd,architecture,plans,reports}

# 2. Инициализация состояния пайплайна
cat > .pipeline-state.json << 'EOF'
{
  "project_name": "",
  "mode": "CREATE",
  "current_stage": 1,
  "gates": {}
}
EOF
```

### Определение режима

| Признак | Режим |
|---------|-------|
| Есть `services/` или `docker-compose.yml` | **FEATURE** |
| Пустая директория или нет признаков проекта | **CREATE** |

#### Алгоритм определения режима (P-006)

```python
def detect_mode() -> str:
    """
    Точный алгоритм определения режима работы.

    Returns:
        'CREATE' или 'FEATURE'
    """
    # 1. Проверить .pipeline-state.json (приоритет)
    if Path(".pipeline-state.json").exists():
        state = read_json(".pipeline-state.json")
        return state.get("mode", "CREATE")

    # 2. Признаки существующего проекта
    project_markers = [
        "services/",           # Сгенерированные сервисы
        "docker-compose.yml",  # Инфраструктура
        "docker-compose.yaml",
        "ai-docs/docs/",       # Артефакты AIDD
        "Makefile",            # Сборка
    ]

    for marker in project_markers:
        if Path(marker).exists():
            return "FEATURE"

    # 3. Дополнительная проверка — наличие Python кода
    python_files = list(Path(".").glob("**/*.py"))
    if len(python_files) > 5:  # Больше 5 файлов — вероятно проект
        return "FEATURE"

    return "CREATE"
```

**Важно**: Режим можно переопределить явно:
```bash
/idea --mode=FEATURE "Добавить фичу"
```

---

## Этапы процесса

### Этап 0: Bootstrap (Инициализация)

| Параметр | Значение |
|----------|----------|
| **Команда** | `/init` (ручной) или авто с `/idea` |
| **Агент** | — (системный) |
| **Вход** | Пустая директория с git и .aidd/ |
| **Выход** | Структура ЦП, `.pipeline-state.json`, `CLAUDE.md` |
| **Ворота** | `BOOTSTRAP_READY` |

**Критерии прохождения ворот BOOTSTRAP_READY**:
- [ ] Git репозиторий инициализирован
- [ ] Фреймворк `.aidd/` подключен (submodule)
- [ ] Python версия >= 3.11
- [ ] Docker установлен
- [ ] Структура `ai-docs/docs/` создана
- [ ] `.pipeline-state.json` инициализирован

**Проверки окружения**:
```bash
# 1. Git репозиторий
git rev-parse --git-dir

# 2. Фреймворк подключен
test -f .aidd/CLAUDE.md

# 3. Python версия
python3 --version  # >= 3.11

# 4. Docker
docker --version
```

**Действия при инициализации**:
```bash
# Создание структуры
mkdir -p ai-docs/docs/{prd,architecture,plans,reports}

# Инициализация состояния
echo '{"project_name":"","mode":"CREATE","current_stage":0,"gates":{"BOOTSTRAP_READY":{"passed":true}}}' > .pipeline-state.json

# Создание CLAUDE.md
echo "# Project\n\nСм. .aidd/CLAUDE.md" > CLAUDE.md
```

**Примечание**: Этап 0 выполняется автоматически при первом `/idea`, если проверки
не были пройдены ранее. Явный запуск `/init` рекомендуется для диагностики.

---

### Этап 1: Идея → PRD

| Параметр | Значение |
|----------|----------|
| **Команда** | `/idea "описание"` |
| **Агент** | Аналитик |
| **Вход** | Описание идеи от пользователя |
| **Выход** | `ai-docs/docs/prd/{name}-prd.md` |
| **Ворота** | `PRD_READY` |

**Критерии прохождения ворот PRD_READY**:
- [ ] Все секции PRD заполнены
- [ ] Требования имеют ID (FR-*, NF-*, UI-*)
- [ ] Определены критерии приёмки
- [ ] Нет блокирующих открытых вопросов

**Артефакты** (в целевом проекте):
```
{project-name}/
└── ai-docs/docs/prd/
    └── booking-restaurant-prd.md
```

---

### Этап 2: Исследование

| Параметр | Значение |
|----------|----------|
| **Команда** | `/research` |
| **Агент** | Исследователь |
| **Вход** | PRD, существующий код (для FEATURE) |
| **Выход** | Анализ, выявленные паттерны |
| **Ворота** | `RESEARCH_DONE` |

**Критерии прохождения ворот RESEARCH_DONE**:
- [ ] Существующий код проанализирован (для FEATURE)
- [ ] Архитектурные паттерны выявлены
- [ ] Технические ограничения определены
- [ ] Рекомендации по интеграции сформулированы

**Режим CREATE**: Анализ требований, выбор технологий.
**Режим FEATURE**: Анализ кода, выявление точек расширения.

---

### Этап 3: Архитектура

| Параметр | Значение |
|----------|----------|
| **Команда** | `/plan` (CREATE) или `/feature-plan` (FEATURE) |
| **Агент** | Архитектор |
| **Вход** | PRD, результаты исследования |
| **Выход** | `ai-docs/docs/architecture/{name}-plan.md` |
| **Ворота** | `PLAN_APPROVED` |

**Критерии прохождения ворот PLAN_APPROVED**:
- [ ] Компоненты системы описаны
- [ ] API контракты определены
- [ ] NFR (нефункциональные требования) учтены
- [ ] **План утверждён пользователем**

**Важно**: Этот этап ТРЕБУЕТ явного подтверждения от пользователя!

**Артефакты** (в целевом проекте):
```
{project-name}/
└── ai-docs/docs/
    ├── architecture/
    │   └── booking-restaurant-plan.md
    └── plans/
        └── notification-feature-plan.md  # для FEATURE
```

---

### Этап 4: Реализация

| Параметр | Значение |
|----------|----------|
| **Команда** | `/generate` |
| **Агент** | Реализатор |
| **Вход** | Утверждённый план |
| **Выход** | Код сервисов, тесты, инфраструктура |
| **Ворота** | `IMPLEMENT_OK` |

**Критерии прохождения ворот IMPLEMENT_OK**:
- [ ] Код написан согласно плану
- [ ] Все unit-тесты проходят
- [ ] Структура соответствует DDD/Hexagonal
- [ ] Type hints и docstrings присутствуют

**Подэтапы реализации**:

| # | Подэтап | Выход |
|---|---------|-------|
| 4.1 | Инфраструктура | docker-compose, Makefile, CI/CD |
| 4.2 | Data Service | API для работы с БД |
| 4.3 | Business API | REST API на FastAPI |
| 4.4 | Background Worker | Фоновые задачи (если нужен) |
| 4.5 | Telegram Bot | Бот (если нужен) |
| 4.6 | Тесты | Unit + Integration тесты |

---

### Этап 5: Ревью

| Параметр | Значение |
|----------|----------|
| **Команда** | `/review` |
| **Агент** | Ревьюер |
| **Вход** | Сгенерированный код |
| **Выход** | `ai-docs/docs/reports/review-report.md` |
| **Ворота** | `REVIEW_OK` |

**Критерии прохождения ворот REVIEW_OK**:
- [ ] Код соответствует conventions.md
- [ ] Архитектура соответствует плану
- [ ] Нет критических замечаний
- [ ] DRY/KISS/YAGNI соблюдены

**Артефакты** (в целевом проекте):
```
{project-name}/
└── ai-docs/docs/reports/
    └── review-report.md
```

---

### Этап 6: QA

| Параметр | Значение |
|----------|----------|
| **Команда** | `/test` |
| **Агент** | QA |
| **Вход** | Код после ревью |
| **Выход** | `ai-docs/docs/reports/qa-report.md` |
| **Ворота** | `QA_PASSED` |

**Критерии прохождения ворот QA_PASSED**:
- [ ] Покрытие тестами ≥75%
- [ ] Все тесты проходят
- [ ] Нет критических багов
- [ ] Требования из PRD проверены

**Артефакты** (в целевом проекте):
```
{project-name}/
└── ai-docs/docs/reports/
    └── qa-report.md
```

---

### Этап 7: Валидация

| Параметр | Значение |
|----------|----------|
| **Команда** | `/validate` |
| **Агент** | Валидатор |
| **Вход** | Все артефакты проекта |
| **Выход** | `ai-docs/docs/reports/validation-report.md` |
| **Ворота** | `ALL_GATES_PASSED` |

**Критерии прохождения ворот ALL_GATES_PASSED**:
- [ ] Все предыдущие ворота пройдены
- [ ] Артефакты соответствуют требованиям
- [ ] RTM (Requirements Traceability Matrix) актуальна
- [ ] Проект готов к деплою

**Артефакты** (в целевом проекте):
```
{project-name}/
└── ai-docs/docs/
    ├── reports/
    │   └── validation-report.md
    └── rtm.md  # Матрица трассировки требований
```

---

### Этап 8: Деплой

| Параметр | Значение |
|----------|----------|
| **Команда** | `/deploy` |
| **Агент** | Валидатор |
| **Вход** | Валидированный проект |
| **Выход** | Работающее приложение |
| **Ворота** | `DEPLOYED` |

**Критерии прохождения ворот DEPLOYED**:
- [ ] Docker-контейнеры собраны
- [ ] Приложение запущено
- [ ] Health-check проходит
- [ ] Базовые сценарии работают

**Команды деплоя**:
```bash
# Сборка и запуск
make build
make up

# Проверка
make health
make logs
```

---

## Таблица команд и ворот

| # | Этап | Команда | Агент | Ворота |
|---|------|---------|-------|--------|
| 0 | Bootstrap | `/init` | — | `BOOTSTRAP_READY` |
| 1 | Идея | `/idea` | Аналитик | `PRD_READY` |
| 2 | Исследование | `/research` | Исследователь | `RESEARCH_DONE` |
| 3 | Архитектура | `/plan` | Архитектор | `PLAN_APPROVED` |
| 4 | Реализация | `/generate` | Реализатор | `IMPLEMENT_OK` |
| 5 | Ревью | `/review` | Ревьюер | `REVIEW_OK` |
| 6 | QA | `/test` | QA | `QA_PASSED` |
| 7 | Валидация | `/validate` | Валидатор | `ALL_GATES_PASSED` |
| 8 | Деплой | `/deploy` | Валидатор | `DEPLOYED` |

### Почему 9 этапов (0-8) и 7 ролей (P-033)

Валидатор выполняет два этапа:
- **Этап 7 (Валидация)**: Проверка всех ворот и артефактов
- **Этап 8 (Деплой)**: Запуск приложения

Это логично, так как:
1. Валидатор уже имеет полный контекст всех артефактов
2. Деплой — логическое продолжение валидации
3. Оба этапа работают с финальным состоянием проекта

---

## Артефакты по этапам (в целевом проекте)

> **ВАЖНО**: Все артефакты создаются в ЦЕЛЕВОМ ПРОЕКТЕ, не в генераторе!

```
{project-name}/                      ← Целевой проект
│
├── .pipeline-state.json             # Состояние пайплайна
│
└── ai-docs/docs/
    ├── prd/
    │   └── {name}-prd.md            # Этап 1: PRD документ
    │
    ├── architecture/
    │   └── {name}-plan.md           # Этап 3: Архитектурный план
    │
    ├── plans/
    │   └── {feature}-plan.md        # Этап 3: План фичи (FEATURE)
    │
    ├── reports/
    │   ├── review-report.md         # Этап 5: Отчёт ревью
    │   ├── qa-report.md             # Этап 6: Отчёт QA
    │   └── validation-report.md     # Этап 7: Отчёт валидации
    │
    └── rtm.md                       # Матрица трассировки требований
```

---

## Пример полного прохода (режим CREATE)

```bash
# 1. Описываем идею
/idea "Создать сервис бронирования столиков в ресторанах.
Пользователи могут искать рестораны, смотреть свободные столики,
бронировать на определённое время. Рестораны получают уведомления
о новых бронях через Telegram."

# Агент: Аналитик создаёт PRD
# Ворота: PRD_READY ✓

# 2. Исследование
/research

# Агент: Исследователь анализирует требования
# Ворота: RESEARCH_DONE ✓

# 3. Архитектура
/plan

# Агент: Архитектор создаёт план
# Пользователь утверждает план
# Ворота: PLAN_APPROVED ✓

# 4. Реализация
/generate

# Агент: Реализатор генерирует код
# Создаются: infrastructure, data-api, business-api, bot
# Ворота: IMPLEMENT_OK ✓

# 5. Ревью
/review

# Агент: Ревьюер проверяет код
# Ворота: REVIEW_OK ✓

# 6. QA
/test

# Агент: QA запускает тесты
# Coverage: 78% ✓
# Ворота: QA_PASSED ✓

# 7. Валидация
/validate

# Агент: Валидатор проверяет все артефакты
# Ворота: ALL_GATES_PASSED ✓

# 8. Деплой
/deploy

# Агент: Запускает docker-compose
# Ворота: DEPLOYED ✓

# Готово! MVP запущен за ~10 минут
```

---

## Состояние пайплайна (.pipeline-state.json)

> **Философия**: Артефакты = Память. Состояние пайплайна — единый источник истины.

### Формат файла

Файл `.pipeline-state.json` создаётся в корне ЦЕЛЕВОГО ПРОЕКТА при первом `/idea`.

```json
{
  "project_name": "booking-service",
  "mode": "CREATE",
  "current_stage": 4,
  "created_at": "2025-12-21T10:00:00Z",
  "updated_at": "2025-12-21T10:30:00Z",
  "gates": {
    "PRD_READY": {"passed": true, "artifact": "ai-docs/docs/prd/booking-prd.md"},
    "PLAN_APPROVED": {"passed": true, "artifact": "ai-docs/docs/architecture/booking-plan.md"}
  },
  "artifacts": {
    "prd": "ai-docs/docs/prd/booking-prd.md",
    "plan": "ai-docs/docs/architecture/booking-plan.md"
  }
}
```

**Шаблон**: [templates/documents/pipeline-state-template.json](templates/documents/pipeline-state-template.json)

### Обновление состояния

Каждая команда ОБЯЗАНА обновить `.pipeline-state.json`:
1. При старте — проверить предусловия
2. При успехе — отметить ворота пройденными
3. При создании артефакта — записать путь

---

## Алгоритм обнаружения артефактов

Команды используют следующий алгоритм для поиска входных артефактов:

```python
def find_artifact(artifact_type: str) -> Path | None:
    """
    Алгоритм поиска артефакта в целевом проекте.

    Args:
        artifact_type: 'prd', 'plan', 'feature_plan', 'review_report', etc.

    Returns:
        Path к артефакту или None
    """
    # 1. Проверить .pipeline-state.json
    state = read_json(".pipeline-state.json")
    if state and state.get("artifacts", {}).get(artifact_type):
        return Path(state["artifacts"][artifact_type])

    # 2. Glob по стандартным паттернам
    patterns = {
        "prd": "ai-docs/docs/prd/*-prd.md",
        "plan": "ai-docs/docs/architecture/*-plan.md",
        "feature_plan": "ai-docs/docs/plans/*-plan.md",
        "review_report": "ai-docs/docs/reports/review-*.md",
        "qa_report": "ai-docs/docs/reports/qa-*.md",
        "rtm": "ai-docs/docs/rtm.md"
    }

    files = glob(patterns.get(artifact_type, ""))
    if files:
        # Вернуть самый свежий
        return max(files, key=lambda f: f.stat().st_mtime)

    return None
```

### Паттерны поиска

| Артефакт | Паттерн | Суффикс |
|----------|---------|---------|
| PRD | `ai-docs/docs/prd/*-prd.md` | `-prd.md` |
| План архитектуры | `ai-docs/docs/architecture/*-plan.md` | `-plan.md` |
| План фичи | `ai-docs/docs/plans/*-plan.md` | `-plan.md` |
| Отчёт ревью | `ai-docs/docs/reports/review-*.md` | `review-*.md` |
| Отчёт QA | `ai-docs/docs/reports/qa-*.md` | `qa-*.md` |
| RTM | `ai-docs/docs/rtm.md` | — |

---

## Проверка предусловий (Gate Check)

Каждая команда ОБЯЗАНА проверить предусловия перед выполнением:

```python
def check_preconditions(command: str) -> bool:
    """Проверка предусловий перед выполнением команды."""

    preconditions = {
        "/init": [],  # Нет предусловий — первый этап
        "/idea": ["BOOTSTRAP_READY"],  # Авто-bootstrap если не пройден
        "/research": ["PRD_READY"],
        "/plan": ["PRD_READY", "RESEARCH_DONE"],
        "/feature-plan": ["PRD_READY", "RESEARCH_DONE"],
        "/generate": ["PLAN_APPROVED"],
        "/review": ["IMPLEMENT_OK"],
        "/test": ["REVIEW_OK"],
        "/validate": ["QA_PASSED"],
        "/deploy": ["ALL_GATES_PASSED"]
    }

    state = read_json(".pipeline-state.json")
    if not state:
        return command == "/idea"

    for gate in preconditions.get(command, []):
        if not state.get("gates", {}).get(gate, {}).get("passed"):
            print(f"❌ Ворота {gate} не пройдены")
            return False

    return True
```

### Матрица предусловий

| Команда | Требуемые ворота | Если не пройдены |
|---------|-----------------|------------------|
| `/init` | — | — |
| `/idea` | BOOTSTRAP_READY | Авто-запуск bootstrap или "/init" |
| `/research` | PRD_READY | "Сначала выполните /idea" |
| `/plan` | PRD_READY, RESEARCH_DONE | "Сначала выполните /research" |
| `/feature-plan` | PRD_READY, RESEARCH_DONE | "Сначала выполните /research" |
| `/generate` | PLAN_APPROVED | "Сначала утвердите план" |
| `/review` | IMPLEMENT_OK | "Сначала выполните /generate" |
| `/test` | REVIEW_OK | "Сначала выполните /review" |
| `/validate` | QA_PASSED | "Сначала выполните /test" |
| `/deploy` | ALL_GATES_PASSED | "Сначала выполните /validate" |

---

## Правила прохождения ворот

### Алгоритм проверки ворот (P-009)

Каждые ворота проверяются по унифицированному алгоритму:

```python
def check_gate(gate: str) -> GateResult:
    """
    Алгоритм проверки ворот.

    Args:
        gate: Название ворот

    Returns:
        GateResult: {passed: bool, reason: str, checklist: list}
    """
    checklist_map = {
        "BOOTSTRAP_READY": [
            ("git_repo", "git rev-parse --git-dir"),
            ("framework_exists", ".aidd/CLAUDE.md"),
            ("python_version", "python3 --version >= 3.11"),
            ("docker_installed", "docker --version"),
            ("structure_created", "ai-docs/docs/ exists"),
            ("state_initialized", ".pipeline-state.json exists"),
        ],
        "PRD_READY": [
            ("artifact_exists", "ai-docs/docs/prd/*-prd.md"),
            ("sections_complete", ["Обзор", "FR-*", "NF-*"]),
            ("ids_present", "Все требования имеют ID"),
            ("no_blockers", "Нет Open вопросов без решения"),
        ],
        "RESEARCH_DONE": [
            ("analysis_complete", "Код проанализирован"),
            ("patterns_identified", "Паттерны выявлены"),
            ("constraints_defined", "Ограничения определены"),
        ],
        "PLAN_APPROVED": [
            ("artifact_exists", "ai-docs/docs/architecture/*-plan.md"),
            ("components_defined", "Компоненты определены"),
            ("api_contracts", "API контракты описаны"),
            ("user_approved", "Пользователь подтвердил"),  # Требует interaction
        ],
        "IMPLEMENT_OK": [
            ("code_exists", "services/*/"),
            ("tests_pass", "pytest exit code 0"),
            ("types_present", "Type hints в коде"),
            ("structure_ok", "DDD структура соблюдена"),
        ],
        "REVIEW_OK": [
            ("artifact_exists", "ai-docs/docs/reports/review-*.md"),
            ("no_blockers", "Нет Blocker замечаний"),
            ("no_critical", "Нет Critical замечаний"),
        ],
        "QA_PASSED": [
            ("artifact_exists", "ai-docs/docs/reports/qa-*.md"),
            ("tests_pass", "Все тесты проходят"),
            ("coverage_ok", "Coverage >= 75%"),
            ("no_critical_bugs", "Нет Critical/Blocker багов"),
        ],
        "ALL_GATES_PASSED": [
            ("all_previous", "Все предыдущие ворота пройдены"),
            ("artifacts_exist", "Все артефакты существуют"),
            ("rtm_complete", "RTM актуальна"),
        ],
        "DEPLOYED": [
            ("containers_up", "docker-compose ps: all running"),
            ("health_ok", "Health endpoints respond 200"),
            ("logs_clean", "Нет ошибок в логах"),
        ],
    }

    checklist = checklist_map.get(gate, [])
    results = []

    for check_name, check_value in checklist:
        passed = run_check(check_name, check_value)
        results.append((check_name, passed, check_value))

    all_passed = all(r[1] for r in results)
    return GateResult(
        passed=all_passed,
        reason="OK" if all_passed else f"Failed: {[r[0] for r in results if not r[1]]}",
        checklist=results
    )
```

### 1. Блокирующие ворота

AI-агент **НЕ МОЖЕТ** перейти к следующему этапу, если ворота не пройдены.

```
❌ PRD_READY не пройден → /plan заблокирована
❌ PLAN_APPROVED не пройден → /generate заблокирована
```

### 2. Откат и восстановление при неудаче (P-004)

Если ворота не пройдены, AI-агент следует алгоритму восстановления:

```python
def handle_gate_failure(gate: str, reason: str) -> Action:
    """
    Алгоритм обработки непройденных ворот.

    Args:
        gate: Название ворот (PRD_READY, PLAN_APPROVED, etc.)
        reason: Причина неудачи

    Returns:
        Action: Рекомендуемое действие
    """
    recovery_actions = {
        "PRD_READY": {
            "incomplete_sections": "Дополнить недостающие секции PRD",
            "missing_criteria": "Добавить критерии приёмки к требованиям",
            "open_questions": "Уточнить вопросы у пользователя",
        },
        "PLAN_APPROVED": {
            "not_approved": "Запросить подтверждение у пользователя",
            "missing_components": "Дополнить архитектурный план",
        },
        "IMPLEMENT_OK": {
            "tests_failed": "Исправить код и перезапустить тесты",
            "missing_types": "Добавить type hints",
            "structure_error": "Исправить структуру DDD",
        },
        "REVIEW_OK": {
            "critical_issues": "Исправить критические замечания",
            "convention_violations": "Привести код к conventions.md",
        },
        "QA_PASSED": {
            "low_coverage": "Добавить тесты для увеличения coverage",
            "tests_failed": "Исправить падающие тесты",
            "bugs_found": "Исправить найденные баги",
        },
        "ALL_GATES_PASSED": {
            "gates_missing": "Вернуться к непройденному этапу",
        },
        "DEPLOYED": {
            "build_failed": "Исправить Dockerfile/docker-compose",
            "health_failed": "Проверить конфигурацию сервисов",
        },
    }

    return recovery_actions.get(gate, {}).get(reason, "Обратиться к пользователю")
```

**Пример восстановления**:
```
/validate
→ ❌ QA_PASSED: Coverage 68% (требуется ≥75%)
→ Автоматическое действие: Добавить тесты
[AI добавляет тесты]
/test
→ ✓ QA_PASSED: Coverage 76%
/validate
→ ✓ ALL_GATES_PASSED
```

**Принципы восстановления**:
1. **Не пропускать этапы** — вернуться к проблемному этапу
2. **Исправить, не обходить** — устранить причину, а не симптом
3. **Сообщить пользователю** — если автоматическое восстановление невозможно

### 3. Явное подтверждение пользователя

Некоторые ворота требуют явного подтверждения:

| Ворота | Требует подтверждения |
|--------|----------------------|
| `PRD_READY` | Нет (автоматическая проверка) |
| `PLAN_APPROVED` | **ДА** (пользователь должен утвердить план) |
| `REVIEW_OK` | Нет (автоматическая проверка) |
| `QA_PASSED` | Нет (автоматическая проверка) |
| `DEPLOYED` | Нет (автоматическая проверка) |

---

## Разграничение ролей Reviewer и QA (P-005)

Две роли выполняют разные функции в пайплайне:

| Аспект | Ревьюер (Этап 5) | QA (Этап 6) |
|--------|------------------|-------------|
| **Фокус** | Качество кода | Функциональность |
| **Что проверяет** | Архитектура, соглашения, DRY/KISS/YAGNI | Тесты, покрытие, соответствие PRD |
| **Методы** | Статический анализ кода | Выполнение тестов |
| **Артефакт** | `review-report.md` | `qa-report.md` |
| **Ворота** | `REVIEW_OK` | `QA_PASSED` |

### Ревьюер отвечает на:
- Соответствует ли код архитектурному плану?
- Соблюдены ли соглашения conventions.md?
- Есть ли дублирование кода (DRY)?
- Не переусложнён ли код (KISS)?
- Нет ли лишнего функционала (YAGNI)?

### QA отвечает на:
- Все ли тесты проходят?
- Достаточно ли покрытие кода (≥75%)?
- Все ли требования из PRD реализованы и работают?
- Есть ли баги?

**Важно**: Ревью предшествует QA. Сначала проверяем качество кода, потом его функциональность.

---

## Режим FEATURE: Полное описание (P-025)

Режим FEATURE предназначен для добавления функционала в существующий проект.

### Отличия от CREATE

| Аспект | CREATE | FEATURE |
|--------|--------|---------|
| Цель | Новый MVP с нуля | Добавление фичи |
| Этап 2 | Анализ требований | Анализ кода |
| Этап 3 | `/plan` — полная архитектура | `/feature-plan` — план интеграции |
| Артефакты | Новый `ai-docs/` | Интеграция в существующий |
| Тесты | Создание с нуля | Расширение существующих |

### Полный процесс FEATURE

```
Этап 1: /idea "Добавить email уведомления"
├── Аналитик создаёт FEATURE_PRD
├── Фокус на интеграции с существующим функционалом
└── Артефакт: ai-docs/docs/prd/notifications-prd.md

Этап 2: /research
├── Исследователь анализирует СУЩЕСТВУЮЩИЙ код
├── Выявляет точки расширения
├── Определяет зависимости
└── Рекомендации по интеграции

Этап 3: /feature-plan (НЕ /plan!)
├── Архитектор создаёт план ИНТЕГРАЦИИ
├── Учитывает существующие компоненты
├── Минимизирует изменения в существующем коде
└── Артефакт: ai-docs/docs/plans/notifications-plan.md

Этап 4: /generate
├── Реализатор создаёт новый код
├── Интегрирует с существующими сервисами
├── Расширяет, не ломает
└── Новые тесты + обновление существующих

Этапы 5-8: Аналогично CREATE
```

### Пример FEATURE pipeline

```bash
# 1. Запуск в директории существующего проекта
cd booking-service/

# 2. Описываем фичу
/idea "Добавить систему email уведомлений.
При бронировании отправлять подтверждение на email.
При отмене — уведомление об отмене."

# 3. Исследование существующего кода
/research
# Агент анализирует:
# - Структуру сервисов
# - Точки, где нужны уведомления
# - Существующие интеграции

# 4. План фичи (НЕ /plan!)
/feature-plan
# Агент создаёт план интеграции:
# - NotificationService в booking_api
# - Интеграция с BookingService
# - Новый HTTP клиент для email

# 5-8. Генерация, ревью, QA, деплой
/generate
/review
/test
/validate
/deploy
```

### Маркеры режима FEATURE

AI определяет режим FEATURE при наличии:

```
{project}/
├── services/           ← Существующие сервисы
├── docker-compose.yml  ← Инфраструктура
├── ai-docs/docs/       ← Предыдущие артефакты
└── Makefile            ← Сборка
```

---

## Версионирование артефактов (P-028)

При итеративной разработке артефакты могут иметь версии.

### Именование версий

```
ai-docs/docs/prd/
├── booking-prd.md           ← Текущая версия
├── booking-prd-v1.md        ← Архив v1
└── booking-prd-v2.md        ← Архив v2

ai-docs/docs/architecture/
├── booking-plan.md          ← Текущая версия
└── booking-plan-v1.md       ← Архив v1
```

### Когда создавать версию

| Ситуация | Действие |
|----------|----------|
| Изменение требований | Новая версия PRD |
| Редизайн архитектуры | Новая версия плана |
| Значительные изменения | Архивировать старую версию |

### Алгоритм версионирования

```python
def version_artifact(artifact_path: Path) -> Path:
    """
    Создать версию артефакта перед значительным изменением.

    Args:
        artifact_path: Путь к текущему артефакту

    Returns:
        Path к заархивированной версии
    """
    # 1. Определить текущую версию
    versions = glob(f"{artifact_path.stem}-v*.md")
    next_version = len(versions) + 1

    # 2. Создать архивную копию
    archive_name = f"{artifact_path.stem}-v{next_version}.md"
    archive_path = artifact_path.parent / archive_name

    # 3. Скопировать текущий в архив
    shutil.copy(artifact_path, archive_path)

    # 4. Добавить заголовок в архив
    content = archive_path.read_text()
    header = f"<!-- Архивная версия v{next_version}. См. {artifact_path.name} -->\n\n"
    archive_path.write_text(header + content)

    return archive_path
```

### Обновление .pipeline-state.json

```json
{
  "artifacts": {
    "prd": "ai-docs/docs/prd/booking-prd.md",
    "prd_history": [
      "ai-docs/docs/prd/booking-prd-v1.md",
      "ai-docs/docs/prd/booking-prd-v2.md"
    ]
  }
}
```

---

## Связанные документы

| Документ | Описание |
|----------|----------|
| [CLAUDE.md](CLAUDE.md) | Главная точка входа |
| [conventions.md](conventions.md) | Соглашения о коде |
| [.claude/agents/](.claude/agents/) | Определения AI-ролей |
| [.claude/commands/](.claude/commands/) | Определения команд |

---

**Версия документа**: 1.1
**Создан**: 2025-12-19
**Назначение**: Процесс разработки AIDD-MVP Generator
