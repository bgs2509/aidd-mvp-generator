# Алгоритм инициализации AI-агента

> **Назначение**: Единый источник истины для порядка чтения файлов при запуске любой команды.
>
> **Принцип**: Сначала понять ГДЕ мы (контекст ЦП), потом КАК действовать (фреймворк).

---

## Обзор

При запуске любой slash-команды (`/idea`, `/research`, `/plan` и т.д.) AI-агент
ОБЯЗАН следовать 4-фазному алгоритму инициализации.

```
┌─────────────────────────────────────────────────────────────────────┐
│              АЛГОРИТМ ИНИЦИАЛИЗАЦИИ AI-АГЕНТА                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ФАЗА 1: Контекст целевого проекта (ЦП)                            │
│  ───────────────────────────────────────                            │
│  1. ./CLAUDE.md              ← Точка входа ЦП                       │
│  2. ./.pipeline-state.json   ← Состояние пайплайна                  │
│  3. ./ai-docs/docs/          ← Существующие артефакты               │
│                                                                     │
│  ФАЗА 2: Проверка предусловий                                       │
│  ─────────────────────────────                                      │
│  4. Проверить требуемые ворота                                      │
│  5. Если не пройдены → сообщить пользователю                        │
│                                                                     │
│  ФАЗА 3: Инструкции фреймворка                                      │
│  ─────────────────────────────                                      │
│  6. .aidd/CLAUDE.md          ← Правила фреймворка                   │
│  7. .aidd/workflow.md        ← Процесс и ворота                     │
│  8. .aidd/.claude/commands/  ← Инструкции команды                   │
│  9. .aidd/.claude/agents/    ← Инструкции роли                      │
│                                                                     │
│  ФАЗА 4: Шаблоны и база знаний (по необходимости)                  │
│  ────────────────────────────────────────────────                   │
│  10. .aidd/templates/documents/  ← Если артефакт не существует       │
│  11. .aidd/knowledge/        ← По теме команды                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Критерии определения источника файла

При выборе откуда читать файл — из ЦП или из Фреймворка — используй эти критерии:

### Таблица критериев

| Критерий | ЦП (`./`) | Фреймворк (`.aidd/`) |
|----------|-----------|---------------------|
| **Содержимое** | Данные ЭТОГО проекта | Универсальные инструкции |
| **Изменяемость** | Меняется AI и пользователем | НЕ меняется (read-only) |
| **Уникальность** | Уникально для проекта | Одинаково для всех проектов |
| **Источник** | Создано в процессе разработки | Шаблон/правило/паттерн |
| **Вопрос** | "ЧТО делаем?" | "КАК делаем?" |

### Алгоритм выбора

```
ЕСЛИ файл отвечает на вопрос:
├── "Какие требования У ЭТОГО проекта?" → ЦП
├── "Какая архитектура У ЭТОГО проекта?" → ЦП
├── "Какой код УЖЕ НАПИСАН?" → ЦП
├── "На каком этапе МЫ сейчас?" → ЦП
│
├── "КАК писать код правильно?" → Фреймворк
├── "КАК структурировать проект?" → Фреймворк
├── "КАКОЙ шаблон использовать?" → Фреймворк
└── "КАКИЕ паттерны применять?" → Фреймворк
```

### Примеры

| Нужно узнать | Источник | Файл |
|--------------|----------|------|
| Требования к фиче X | ЦП | `./ai-docs/docs/prd/X-prd.md` |
| Как писать FastAPI | Фреймворк | `.aidd/knowledge/services/fastapi.md` |
| Какие сервисы уже есть | ЦП | `./services/` |
| Шаблон нового сервиса | Фреймворк | `.aidd/templates/services/` |
| Пройдены ли ворота | ЦП | `./.pipeline-state.json` |
| Какие ворота проверять | Фреймворк | `.aidd/workflow.md` |

### Простое правило

> **ЦП** = Состояние и артефакты проекта (уникальные, изменяемые)
> **Фреймворк** = Инструкции и шаблоны (универсальные, read-only)

---

## Фаза 1: Контекст целевого проекта

AI **СНАЧАЛА** читает файлы целевого проекта, чтобы понять:
- Какой это проект
- На каком этапе находится разработка
- Какие артефакты уже существуют
- Какой режим работы (CREATE или FEATURE)

### 1.1 Чтение ./CLAUDE.md

```python
if exists("./CLAUDE.md"):
    read("./CLAUDE.md")
    # Понять: название проекта, специфические правила, контекст
```

### 1.2 Чтение ./.pipeline-state.json

```python
if exists("./.pipeline-state.json"):
    state = read_json("./.pipeline-state.json")

    mode = state.get("mode")                    # CREATE или FEATURE
    current_stage = state.get("current_stage")  # 1-8
    passed_gates = state.get("gates", {})       # Пройденные ворота
    artifacts = state.get("artifacts", {})      # Пути к артефактам

    # Теперь AI знает полный контекст проекта
else:
    # Новый проект — нужна инициализация
    mode = None
```

### 1.3 Проверка существующих артефактов

```python
existing_artifacts = {
    "prd": glob("./ai-docs/docs/prd/*-prd.md"),
    "plan": glob("./ai-docs/docs/architecture/*-plan.md"),
    "feature_plans": glob("./ai-docs/docs/plans/*-plan.md"),
    "services": exists("./services/"),
    "reports": glob("./ai-docs/docs/reports/*.md"),
}
```

---

## Фаза 2: Проверка предусловий

Каждая команда имеет предусловия — ворота, которые должны быть пройдены.

### Матрица предусловий

| Команда | Требуемые ворота | Если не пройдены |
|---------|-----------------|------------------|
| `/idea` | — | — (первый этап) |
| `/research` | `PRD_READY` | "Сначала выполните /idea" |
| `/plan` | `PRD_READY`, `RESEARCH_DONE` | "Сначала выполните /research" |
| `/feature-plan` | `PRD_READY`, `RESEARCH_DONE` | "Сначала выполните /research" |
| `/generate` | `PLAN_APPROVED` | "Сначала утвердите план" |
| `/review` | `IMPLEMENT_OK` | "Сначала выполните /generate" |
| `/test` | `REVIEW_OK` | "Сначала выполните /review" |
| `/validate` | `QA_PASSED` | "Сначала выполните /test" |
| `/deploy` | `ALL_GATES_PASSED` | "Сначала выполните /validate" |

### Алгоритм проверки

```python
def check_preconditions(command: str) -> bool:
    """
    Проверка предусловий перед выполнением команды.

    Returns:
        True если все ворота пройдены, False иначе
    """
    preconditions = {
        "/idea": [],
        "/research": ["PRD_READY"],
        "/plan": ["PRD_READY", "RESEARCH_DONE"],
        "/feature-plan": ["PRD_READY", "RESEARCH_DONE"],
        "/generate": ["PLAN_APPROVED"],
        "/review": ["IMPLEMENT_OK"],
        "/test": ["REVIEW_OK"],
        "/validate": ["QA_PASSED"],
        "/deploy": ["ALL_GATES_PASSED"],
    }

    state = read_json("./.pipeline-state.json")
    if not state:
        return command == "/idea"  # Только /idea можно без state

    for gate in preconditions.get(command, []):
        if not state.get("gates", {}).get(gate, {}).get("passed"):
            print(f"❌ Ворота {gate} не пройдены")
            print(f"→ {recovery_hint(gate)}")
            return False

    return True
```

---

## Фаза 3: Инструкции фреймворка

**ПОСЛЕ** понимания контекста ЦП, AI читает инструкции фреймворка.

### 3.1 Базовые документы (всегда)

```python
read(".aidd/CLAUDE.md")      # Общие правила фреймворка
read(".aidd/workflow.md")    # Процесс и качественные ворота
```

### 3.2 Инструкции команды и роли (по запросу)

```python
command_file = f".aidd/.claude/commands/{command}.md"
read(command_file)

# Определить роль из команды
role = COMMAND_TO_ROLE[command]
role_file = f".aidd/.claude/agents/{role}.md"
read(role_file)
```

### Сопоставление команд и ролей

| Команда | Роль |
|---------|------|
| `/idea` | analyst |
| `/research` | researcher |
| `/plan` | architect |
| `/feature-plan` | architect |
| `/generate` | implementer |
| `/review` | reviewer |
| `/test` | qa |
| `/validate` | validator |
| `/deploy` | validator |

---

## Фаза 4: Шаблоны и база знаний

Шаблоны и knowledge base читаются **ТОЛЬКО ЕСЛИ НУЖНЫ**.

### 4.1 Шаблоны документов

```python
# Читать шаблон ТОЛЬКО если артефакт не существует
if command == "/idea" and not existing_artifacts["prd"]:
    read(".aidd/templates/documents/prd-template.md")

if command == "/plan" and not existing_artifacts["plan"]:
    read(".aidd/templates/documents/architecture-template.md")
```

### 4.2 База знаний

```python
# Читать по необходимости для конкретной команды
knowledge_map = {
    "/plan": [
        ".aidd/knowledge/architecture/ddd-hexagonal.md",
        ".aidd/knowledge/architecture/http-only.md",
    ],
    "/generate": [
        ".aidd/knowledge/services/fastapi.md",
        ".aidd/knowledge/infrastructure/docker.md",
    ],
    "/review": [
        ".aidd/knowledge/quality/testing.md",
    ],
}

for knowledge_file in knowledge_map.get(command, []):
    read(knowledge_file)
```

---

## Полный алгоритм (псевдокод)

```python
def initialize_context(command: str) -> Context:
    """
    Полный алгоритм инициализации AI-агента.

    Принцип: Сначала ГДЕ мы, потом КАК действовать.

    Args:
        command: Slash-команда (/idea, /research, etc.)

    Returns:
        Context: Полный контекст для выполнения команды
    """
    context = Context()

    # ═══════════════════════════════════════════════════════════════
    # ФАЗА 1: Контекст целевого проекта
    # ═══════════════════════════════════════════════════════════════

    # 1.1 Точка входа ЦП
    if exists("./CLAUDE.md"):
        context.project_info = read("./CLAUDE.md")

    # 1.2 Состояние пайплайна
    if exists("./.pipeline-state.json"):
        context.state = read_json("./.pipeline-state.json")
        context.mode = context.state.get("mode")
        context.current_stage = context.state.get("current_stage")
        context.passed_gates = context.state.get("gates", {})
    else:
        context.mode = None  # Требуется инициализация

    # 1.3 Существующие артефакты
    context.existing_artifacts = {
        "prd": glob("./ai-docs/docs/prd/*-prd.md"),
        "plan": glob("./ai-docs/docs/architecture/*-plan.md"),
        "feature_plans": glob("./ai-docs/docs/plans/*-plan.md"),
        "services": exists("./services/"),
        "reports": glob("./ai-docs/docs/reports/*.md"),
    }

    # ═══════════════════════════════════════════════════════════════
    # ФАЗА 2: Проверка предусловий
    # ═══════════════════════════════════════════════════════════════

    if not check_preconditions(command):
        raise GateNotPassedError(f"Предусловия для {command} не выполнены")

    # ═══════════════════════════════════════════════════════════════
    # ФАЗА 3: Инструкции фреймворка
    # ═══════════════════════════════════════════════════════════════

    # Базовые документы
    context.framework_rules = read(".aidd/CLAUDE.md")
    context.workflow = read(".aidd/workflow.md")

    # Инструкции команды
    context.command_instructions = read(f".aidd/.claude/commands/{command}.md")

    # Инструкции роли
    role = COMMAND_TO_ROLE[command]
    context.role_instructions = read(f".aidd/.claude/agents/{role}.md")

    # ═══════════════════════════════════════════════════════════════
    # ФАЗА 4: Шаблоны и база знаний (по необходимости)
    # ═══════════════════════════════════════════════════════════════

    # Шаблоны — только если артефакт не существует
    template_needed = should_load_template(command, context.existing_artifacts)
    if template_needed:
        context.template = read(template_needed)

    # База знаний — по теме команды
    for knowledge_file in KNOWLEDGE_MAP.get(command, []):
        context.knowledge.append(read(knowledge_file))

    return context
```

---

## Определение режима работы

```python
def detect_mode(state: dict, existing_artifacts: dict) -> str:
    """
    Определение режима работы: CREATE или FEATURE.

    Returns:
        'CREATE' — новый проект с нуля
        'FEATURE' — добавление функционала в существующий проект
    """
    # 1. Приоритет: явное указание в state
    if state and state.get("mode"):
        return state["mode"]

    # 2. Признаки существующего проекта
    project_markers = [
        existing_artifacts.get("services"),     # services/
        exists("./docker-compose.yml"),         # Инфраструктура
        exists("./docker-compose.yaml"),
        bool(existing_artifacts.get("plan")),   # Архитектурный план
    ]

    if any(project_markers):
        return "FEATURE"

    # 3. Дополнительно: много Python файлов
    python_files = list(glob("./**/*.py"))
    if len(python_files) > 5:
        return "FEATURE"

    return "CREATE"
```

---

## Таблица порядка чтения для всех команд

| Команда | Фаза 1 (ЦП) | Фаза 2 | Фаза 3 (Фреймворк) | Фаза 4 |
|---------|-------------|--------|--------------------|---------
| `/idea` | CLAUDE.md, state, ai-docs | — | CLAUDE, workflow, idea.md, analyst.md | prd-template (если PRD нет) |
| `/research` | CLAUDE.md, state, PRD | PRD_READY | CLAUDE, workflow, research.md, researcher.md | knowledge/architecture |
| `/plan` | CLAUDE.md, state, PRD | PRD_READY, RESEARCH_DONE | CLAUDE, workflow, plan.md, architect.md | architecture-template, knowledge/architecture |
| `/feature-plan` | CLAUDE.md, state, PRD, существующая архитектура | PRD_READY, RESEARCH_DONE | CLAUDE, workflow, feature-plan.md, architect.md | — |
| `/generate` | CLAUDE.md, state, план | PLAN_APPROVED | CLAUDE, workflow, generate.md, implementer.md | templates/services, knowledge/services |
| `/review` | CLAUDE.md, state, код | IMPLEMENT_OK | CLAUDE, workflow, review.md, reviewer.md | conventions.md |
| `/test` | CLAUDE.md, state, PRD, код | REVIEW_OK | CLAUDE, workflow, test.md, qa.md | knowledge/quality |
| `/validate` | CLAUDE.md, state, все артефакты | QA_PASSED | CLAUDE, workflow, validate.md, validator.md | — |
| `/deploy` | CLAUDE.md, state, инфраструктура | ALL_GATES_PASSED | CLAUDE, workflow, deploy.md, validator.md | knowledge/infrastructure |

---

## Пример: Инициализация для /idea

```python
# Пользователь запускает: /idea "Создать сервис бронирования"

# ФАЗА 1: Контекст ЦП
if exists("./CLAUDE.md"):
    read("./CLAUDE.md")  # → Понять специфику проекта

if exists("./.pipeline-state.json"):
    state = read_json("./.pipeline-state.json")  # → mode, gates
else:
    state = None  # → Новый проект

artifacts = glob("./ai-docs/docs/prd/*-prd.md")  # → []

# ФАЗА 2: Предусловия
# /idea не требует предусловий — пропуск

# ФАЗА 3: Фреймворк
read(".aidd/CLAUDE.md")
read(".aidd/workflow.md")
read(".aidd/.claude/commands/idea.md")
read(".aidd/.claude/agents/analyst.md")

# ФАЗА 4: Шаблоны
if not artifacts:  # PRD не существует
    read(".aidd/templates/documents/prd-template.md")

# Определение режима
mode = detect_mode(state, {"prd": artifacts, "services": False})
# → mode = "CREATE"

# Bootstrap (только для /idea при mode == None)
mkdir("./ai-docs/docs/{prd,architecture,plans,reports}")
write("./.pipeline-state.json", {"mode": "CREATE", ...})

# Выполнение: создание PRD
create_prd("./ai-docs/docs/prd/booking-prd.md")
```

---

## Пример: Инициализация для /generate (середина пайплайна)

```python
# Пользователь запускает: /generate

# ФАЗА 1: Контекст ЦП
read("./CLAUDE.md")  # → "Booking Service"
state = read_json("./.pipeline-state.json")
# → mode: "CREATE", stage: 4, gates: {PRD_READY: ✓, RESEARCH_DONE: ✓, PLAN_APPROVED: ✓}

plan = read(state["artifacts"]["plan"])  # → Архитектурный план

# ФАЗА 2: Предусловия
assert state["gates"]["PLAN_APPROVED"]["passed"]  # ✓

# ФАЗА 3: Фреймворк
read(".aidd/CLAUDE.md")
read(".aidd/workflow.md")
read(".aidd/.claude/commands/generate.md")
read(".aidd/.claude/agents/implementer.md")
read(".aidd/conventions.md")

# ФАЗА 4: Шаблоны и знания
read(".aidd/templates/services/fastapi_business_api/")
read(".aidd/templates/services/postgres_data_api/")
read(".aidd/templates/infrastructure/docker/")
read(".aidd/knowledge/services/fastapi.md")

# Выполнение: генерация кода
generate_services(plan)
```

---

## Связанные документы

| Документ | Описание |
|----------|----------|
| [CLAUDE.md](../CLAUDE.md) | Главная точка входа фреймворка |
| [workflow.md](../workflow.md) | 8-этапный процесс и ворота |
| [NAVIGATION.md](NAVIGATION.md) | Навигационная матрица по этапам |
| [target-project-structure.md](target-project-structure.md) | Структура целевого проекта |

---

**Версия**: 1.0
**Создан**: 2025-12-21
**Назначение**: Единый источник истины для алгоритма инициализации AI-агента
