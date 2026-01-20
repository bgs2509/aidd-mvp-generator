# workflow.md — Процесс разработки AIDD-MVP

**Примечание (Migration Mode v2.4):** Фреймворк поддерживает обе версии команд — legacy naming (`/aidd-idea`, `/aidd-generate`, `/aidd-finalize`, `/aidd-feature-plan`) и new naming (`/aidd-analyze`, `/aidd-code`, `/aidd-validate`, `/aidd-plan-feature`) работают идентично.


> **Назначение**: Описание 6-этапного процесса разработки MVP (этапы 0-5).
> AI-агент ОБЯЗАН следовать этому процессу и проходить качественные ворота.
>
> **Философия**: Артефакты = Память. Не полагаемся на память чата.

---

## Обзор процесса

AIDD-MVP Generator использует 6-этапный конвейер разработки (Этапы 0-5)
с обязательными качественными воротами между этапами. Переход на следующий
этап возможен ТОЛЬКО после прохождения ворот текущего этапа.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AIDD-MVP DEVELOPMENT PIPELINE (v2.0)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────┐                                                               │
│  │ BOOTSTRAP │  Этап 0: Инициализация целевого проекта                      │
│  │/aidd-init │  ─────────────────────────────────────────────────────────── │
│  └─────┬─────┘                                                               │
│        │ BOOTSTRAP_READY                                                     │
│        ▼                                                                     │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────────────┐             │
│  │  ИДЕЯ   │───▶│ИССЛЕДО- │───▶│АРХИТЕК- │───▶│   РЕАЛИЗА-   │             │
│  │         │    │ ВАНИЕ   │    │  ТУРА   │    │     ЦИЯ       │             │
│  └────┬────┘    └────┬────┘    └────┬────┘    └──────┬───────┘             │
│       │              │              │                 │                     │
│  ┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌──────▼───────┐             │
│  │PRD_READY│    │RESEARCH │    │  PLAN   │    │  IMPLEMENT   │             │
│  │         │    │  RESEARCH_DONE  │    │APPROVED │    │     IMPLEMENT_OK      │             │
│  └─────────┘    └─────────┘    └─────────┘    └──────────────┘             │
│                                      ⚠️                                      │
│                              Требует подтверждения                           │
│                                пользователя!                                 │
│                                                                              │
│                                     ▼                                        │
│  ┌───────────────────────────────────────────────────────────────┐          │
│  │            QUALITY & DEPLOY (/aidd-finalize)                  │          │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────────────┐      │          │
│  │  │ Review │─▶│  Test  │─▶│Validate│─▶│Deploy + Report │      │          │
│  │  └────┬───┘  └────┬───┘  └────┬───┘  └────┬───────────┘      │          │
│  │       │           │           │            │                  │          │
│  │  REVIEW_OK    QA_PASSED  ALL_GATES     DEPLOYED              │          │
│  │                                 PASSED                        │          │
│  └───────────────────────────────────────────────────────────────┘          │
│                                                                              │
│  Артефакт: 1 Completion Report (вместо 4 файлов)                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Два режима работы

### CREATE — Создание нового MVP

Полный 6-этапный процесс (этапы 0-5) для создания проекта с нуля.

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

# 2. Инициализация состояния пайплайна (v2 формат)
cat > .pipeline-state.json << 'EOF'
{
  "version": "2.0",
  "project_name": "",
  "mode": "CREATE",
  "global_gates": {
    "BOOTSTRAP_READY": { "passed": true, "passed_at": null }
  },
  "active_pipelines": {},
  "features_registry": {},
  "next_feature_id": 1
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

# 2. Инициализация состояния (если не существует, v2 формат)
[ -f ".pipeline-state.json" ] || echo '{"version":"2.0","project_name":"","mode":"CREATE","global_gates":{"BOOTSTRAP_READY":{"passed":true}},"active_pipelines":{},"next_feature_id":1}' > .pipeline-state.json

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
- [ ] HTTP-only: бизнес-сервисы НЕ обращаются к БД напрямую (только через Data API)
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

### Этап 5: Quality & Deploy

**Команда**: `/aidd-finalize` (или `/aidd-validate` в v2.4+)
**Роль**: Валидатор (`.claude/agents/validator.md`)
**Предусловие**: `IMPLEMENT_OK` ✓
**Артефакт**: `ai-docs/docs/reports/{YYYY-MM-DD}_{FID}_{slug}-completion.md`

#### Описание

Этап Quality & Deploy выполняет полный цикл проверки качества и деплоя в 4 последовательных шага:

```
┌──────────────────────────────────────────────────────────────┐
│  Шаг 1: Code Review                                          │
│  ├─ Архитектура (DDD, HTTP-only)                             │
│  ├─ Quality Cascade (QC-1...QC-17)                           │
│  ├─ Log-Driven Design                                        │
│  └─ Security checklist                                       │
│  → Ворота: REVIEW_OK ✓                                       │
├──────────────────────────────────────────────────────────────┤
│  Шаг 2: Testing                                              │
│  ├─ Запуск pytest с coverage                                 │
│  ├─ Проверка покрытия ≥75%                                   │
│  └─ Верификация требований FR-*                              │
│  → Ворота: QA_PASSED ✓                                       │
├──────────────────────────────────────────────────────────────┤
│  Шаг 3: Validation                                           │
│  ├─ Проверка всех ворот (PRD_READY...QA_PASSED)              │
│  ├─ Верификация артефактов                                   │
│  └─ Финальная проверка security                              │
│  → Ворота: ALL_GATES_PASSED ✓                                │
├──────────────────────────────────────────────────────────────┤
│  Шаг 4: Deploy & Completion Report                           │
│  ├─ docker-compose build                                     │
│  ├─ docker-compose up                                        │
│  ├─ Health-check                                             │
│  ├─ Базовые сценарии                                         │
│  ├─ СОЗДАНИЕ COMPLETION REPORT (обязательно!)                │
│  └─ Перенос в features_registry                              │
│  → Ворота: DEPLOYED ✓                                        │
└──────────────────────────────────────────────────────────────┘
```

#### Два режима работы

| Режим | Когда использовать | Ворота |
|-------|-------------------|--------|
| **Полный** (рекомендуется) | Production-ready MVP | `REVIEW_OK` → `QA_PASSED` → `ALL_GATES_PASSED` → `DEPLOYED` |
| **Быстрый** | Документация, застопорившаяся фича | `DOCUMENTED` (только static analysis) |

**Быстрый режим**:
- Выполняет только mypy, ruff, bandit (без тестов)
- Создаёт DRAFT Completion Report с пометкой "⚠️ DRAFT — QA не выполнено"
- Фича остаётся в `active_pipelines` (НЕ переносится в `features_registry`)
- Позволяет переключиться на другую фичу без завершения текущей

#### Библиотеки инструкций

Валидатор использует две вспомогательные библиотеки:

| Библиотека | Файл | Содержимое |
|------------|------|-----------|
| **Code Review** | `.claude/agents/code-review-library.md` | Quality Cascade (17 проверок), Log-Driven Design, Security |
| **Testing** | `.claude/agents/testing-library.md` | Тестовые сценарии, Coverage, Верификация требований |

#### Completion Report

Единственный артефакт этапа Quality & Deploy. Содержит:

- Executive Summary
- Code Review Summary (результаты 17 проверок)
- Testing Summary (coverage, требования)
- Requirements Traceability (соответствие FR-*)
- ADR (архитектурные решения)
- Scope Changes (план vs факт)
- Known Limitations
- Метрики качества

**Путь**: `ai-docs/docs/reports/{YYYY-MM-DD}_{FID}_{slug}-completion.md`

#### Команды

```bash
# Полный режим (рекомендуется)
/aidd-finalize

# Быстрый режим (явное указание)
/aidd-finalize --mode=quick

# Alias (v2.4+)
/aidd-validate
```

#### Детальные инструкции

См. `.claude/commands/aidd-finalize.md` → секции по каждому шагу.

---

## Таблица команд и ворот

| # | Этап | Команда (старая → новая) | Агент | Ворота | Артефакт (v2 → v3) |
|---|------|--------------------------|-------|--------|-------------------|
| 0 | Bootstrap | `/aidd-init` | — | `BOOTSTRAP_READY` | Структура ЦП |
| 1 | Идея | `/aidd-idea` → `/aidd-analyze` | Аналитик | `PRD_READY` | `prd/{name}-prd.md` → `_analysis/{name}.md` |
| 2 | Исследование | `/aidd-research` | Исследователь | `RESEARCH_DONE` | `research/{name}-research.md` → `_research/{name}.md` |
| 3 | Архитектура (CREATE) | `/aidd-plan` | Архитектор → Планировщик | `PLAN_APPROVED` | `architecture/{name}-plan.md` → `_plans/mvp/{name}.md` |
| 3 | Архитектура (FEATURE) | `/aidd-feature-plan` → `/aidd-plan-feature` | Архитектор → Планировщик | `PLAN_APPROVED` | `plans/{feature}-plan.md` → `_plans/features/{name}.md` |
| 4 | Реализация | `/aidd-generate` → `/aidd-code` | Реализатор → Программист | `IMPLEMENT_OK` | `services/`, тесты |
| 5 | Quality & Deploy | `/aidd-finalize` → `/aidd-validate` | Валидатор | **Full**: `REVIEW_OK`, `QA_PASSED`, `ALL_GATES_PASSED`, `DEPLOYED` <br> **Quick**: `DOCUMENTED` | `reports/{name}-completion.md` → `_validation/{name}.md` |

> **Migration Mode (v2.4+)**: Все команды доступны в двух вариантах — обе работают одинаково. Артефакты создаются в разных папках в зависимости от `naming_version` в `.pipeline-state.json`.
>
> **Примечание**: `/aidd-finalize` (или `/aidd-validate`) поддерживает два режима:
> - **Полный (рекомендуется)**: Review → Test → Validate → Deploy → Production-ready MVP
> - **Быстрый**: Только DRAFT Completion Report + Static Analysis → для документации или незавершённых фич
>
> Файлы команд: [docs/INDEX.md](docs/INDEX.md#slash-команды)


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
    ├── research/
    │   └── {name}-research.md       # Этап 2: Research Report
    │
    ├── architecture/
    │   └── {name}-plan.md           # Этап 3: Архитектурный план (CREATE)
    │
    ├── plans/
    │   └── {feature}-plan.md        # Этап 3: План фичи (FEATURE)
    │
    └── reports/
        └── {date}_{FID}_{slug}-completion.md  # Этап 5: Единый Completion Report
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

# 5. Quality & Deploy
/aidd-finalize

# Агент: Валидатор выполняет 4 шага
# ✓ Step 1/4: Code Review → REVIEW_OK
# ✓ Step 2/4: Testing (Coverage 82%) → QA_PASSED
# ✓ Step 3/4: Validation → ALL_GATES_PASSED
# ✓ Step 4/4: Deploy + Completion Report → DEPLOYED
# ✓ Completion Report: ai-docs/docs/reports/2025-12-23_F001_table-booking-completion.md

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
        "/aidd-finalize": ["IMPLEMENT_OK"],  # Full mode - требует реализации
        # Quick mode (/aidd-finalize --quick) - без предусловий
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
| `/aidd-finalize` (Full) | IMPLEMENT_OK | "Сначала выполните /aidd-generate" |
| `/aidd-finalize` (Quick) | — | Создаёт DRAFT отчёт без предусловий |

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
/aidd-finalize
→ ❌ Step 2/4: Testing failed (Coverage 68%, требуется ≥75%)
→ Автоматическое действие: Добавить тесты
[AI добавляет тесты]
/aidd-finalize
→ ✓ Step 2/4: Testing passed (Coverage 76%)
→ ✓ Step 3/4: Validation → ALL_GATES_PASSED
→ ✓ Step 4/4: Deploy → DEPLOYED
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

# 4-5. Генерация и финализация
/aidd-generate
/aidd-finalize
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
│    │  │     └── /aidd-finalize ───────────▶ DEPLOYED                   │
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

После `/aidd-finalize` фича переносится из `active_pipelines` в `features_registry`:

```python
def complete_feature_deploy(state: dict, fid: str):
    """
    1. Отметить DEPLOYED в gates
    2. Создать Completion Report (итоговый документ)
    3. Добавить путь к completion в artifacts
    4. Перенести в features_registry
    5. Удалить из active_pipelines
    """
```

> **Completion Report** — единый документ, который AI ОБЯЗАН читать при работе
> с deployed фичами. Содержит: ADR, scope changes, known limitations, метрики.
> **Путь**: `reports/{date}_{FID}_{slug}-completion.md`

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
