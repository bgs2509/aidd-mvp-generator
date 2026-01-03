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
│  │/aidd-init │  ─────────────────────────────────────────────────────────── │
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
/aidd-idea "Создать сервис бронирования столиков в ресторанах"
```

### FEATURE — Добавление функционала

Адаптированный процесс для добавления фичи в существующий проект.

```bash
/aidd-idea "Добавить систему уведомлений по email"
```

**Отличия режима FEATURE**:
- Этап 2 (Исследование) — анализ существующего кода
- Этап 3 (Архитектура) — `/aidd-feature-plan` вместо `/aidd-plan`
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

Перед запуском `/aidd-idea` фреймворк должен быть подключен:

```bash
# Если фреймворк ещё не подключен
git submodule add https://github.com/your-org/aidd-mvp-generator.git .aidd
git submodule update --init --recursive
```

### Автоматическая инициализация при `/aidd-idea`

При первом запуске `/aidd-idea` AI-агент выполняет:

> **VERIFY BEFORE ACT**: Перед созданием проверяем существование директорий.

```bash
# 1. VERIFY: Проверить существующую структуру артефактов
if [ -d "ai-docs/docs" ]; then
    existing_count=$(ls -d ai-docs/docs/*/ 2>/dev/null | wc -l)
    echo "✓ Структура ai-docs/docs/ уже существует ($existing_count директорий)"
fi

# 2. ACT: Создать только недостающие директории
for dir in prd architecture plans reports research; do
    [ -d "ai-docs/docs/$dir" ] || mkdir -p "ai-docs/docs/$dir"
done

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
/aidd-idea --mode=FEATURE "Добавить фичу"
```

---

## Этапы процесса

### Этап 0: Bootstrap (Инициализация)

| Параметр | Значение |
|----------|----------|
| **Команда** | `/aidd-init` (ручной) или авто с `/aidd-idea` |
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

> **VERIFY BEFORE ACT**: Перед созданием проверяем существование.

```bash
# 1. VERIFY + ACT: Создать только недостающие директории
for dir in prd architecture plans reports research; do
    [ -d "ai-docs/docs/$dir" ] || mkdir -p "ai-docs/docs/$dir"
done

# 2. Инициализация состояния (если не существует)
[ -f ".pipeline-state.json" ] || echo '{"project_name":"","mode":"CREATE","current_stage":0,"gates":{"BOOTSTRAP_READY":{"passed":true}}}' > .pipeline-state.json

# 3. Создание CLAUDE.md (если не существует)
[ -f "CLAUDE.md" ] || echo "# Project\n\nСм. .aidd/CLAUDE.md" > CLAUDE.md
```

**Примечание**: Этап 0 выполняется автоматически при первом `/aidd-idea`, если проверки
не были пройдены ранее. Явный запуск `/aidd-init` рекомендуется для диагностики.

---

### Этап 1: Идея → PRD

| Параметр | Значение |
|----------|----------|
| **Команда** | `/aidd-idea "описание"` |
| **Агент** | Аналитик |
| **Вход** | Описание идеи от пользователя |
| **Выход** | `ai-docs/docs/prd/{name}-prd.md` |
| **Ворота** | `PRD_READY` |

**Критерии прохождения ворот PRD_READY**:
- [ ] Все секции PRD заполнены
- [ ] Требования имеют ID (FR-*, NF-*, UI-*, INT-*)
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
| **Команда** | `/aidd-research` |
| **Агент** | Исследователь |
| **Вход** | PRD, существующий код (для FEATURE) |
| **Выход** | `ai-docs/docs/research/{name}-research.md` |
| **Ворота** | `RESEARCH_DONE` |

**Критерии прохождения ворот RESEARCH_DONE**:
- [ ] Существующий код проанализирован (для FEATURE)
- [ ] Архитектурные паттерны выявлены и описаны в отчёте
- [ ] Технические ограничения определены
- [ ] Рекомендации по интеграции сформулированы
- [ ] Отчёт исследования сохранён в `ai-docs/docs/research/{name}-research.md`

**Режим CREATE**: Анализ требований, выбор технологий, фиксация гипотез.
**Режим FEATURE**: Анализ кода, выявление точек расширения, фиксация выводов.

**Артефакты** (в целевом проекте):
```
{project-name}/
└── ai-docs/docs/research/
    └── booking-restaurant-research.md
```

---

### Этап 3: Архитектура

| Параметр | Значение |
|----------|----------|
| **Команда** | `/aidd-plan` (CREATE) или `/aidd-feature-plan` (FEATURE) |
| **Агент** | Архитектор |
| **Вход** | PRD, Research Report |
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
| **Команда** | `/aidd-generate` |
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
| **Команда** | `/aidd-review` |
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
| **Команда** | `/aidd-test` |
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
| **Команда** | `/aidd-validate` |
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
| **Команда** | `/aidd-deploy` |
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
| 0 | Bootstrap | `/aidd-init` | — | `BOOTSTRAP_READY` |
| 1 | Идея | `/aidd-idea` | Аналитик | `PRD_READY` |
| 2 | Исследование | `/aidd-research` | Исследователь | `RESEARCH_DONE` |
| 3 | Архитектура | `/aidd-plan` | Архитектор | `PLAN_APPROVED` |
| 4 | Реализация | `/aidd-generate` | Реализатор | `IMPLEMENT_OK` |
| 5 | Ревью | `/aidd-review` | Ревьюер | `REVIEW_OK` |
| 6 | QA | `/aidd-test` | QA | `QA_PASSED` |
| 7 | Валидация | `/aidd-validate` | Валидатор | `ALL_GATES_PASSED` |
| 8 | Деплой | `/aidd-deploy` | Валидатор | `DEPLOYED` |

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
/aidd-idea "Создать сервис бронирования столиков в ресторанах.
Пользователи могут искать рестораны, смотреть свободные столики,
бронировать на определённое время. Рестораны получают уведомления
о новых бронях через Telegram."

# Агент: Аналитик создаёт PRD
# Ворота: PRD_READY ✓

# 2. Исследование
/aidd-research

# Агент: Исследователь анализирует требования
# Ворота: RESEARCH_DONE ✓

# 3. Архитектура
/aidd-plan

# Агент: Архитектор создаёт план
# Пользователь утверждает план
# Ворота: PLAN_APPROVED ✓

# 4. Реализация
/aidd-generate

# Агент: Реализатор генерирует код
# Создаются: infrastructure, data-api, business-api, bot
# Ворота: IMPLEMENT_OK ✓

# 5. Ревью
/aidd-review

# Агент: Ревьюер проверяет код
# Ворота: REVIEW_OK ✓

# 6. QA
/aidd-test

# Агент: QA запускает тесты
# Coverage: 78% ✓
# Ворота: QA_PASSED ✓

# 7. Валидация
/aidd-validate

# Агент: Валидатор проверяет все артефакты
# Ворота: ALL_GATES_PASSED ✓

# 8. Деплой
/aidd-deploy

# Агент: Запускает docker-compose
# Ворота: DEPLOYED ✓

# Готово! MVP запущен за ~10 минут
```

---

## Состояние пайплайна (.pipeline-state.json)

> **Философия**: Артефакты = Память. Состояние пайплайна — единый источник истины.

### Формат файла (v2 — параллельные пайплайны)

Файл `.pipeline-state.json` создаётся в корне ЦЕЛЕВОГО ПРОЕКТА при первом `/aidd-idea`.

```json
{
  "version": "2.0",
  "project_name": "booking-service",
  "mode": "FEATURE",

  "global_gates": {
    "BOOTSTRAP_READY": {"passed": true, "passed_at": "2025-12-25T10:00:00Z"}
  },

  "active_pipelines": {
    "F042": {
      "branch": "feature/F042-oauth-auth",
      "name": "oauth-auth",
      "title": "OAuth авторизация",
      "stage": "IMPLEMENT",
      "created": "2025-12-25",
      "gates": {
        "PRD_READY": {"passed": true, "passed_at": "..."},
        "RESEARCH_DONE": {"passed": true, "passed_at": "..."},
        "PLAN_APPROVED": {"passed": true, "passed_at": "...", "approved_by": "user"}
      },
      "artifacts": {
        "prd": "prd/2025-12-25_F042_oauth-auth-prd.md",
        "research": "research/2025-12-25_F042_oauth-auth-research.md",
        "plan": "plans/2025-12-25_F042_oauth-auth-plan.md"
      }
    }
  },

  "next_feature_id": 43,

  "features_registry": {
    "F001": {"status": "DEPLOYED", "deployed": "2025-12-20"}
  }
}
```

**Ключевые изменения v2**:
- `active_pipelines` — словарь активных фич (вместо `current_feature`)
- `global_gates` — ворота уровня проекта (BOOTSTRAP_READY)
- Ворота изолированы в `active_pipelines[FID].gates`
- `features_registry` — реестр завершённых фич

**Шаблон**: [templates/documents/pipeline-state-template.json](templates/documents/pipeline-state-template.json)
**Спецификация v2**: [knowledge/pipeline/state-v2.md](knowledge/pipeline/state-v2.md)

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
        "research": "ai-docs/docs/research/*-research.md",
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
| Research Report | `ai-docs/docs/research/*-research.md` | `-research.md` |
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
        "/aidd-init": [],  # Нет предусловий — первый этап
        "/aidd-idea": ["BOOTSTRAP_READY"],  # Авто-bootstrap если не пройден
        "/aidd-research": ["PRD_READY"],
        "/aidd-plan": ["PRD_READY", "RESEARCH_DONE"],
        "/aidd-feature-plan": ["PRD_READY", "RESEARCH_DONE"],
        "/aidd-generate": ["PLAN_APPROVED"],
        "/aidd-review": ["IMPLEMENT_OK"],
        "/aidd-test": ["REVIEW_OK"],
        "/aidd-validate": ["QA_PASSED"],
        "/aidd-deploy": ["ALL_GATES_PASSED"]
    }

    state = read_json(".pipeline-state.json")
    if not state:
        return command == "/aidd-idea"

    for gate in preconditions.get(command, []):
        if not state.get("gates", {}).get(gate, {}).get("passed"):
            print(f"❌ Ворота {gate} не пройдены")
            return False

    return True
```

### Матрица предусловий

| Команда | Требуемые ворота | Если не пройдены |
|---------|-----------------|------------------|
| `/aidd-init` | — | — |
| `/aidd-idea` | BOOTSTRAP_READY | Авто-запуск bootstrap или "/aidd-init" |
| `/aidd-research` | PRD_READY | "Сначала выполните /aidd-idea" |
| `/aidd-plan` | PRD_READY, RESEARCH_DONE | "Сначала выполните /aidd-research" |
| `/aidd-feature-plan` | PRD_READY, RESEARCH_DONE | "Сначала выполните /aidd-research" |
| `/aidd-generate` | PLAN_APPROVED | "Сначала утвердите план" |
| `/aidd-review` | IMPLEMENT_OK | "Сначала выполните /aidd-generate" |
| `/aidd-test` | REVIEW_OK | "Сначала выполните /aidd-review" |
| `/aidd-validate` | QA_PASSED | "Сначала выполните /aidd-test" |
| `/aidd-deploy` | ALL_GATES_PASSED | "Сначала выполните /aidd-validate" |

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
            ("artifact_exists", "ai-docs/docs/research/*-research.md"),
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
❌ PRD_READY не пройден → /aidd-plan заблокирована
❌ PLAN_APPROVED не пройден → /aidd-generate заблокирована
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
/aidd-validate
→ ❌ QA_PASSED: Coverage 68% (требуется ≥75%)
→ Автоматическое действие: Добавить тесты
[AI добавляет тесты]
/aidd-test
→ ✓ QA_PASSED: Coverage 76%
/aidd-validate
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
| Этап 3 | `/aidd-plan` — полная архитектура | `/aidd-feature-plan` — план интеграции |
| Артефакты | Новый `ai-docs/` | Интеграция в существующий |
| Тесты | Создание с нуля | Расширение существующих |

### Полный процесс FEATURE

```
Этап 1: /aidd-idea "Добавить email уведомления"
├── Аналитик создаёт FEATURE_PRD
├── Фокус на интеграции с существующим функционалом
└── Артефакт: ai-docs/docs/prd/notifications-prd.md

Этап 2: /aidd-research
├── Исследователь анализирует СУЩЕСТВУЮЩИЙ код
├── Выявляет точки расширения
├── Определяет зависимости
└── Рекомендации по интеграции

Этап 3: /aidd-feature-plan (НЕ /aidd-plan!)
├── Архитектор создаёт план ИНТЕГРАЦИИ
├── Учитывает существующие компоненты
├── Минимизирует изменения в существующем коде
└── Артефакт: ai-docs/docs/plans/notifications-plan.md

Этап 4: /aidd-generate
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
/aidd-idea "Добавить систему email уведомлений.
При бронировании отправлять подтверждение на email.
При отмене — уведомление об отмене."

# 3. Исследование существующего кода
/aidd-research
# Агент анализирует:
# - Структуру сервисов
# - Точки, где нужны уведомления
# - Существующие интеграции

# 4. План фичи (НЕ /aidd-plan!)
/aidd-feature-plan
# Агент создаёт план интеграции:
# - NotificationService в booking_api
# - Интеграция с BookingService
# - Новый HTTP клиент для email

# 5-8. Генерация, ревью, QA, деплой
/aidd-generate
/aidd-review
/aidd-test
/aidd-validate
/aidd-deploy
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

## Параллельные пайплайны (Pipeline State v2)

Фреймворк поддерживает одновременную разработку нескольких фич в отдельных git ветках.

### Концепция

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
│    │  │     └── /aidd-deploy ──────────────▶ DEPLOYED                   │
│    │  │                                                                 │
│    │  └── feature/F043-payments ──────────────────────▶ merge           │
│    │        ├── /aidd-idea      (параллельно с F042!)                  │
│    │        └── ...                                                     │
│    ▼                                                                    │
│  main (с обеими фичами)                                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Именование веток

```
feature/{FID}-{slug}

Примеры:
- feature/F001-table-booking
- feature/F042-oauth-auth
- feature/F043-payments
```

### Определение контекста фичи

AI автоматически определяет текущую фичу по git ветке:

```python
def get_current_feature_context(state: dict) -> tuple[str, dict] | None:
    """
    1. Получить текущую git ветку
    2. Найти FID в active_pipelines по branch
    3. Если одна активная фича — использовать её
    4. Иначе — вернуть None (требуется явное указание)
    """
```

### Изоляция ворот

Каждая фича имеет свои ворота в `active_pipelines[FID].gates`:

```
┌─────────────────────────────────────────────────────────────────┐
│  ВОРОТА: Глобальные vs Локальные                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ГЛОБАЛЬНЫЕ (один раз на проект):                               │
│  └── BOOTSTRAP_READY                                            │
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

### Завершение фичи

После `/aidd-deploy` фича переносится из `active_pipelines` в `features_registry`:

```python
def complete_feature_deploy(state: dict, fid: str):
    """
    1. Отметить DEPLOYED в gates
    2. Перенести в features_registry
    3. Удалить из active_pipelines
    """
```

### Git-хелперы

```bash
# Показать текущий контекст
python3 scripts/git_helpers.py context

# Проверить конфликты между фичами
python3 scripts/git_helpers.py conflicts F042 F043

# Завершить фичу и подготовить к merge
python3 scripts/git_helpers.py merge F042
```

**Документация**: [knowledge/pipeline/git-integration.md](knowledge/pipeline/git-integration.md)

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

**Версия документа**: 1.2
**Создан**: 2025-12-19
**Обновлён**: 2025-12-25
**Назначение**: Процесс разработки AIDD-MVP Generator
