# placeholder: Исправление проблем документации AIDD-MVP Generator

**Дата создания**: 2025-12-21
**Источник**: [2025-12-20-documentation-problems.md](2025-12-20-documentation-problems.md)
**Статус**: В работе
**Всего проблем**: 36

---

## Прогресс

| Приоритет | Всего | Решено | Прогресс |
|-----------|-------|--------|----------|
| 🔴 CRITICAL | 13 | 0 | ░░░░░░░░░░ 0% |
| 🟠 HIGH | 10 | 0 | ░░░░░░░░░░ 0% |
| 🟡 MEDIUM | 9 | 0 | ░░░░░░░░░░ 0% |
| 🟢 LOW | 4 | 0 | ░░░░░░░░░░ 0% |
| **ИТОГО** | **36** | **0** | ░░░░░░░░░░ **0%** |

---

## 🔴 CRITICAL: Критические проблемы (13)

### [ ] P-001: Несуществующие директории для артефактов

**Приоритет**: 🔴 CRITICAL
**Тип**: Целостность структуры
**Блокирует**: P-002, P-022

#### Проблема
Документация ссылается на директории, которые не существуют:
- `docs/prd/`
- `docs/architecture/`
- `docs/plans/`
- `docs/reports/`
- `docs/tasklists/`

#### Решение

**Шаг 1**: Создать структуру директорий
```bash
mkdir -p docs/prd
mkdir -p docs/architecture
mkdir -p docs/plans
mkdir -p docs/reports
mkdir -p docs/tasklists
```

**Шаг 2**: Создать .gitkeep для сохранения в git
```bash
touch docs/prd/.gitkeep
touch docs/architecture/.gitkeep
touch docs/plans/.gitkeep
touch docs/reports/.gitkeep
touch docs/tasklists/.gitkeep
```

**Шаг 3**: Создать README.md в каждой директории
```markdown
# docs/prd/README.md
Директория для PRD документов. Создаются командой /idea.
Шаблон: ../templates/prd-template.md

# docs/architecture/README.md
Директория для архитектурных планов. Создаются командой /plan.
Шаблон: ../templates/architecture-template.md

# docs/plans/README.md
Директория для планов фич. Создаются командой /feature-plan.

# docs/reports/README.md
Директория для отчётов (review, qa, validation).
Шаблоны: ../templates/qa-report-template.md

# docs/tasklists/README.md
Директория для списков задач.
Шаблон: ../templates/tasklist-template.md
```

#### Файлы для изменения
- [ ] Создать `docs/prd/README.md`
- [ ] Создать `docs/architecture/README.md`
- [ ] Создать `docs/plans/README.md`
- [ ] Создать `docs/reports/README.md`
- [ ] Создать `docs/tasklists/README.md`

#### Проверка
```bash
ls -la docs/prd/ docs/architecture/ docs/plans/ docs/reports/ docs/tasklists/
```

---

### [ ] P-002: Неправильный путь к шаблону PRD

**Приоритет**: 🔴 CRITICAL
**Тип**: Битая ссылка
**Зависит от**: P-001

#### Проблема
Агент Аналитик ссылается на `docs/prd/template.md`, но файл находится в `templates/documents/prd-template.md`.

#### Решение

**Вариант A** (рекомендуется): Исправить ссылки в документах

**Шаг 1**: Обновить `.claude/agents/analyst.md`
```markdown
# Было:
| `docs/prd/template.md` | Шаблон PRD |

# Стало:
| `templates/documents/prd-template.md` | Шаблон PRD |
```

**Шаг 2**: Обновить `docs/history/2025-12-19-aidd-mvp-framework-plan.md`
```markdown
# Найти и заменить:
docs/prd/template.md → templates/documents/prd-template.md
```

**Шаг 3**: Обновить `docs/history/2025-12-19-aidd-mvp-implementation-todo.md`
```markdown
# Найти и заменить:
docs/prd/template.md → templates/documents/prd-template.md
```

#### Файлы для изменения
- [ ] `.claude/agents/analyst.md` — строка 136
- [ ] `docs/history/2025-12-19-aidd-mvp-framework-plan.md`
- [ ] `docs/history/2025-12-19-aidd-mvp-implementation-todo.md`

#### Проверка
```bash
grep -r "docs/prd/template.md" --include="*.md"
# Должно вернуть пустой результат
```

---

### [ ] P-003: Конфликт инструментов между агентами и командами

**Приоритет**: 🔴 CRITICAL
**Тип**: Конфликт документов
**Связан с**: P-010

#### Проблема
Агенты и команды объявляют разные наборы инструментов для одних ролей.

#### Решение

**Принцип**: Команды определяют ОГРАНИЧЕНИЯ, агенты определяют ВОЗМОЖНОСТИ.
Итоговые права = пересечение (команда ∩ агент).

**Шаг 1**: Создать таблицу соответствия в `CLAUDE.md`

```markdown
## Модель разрешений инструментов

| Роль | Агент (возможности) | Команда (ограничения) | Итоговые права |
|------|---------------------|----------------------|----------------|
| Аналитик | Read, Glob, Grep, Edit, Write | Edit(**/*.md), Write(**/*.md) | Только .md файлы |
| Реализатор | Read, Glob, Grep, Edit, Write, Bash | Bash(make/docker/pytest) | Ограниченный Bash |
| QA | Read, Glob, Grep, Bash, Edit, Write | Bash(pytest/make), Edit/Write(**/*.md) | Только тесты и md |
```

**Шаг 2**: Обновить `.claude/agents/analyst.md`
```markdown
## Инструменты

| Инструмент | Назначение | Ограничения |
|------------|-----------|-------------|
| Read | Чтение файлов | Все файлы |
| Glob | Поиск файлов | Все паттерны |
| Grep | Поиск в содержимом | Все файлы |
| Edit | Редактирование | **Только .md файлы** |
| Write | Создание файлов | **Только .md файлы** |

> **Примечание**: Конкретные ограничения определяются в соответствующей команде.
```

**Шаг 3**: Добавить в каждую команду секцию "Разрешения"
```markdown
## Разрешения инструментов

Эта команда разрешает следующие инструменты:
- `Edit(**/*.md)` — редактирование markdown файлов
- `Write(**/*.md)` — создание markdown файлов
- ...

> Полный список возможностей агента: `.claude/agents/{role}.md`
```

#### Файлы для изменения
- [ ] `CLAUDE.md` — добавить секцию "Модель разрешений"
- [ ] `.claude/agents/analyst.md` — уточнить ограничения
- [ ] `.claude/agents/coder.md` — уточнить ограничения
- [ ] `.claude/agents/qa.md` — уточнить ограничения
- [ ] `.claude/commands/idea.md` — добавить секцию разрешений
- [ ] `.claude/commands/generate.md` — добавить секцию разрешений
- [ ] `.claude/commands/test.md` — добавить секцию разрешений

#### Проверка
Просмотреть все файлы и убедиться в согласованности.

---

### [ ] P-004: Отсутствие алгоритма отката при неудаче ворот

**Приоритет**: 🔴 CRITICAL
**Тип**: Неполнота пайплайна
**Связан с**: P-009, P-020

#### Проблема
Нет чёткого алгоритма, что делать при провале качественных ворот.

#### Решение

**Шаг 1**: Добавить секцию "Алгоритм отката" в `workflow.md`

```markdown
## Алгоритм отката при неудаче ворот

### Матрица влияния изменений

| Изменение | Инвалидирует ворота |
|-----------|---------------------|
| Изменён PRD | RESEARCH_DONE, PLAN_APPROVED, IMPLEMENT_OK, REVIEW_OK, QA_PASSED |
| Изменён план | IMPLEMENT_OK, REVIEW_OK, QA_PASSED |
| Изменён код | REVIEW_OK, QA_PASSED |
| Изменены тесты | QA_PASSED |

### Процедура отката

1. **Определить провалившиеся ворота**
   ```
   /validate → Список непройденных ворот
   ```

2. **Определить минимальный откат**
   - Если провал QA_PASSED → вернуться к /test
   - Если провал REVIEW_OK → вернуться к /review
   - Если провал IMPLEMENT_OK → вернуться к /generate
   - Если изменился PRD → полный перезапуск с /research

3. **Выполнить исправления**
   ```
   # Пример: провал QA_PASSED (coverage 68%)
   /test                    # Добавить недостающие тесты
   /validate                # Перепроверить все ворота
   ```

4. **Правило инвалидации**
   Любое изменение кода автоматически инвалидирует:
   - REVIEW_OK (требуется повторное ревью)
   - QA_PASSED (требуется перезапуск тестов)

### Пример полного отката

```
Сценарий: Coverage упал до 68%

1. /validate → ❌ QA_PASSED: Coverage 68%
2. Анализ: нужны дополнительные тесты
3. /test → Добавлены тесты → Coverage 78%
4. /validate → ✅ QA_PASSED: Coverage 78%
             → ⚠️ REVIEW_OK: код изменился
5. /review → Проверка новых тестов → ✅ REVIEW_OK
6. /validate → ✅ Все ворота пройдены
```
```

#### Файлы для изменения
- [ ] `workflow.md` — добавить секцию "Алгоритм отката"
- [ ] `.claude/commands/validate.md` — добавить логику инвалидации

#### Проверка
Прочитать обновлённый workflow.md и убедиться в понятности алгоритма.

---

### [ ] P-019: Отсутствие индекса/реестра файлов проекта

**Приоритет**: 🔴 CRITICAL
**Тип**: Целостность пайплайна
**Блокирует**: P-021

#### Проблема
Нет индексного файла со списком всех файлов и их назначением.

#### Решение

**Шаг 1**: Создать `docs/INDEX.md`

```markdown
# Индекс файлов AIDD-MVP Generator

> Полный список файлов проекта с описанием назначения.
> Обновлено: {дата}

## Структура проекта

### Корневые файлы

| Файл | Назначение | Читать когда |
|------|-----------|--------------|
| `CLAUDE.md` | Точка входа для AI | Первым |
| `conventions.md` | Соглашения о коде | При написании кода |
| `workflow.md` | 8-этапный процесс | При планировании |
| `README.md` | Общая документация | Для понимания проекта |

### .claude/agents/

| Файл | Роль | Этапы |
|------|------|-------|
| `analyst.md` | Аналитик | 1 |
| `researcher.md` | Исследователь | 2 |
| `planner.md` | Архитектор | 3 |
| `coder.md` | Реализатор | 4 |
| `reviewer.md` | Ревьюер | 5 |
| `qa.md` | QA инженер | 6 |
| `validator.md` | Валидатор | 7, 8 |

### .claude/commands/

| Файл | Команда | Агент | Этап |
|------|---------|-------|------|
| `idea.md` | /idea | Аналитик | 1 |
| `research.md` | /research | Исследователь | 2 |
| `plan.md` | /plan | Архитектор | 3 (CREATE) |
| `feature-plan.md` | /feature-plan | Архитектор | 3 (FEATURE) |
| `generate.md` | /generate | Реализатор | 4 |
| `review.md` | /review | Ревьюер | 5 |
| `test.md` | /test | QA | 6 |
| `validate.md` | /validate | Валидатор | 7 |
| `deploy.md` | /deploy | Валидатор | 8 |

### templates/documents/

| Файл | Используется в | Создаётся командой |
|------|----------------|-------------------|
| `prd-template.md` | docs/prd/*.md | /idea |
| `architecture-template.md` | docs/architecture/*.md | /plan |
| `qa-report-template.md` | docs/reports/qa-*.md | /test |
| `tasklist-template.md` | docs/tasklists/*.md | /plan, /feature-plan |

### knowledge/

| Директория | Содержимое | Используется |
|------------|-----------|--------------|
| `architecture/` | DDD, Hexagonal | Архитектором |
| `services/` | FastAPI, Aiogram, Workers | Реализатором |
| `integrations/` | HTTP, Redis | Реализатором |
| `infrastructure/` | Docker, Nginx | Реализатором |
| `quality/` | Тестирование | QA |

### templates/services/

| Директория | Тип сервиса | Порт |
|------------|-------------|------|
| `fastapi_business_api/` | Business API | 8000-8099 |
| `aiogram_bot/` | Telegram Bot | — |
| `asyncio_worker/` | Background Worker | — |
| `postgres_data_api/` | Data API (PostgreSQL) | 8001 |
| `mongo_data_api/` | Data API (MongoDB) | 8002 |

## Карта зависимостей

```
CLAUDE.md
    ├── → conventions.md
    ├── → workflow.md
    │       ├── → .claude/commands/*.md
    │       └── → .claude/agents/*.md
    │               └── → roles/*/*.md
    ├── → knowledge/*/*.md
    └── → templates/*
            └── → shared/
```
```

#### Файлы для создания
- [ ] `docs/INDEX.md`

#### Проверка
```bash
cat docs/INDEX.md | head -50
```

---

### [ ] P-020: Нет механизма передачи состояния между этапами

**Приоритет**: 🔴 CRITICAL
**Тип**: Целостность пайплайна
**Связан с**: P-004, P-009

#### Проблема
Философия "Артефакты = Память" заявлена, но не реализована.

#### Решение

**Шаг 1**: Создать файл состояния пайплайна

```bash
# Создать шаблон
touch templates/documents/pipeline-state-template.md
```

**Шаг 2**: Определить формат `.pipeline-state.json`

```json
{
  "project_name": "booking-service",
  "mode": "CREATE",
  "current_stage": 4,
  "started_at": "2025-12-21T10:00:00Z",
  "updated_at": "2025-12-21T12:30:00Z",

  "gates": {
    "PRD_READY": {
      "passed": true,
      "passed_at": "2025-12-21T10:15:00Z",
      "artifact": "docs/prd/booking-prd.md"
    },
    "RESEARCH_DONE": {
      "passed": true,
      "passed_at": "2025-12-21T10:30:00Z",
      "artifact": null
    },
    "PLAN_APPROVED": {
      "passed": true,
      "passed_at": "2025-12-21T11:00:00Z",
      "artifact": "docs/architecture/booking-plan.md",
      "approved_by": "user"
    },
    "IMPLEMENT_OK": {
      "passed": false,
      "artifact": null
    },
    "REVIEW_OK": { "passed": false },
    "QA_PASSED": { "passed": false },
    "ALL_GATES_PASSED": { "passed": false },
    "DEPLOYED": { "passed": false }
  },

  "artifacts": {
    "prd": "docs/prd/booking-prd.md",
    "plan": "docs/architecture/booking-plan.md",
    "services": []
  },

  "artifact_hashes": {
    "docs/prd/booking-prd.md": "sha256:abc123...",
    "docs/architecture/booking-plan.md": "sha256:def456..."
  }
}
```

**Шаг 3**: Добавить инструкции по работе с состоянием в каждую команду

```markdown
## Работа с состоянием пайплайна

### Чтение состояния
1. Прочитать `.pipeline-state.json`
2. Проверить `current_stage` и `gates`
3. Найти артефакты в `artifacts`

### Обновление состояния
После успешного завершения этапа:
1. Обновить `current_stage`
2. Установить `gates.{GATE_NAME}.passed = true`
3. Записать путь к артефакту в `artifacts`
4. Вычислить и сохранить хеш артефакта

### Проверка инвалидации
Перед началом этапа:
1. Проверить хеши артефактов-зависимостей
2. Если хеш изменился → инвалидировать зависимые ворота
```

**Шаг 4**: Обновить workflow.md

```markdown
## Состояние пайплайна

Состояние хранится в файле `.pipeline-state.json` в корне проекта.

### Инициализация
При первом запуске `/idea` создаётся файл состояния:
- `mode`: CREATE или FEATURE
- `project_name`: имя из PRD
- Все ворота = false

### Обновление
Каждая команда обновляет состояние после успешного завершения.

### Инвалидация
При изменении артефакта автоматически инвалидируются зависимые ворота.
```

#### Файлы для создания/изменения
- [ ] Создать `templates/documents/pipeline-state-template.json`
- [ ] Обновить `workflow.md` — добавить секцию о состоянии
- [ ] Обновить `.claude/commands/idea.md` — создание state
- [ ] Обновить все команды — чтение/запись state

#### Проверка
```bash
cat templates/documents/pipeline-state-template.json | jq .
```

---

### [ ] P-021: Нет алгоритма обнаружения входных артефактов

**Приоритет**: 🔴 CRITICAL
**Тип**: Неполнота пайплайна
**Зависит от**: P-019, P-020

#### Проблема
Команды требуют входные артефакты, но не определяют алгоритм их поиска.

#### Решение

**Шаг 1**: Добавить секцию "Обнаружение артефактов" в `workflow.md`

```markdown
## Алгоритм обнаружения артефактов

### Источники (в порядке приоритета)

1. **Файл состояния** (приоритет 1)
   ```
   .pipeline-state.json → artifacts.{type}
   ```

2. **Glob-паттерны** (приоритет 2)
   ```
   PRD: docs/prd/*-prd.md
   План: docs/architecture/*-plan.md
   План фичи: docs/plans/*-plan.md
   Отчёт QA: docs/reports/qa-*.md
   ```

3. **Последний по дате** (при множественных совпадениях)
   ```
   Если найдено несколько файлов → взять самый новый
   ```

### Псевдокод обнаружения

```python
def find_artifact(artifact_type: str) -> Path | None:
    # 1. Проверить state file
    state = read_json(".pipeline-state.json")
    if state and state.artifacts.get(artifact_type):
        path = Path(state.artifacts[artifact_type])
        if path.exists():
            return path

    # 2. Glob по известным паттернам
    patterns = {
        "prd": "docs/prd/*-prd.md",
        "plan": "docs/architecture/*-plan.md",
        "feature_plan": "docs/plans/*-plan.md",
        "qa_report": "docs/reports/qa-*.md"
    }

    if artifact_type in patterns:
        files = glob(patterns[artifact_type])
        if files:
            return max(files, key=lambda f: f.stat().st_mtime)

    # 3. Не найден
    return None
```

### Таблица артефактов по этапам

| Этап | Команда | Входные артефакты | Выходные артефакты |
|------|---------|-------------------|-------------------|
| 1 | /idea | — | docs/prd/{name}-prd.md |
| 2 | /research | PRD | (анализ в памяти) |
| 3 | /plan | PRD | docs/architecture/{name}-plan.md |
| 3 | /feature-plan | PRD | docs/plans/{feature}-plan.md |
| 4 | /generate | План | services/*, shared/* |
| 5 | /review | Код | docs/reports/review-*.md |
| 6 | /test | Код | docs/reports/qa-*.md |
| 7 | /validate | Все | docs/rtm.md |
| 8 | /deploy | Все | — |
```

**Шаг 2**: Добавить секцию в каждую команду

```markdown
## Обнаружение входных артефактов

### Требуемые артефакты
| Артефакт | Паттерн | Обязательный |
|----------|---------|--------------|
| PRD | `docs/prd/*-prd.md` | Да |
| План | `docs/architecture/*-plan.md` | Да |

### Алгоритм поиска
1. Проверить `.pipeline-state.json`
2. Если не найден → Glob по паттерну
3. Если множественные → взять последний по дате
4. Если не найден → ошибка "Артефакт не найден"
```

#### Файлы для изменения
- [ ] `workflow.md` — добавить алгоритм обнаружения
- [ ] `.claude/commands/research.md` — добавить секцию
- [ ] `.claude/commands/plan.md` — добавить секцию
- [ ] `.claude/commands/feature-plan.md` — добавить секцию
- [ ] `.claude/commands/generate.md` — добавить секцию
- [ ] `.claude/commands/review.md` — добавить секцию
- [ ] `.claude/commands/test.md` — добавить секцию
- [ ] `.claude/commands/validate.md` — добавить секцию

---

### [ ] P-022: Нет bootstrap процесса для создания структуры

**Приоритет**: 🔴 CRITICAL
**Тип**: Неполнота инициализации
**Зависит от**: P-001

#### Проблема
Пайплайн предполагает существование директорий, но не создаёт их.

#### Решение

**Шаг 1**: Добавить автоматическое создание структуры в `/idea`

Обновить `.claude/commands/idea.md`:

```markdown
## Инициализация структуры проекта

При первом запуске `/idea` необходимо создать структуру директорий:

### Проверка и создание

```bash
# Создать директории если не существуют
mkdir -p docs/prd
mkdir -p docs/architecture
mkdir -p docs/plans
mkdir -p docs/reports
mkdir -p docs/tasklists
```

### Создание файла состояния

```bash
# Если .pipeline-state.json не существует
if [ ! -f .pipeline-state.json ]; then
    echo '{"project_name": "", "mode": "", "current_stage": 0, "gates": {}}' > .pipeline-state.json
fi
```

### Чек-лист инициализации

- [ ] Проверить наличие docs/prd/
- [ ] Проверить наличие docs/architecture/
- [ ] Проверить наличие docs/plans/
- [ ] Проверить наличие docs/reports/
- [ ] Проверить наличие .pipeline-state.json
- [ ] Создать недостающие директории
```

**Шаг 2**: Добавить секцию "Bootstrap" в workflow.md

```markdown
## Bootstrap (инициализация проекта)

### Автоматическая инициализация

При первом запуске `/idea` выполняется:

1. **Проверка структуры**
   - Если отсутствуют директории → создать
   - Если отсутствует .pipeline-state.json → создать

2. **Создание директорий**
   ```
   docs/prd/
   docs/architecture/
   docs/plans/
   docs/reports/
   docs/tasklists/
   ```

3. **Инициализация состояния**
   ```json
   {
     "project_name": "{из PRD}",
     "mode": "CREATE|FEATURE",
     "current_stage": 1,
     "gates": {...}
   }
   ```

### Ручная инициализация (опционально)

Если нужно инициализировать без создания PRD:
```bash
# Создать структуру вручную
mkdir -p docs/{prd,architecture,plans,reports,tasklists}
```
```

#### Файлы для изменения
- [ ] `.claude/commands/idea.md` — добавить bootstrap
- [ ] `workflow.md` — добавить секцию Bootstrap
- [ ] `CLAUDE.md` — упомянуть автоматическую инициализацию

---

### [ ] P-032: Дублирование фреймворков (.ai-framework vs aidd-mvp-generator)

**Приоритет**: 🔴 CRITICAL
**Тип**: Архитектурная проблема
**Является причиной**: P-033, P-034, P-035, P-036

#### Проблема
В проекте существуют ДВА ПАРАЛЛЕЛЬНЫХ ФРЕЙМВОРКА, что создаёт путаницу.

#### Решение

**Рекомендуемый вариант**: Извлечение полезного (Вариант C)

**Шаг 1**: Идентифицировать полезные компоненты .ai-framework/

| Компонент | Путь | Действие |
|-----------|------|----------|
| INDEX.md | .ai-framework/docs/INDEX.md | Адаптировать для основного проекта |
| Navigation Matrix | .ai-framework/docs/reference/ai-navigation-matrix.md | Адаптировать |
| Deliverables Catalog | .ai-framework/docs/reference/deliverables-catalog.md | Извлечь принципы |
| AGENTS.md | .ai-framework/AGENTS.md | Изучить структуру |

**Шаг 2**: Создать документ решения

```markdown
## Политика использования .ai-framework/

### Текущий статус
`.ai-framework/` — это отдельный зрелый фреймворк, который НЕ используется
напрямую в aidd-mvp-generator.

### Решение
1. Извлечь полезные концепции (INDEX, Navigation Matrix)
2. Адаптировать под 8-стадийный процесс
3. НЕ интегрировать как submodule
4. Использовать как референс для улучшений

### Что извлечено
- [x] Концепция INDEX.md → создан docs/INDEX.md
- [x] Идея Navigation Matrix → создана docs/NAVIGATION.md
- [ ] Deliverables Catalog → адаптировать для 8 этапов
```

**Шаг 3**: Добавить в CLAUDE.md примечание

```markdown
## Примечание о .ai-framework/

> **ВАЖНО**: Директория `.ai-framework/` содержит отдельный фреймворк
> и НЕ является частью aidd-mvp-generator.
> AI-агенты должны использовать ТОЛЬКО документацию основного проекта.
> `.ai-framework/` может использоваться как референс для улучшений.
```

#### Файлы для изменения
- [ ] `CLAUDE.md` — добавить примечание о .ai-framework/
- [ ] Создать `docs/INDEX.md` (адаптированный)
- [ ] Создать `docs/NAVIGATION.md` (адаптированный)

---

### [ ] P-033: Несогласованность количества стадий (7 vs 8)

**Приоритет**: 🔴 CRITICAL
**Тип**: Конфликт документов
**Зависит от**: P-032

#### Проблема
Основной проект использует 8 стадий, .ai-framework/ использует 7 стадий.

#### Решение

**Шаг 1**: Задокументировать официальный 8-стадийный процесс

Добавить в `workflow.md`:

```markdown
## Официальный 8-стадийный процесс AIDD-MVP

> **ВАЖНО**: Это ЕДИНСТВЕННЫЙ официальный процесс.
> Другие варианты (7 стадий и т.д.) не применяются.

| # | Этап | Команда | Агент | Ворота |
|---|------|---------|-------|--------|
| 1 | Идея/PRD | /idea | Аналитик | PRD_READY |
| 2 | Исследование | /research | Исследователь | RESEARCH_DONE |
| 3 | Архитектура | /plan или /feature-plan | Архитектор | PLAN_APPROVED |
| 4 | Реализация | /generate | Реализатор | IMPLEMENT_OK |
| 5 | Ревью | /review | Ревьюер | REVIEW_OK |
| 6 | QA | /test | QA | QA_PASSED |
| 7 | Валидация | /validate | Валидатор | ALL_GATES_PASSED |
| 8 | Деплой | /deploy | Валидатор | DEPLOYED |
```

**Шаг 2**: Убедиться что все документы ссылаются на 8 этапов

Проверить и обновить:
- [ ] CLAUDE.md
- [ ] workflow.md
- [ ] README.md
- [ ] Все агенты в .claude/agents/

#### Файлы для изменения
- [ ] `workflow.md` — явно указать "8-стадийный процесс"
- [ ] `CLAUDE.md` — синхронизировать таблицу этапов

---

### [ ] P-034: Несогласованность путей артефактов (docs/ vs ai-docs/)

**Приоритет**: 🔴 CRITICAL
**Тип**: Конфликт документов

#### Проблема
Разные части проекта используют разные префиксы путей (docs/ vs ai-docs/).

#### Решение

**Шаг 1**: Установить единый стандарт

```markdown
## Стандарт путей артефактов

| Тип артефакта | Путь | Суффикс |
|---------------|------|---------|
| PRD | `docs/prd/{name}-prd.md` | -prd.md |
| Архитектура | `docs/architecture/{name}-plan.md` | -plan.md |
| План фичи | `docs/plans/{feature}-plan.md` | -plan.md |
| Отчёт QA | `docs/reports/qa-{name}.md` | qa-*.md |
| Отчёт ревью | `docs/reports/review-{name}.md` | review-*.md |
| RTM | `docs/rtm.md` | rtm.md |
| Tasklist | `docs/tasklists/{name}-tasks.md` | -tasks.md |

**ВАЖНО**: Префикс `ai-docs/` НЕ ИСПОЛЬЗУЕТСЯ.
```

**Шаг 2**: Найти и исправить все неправильные пути

```bash
grep -r "ai-docs/" --include="*.md"
```

Для каждого найденного файла заменить `ai-docs/` на `docs/`.

**Шаг 3**: Исправить суффиксы

```markdown
# Было (в разных местах):
{name}-arch.md
{name}-plan.md

# Стало (единый стандарт):
{name}-plan.md  # для архитектуры
```

#### Файлы для изменения
- [ ] `roles/validator/artifact-verification.md` — исправить ai-docs/ на docs/
- [ ] Поиск и замена во всех файлах с неправильными путями

#### Проверка
```bash
grep -r "ai-docs/" --include="*.md"
# Должно вернуть пустой результат
```

---

### [ ] P-035: .ai-framework не интегрирован как submodule

**Приоритет**: 🔴 CRITICAL
**Тип**: Архитектурная проблема
**Зависит от**: P-032

#### Проблема
.ai-framework/ существует но не интегрирован и не используется.

#### Решение

**Решение**: НЕ интегрировать как submodule (см. P-032)

**Шаг 1**: Задокументировать политику

Добавить в `CLAUDE.md`:

```markdown
## Политика в отношении .ai-framework/

`.ai-framework/` — это **отдельный проект**, который:
- НЕ интегрирован как submodule
- НЕ используется напрямую AI-агентами
- Может использоваться как референс для улучшений

**Причина**:
- Разные количества стадий (7 vs 8)
- Разные пути артефактов
- Разные соглашения

**AI-агенты должны игнорировать .ai-framework/** и работать
только с документацией основного проекта.
```

**Шаг 2**: Добавить .ai-framework/ в список игнорируемых

В CLAUDE.md или отдельном файле:

```markdown
## Игнорируемые директории

AI-агенты НЕ должны читать/изменять:
- `.ai-framework/` — отдельный проект
- `node_modules/` — зависимости
- `.git/` — система контроля версий
```

#### Файлы для изменения
- [ ] `CLAUDE.md` — добавить политику

---

### [ ] P-036: AI Navigation Matrix не адаптирована

**Приоритет**: 🔴 CRITICAL
**Тип**: Неполнота документации
**Зависит от**: P-032, P-035

#### Проблема
Navigation Matrix из .ai-framework/ полезна, но не адаптирована для основного проекта.

#### Решение

**Шаг 1**: Создать адаптированную Navigation Matrix

Создать `docs/NAVIGATION.md`:

```markdown
# Навигационная матрица AIDD-MVP Generator

> Карта файлов для каждого этапа пайплайна.

## Матрица по этапам

### Этап 1: Идея/PRD

| Что делать | Какие файлы читать | Какие файлы создавать |
|------------|-------------------|----------------------|
| Понять контекст | CLAUDE.md | — |
| Изучить процесс | workflow.md (секция 1) | — |
| Изучить роль | .claude/agents/analyst.md | — |
| Изучить шаблон | templates/documents/prd-template.md | — |
| Создать PRD | — | docs/prd/{name}-prd.md |

### Этап 2: Исследование

| Что делать | Какие файлы читать | Какие файлы создавать |
|------------|-------------------|----------------------|
| Прочитать PRD | docs/prd/{name}-prd.md | — |
| Изучить роль | .claude/agents/researcher.md | — |
| Анализ кода | src/**/*.py, services/**/*.py | — |

### Этап 3: Архитектура

| Что делать | Какие файлы читать | Какие файлы создавать |
|------------|-------------------|----------------------|
| Прочитать PRD | docs/prd/{name}-prd.md | — |
| Изучить роль | .claude/agents/planner.md | — |
| Изучить шаблон | templates/documents/architecture-template.md | — |
| Изучить принципы | knowledge/architecture/*.md | — |
| Создать план | — | docs/architecture/{name}-plan.md |

### Этап 4: Реализация

| Что делать | Какие файлы читать | Какие файлы создавать |
|------------|-------------------|----------------------|
| Прочитать план | docs/architecture/{name}-plan.md | — |
| Изучить роль | .claude/agents/coder.md | — |
| Изучить шаблоны | templates/services/* | — |
| Изучить shared | templates/shared/* | — |
| Создать код | — | services/*, shared/* |

### Этап 5: Ревью

| Что делать | Какие файлы читать | Какие файлы создавать |
|------------|-------------------|----------------------|
| Прочитать план | docs/architecture/{name}-plan.md | — |
| Изучить роль | .claude/agents/reviewer.md | — |
| Изучить соглашения | conventions.md | — |
| Проверить код | services/**/*.py | — |
| Создать отчёт | — | docs/reports/review-{name}.md |

### Этап 6: QA

| Что делать | Какие файлы читать | Какие файлы создавать |
|------------|-------------------|----------------------|
| Изучить роль | .claude/agents/qa.md | — |
| Изучить шаблон | templates/documents/qa-report-template.md | — |
| Запустить тесты | tests/**/*.py | — |
| Создать отчёт | — | docs/reports/qa-{name}.md |

### Этап 7: Валидация

| Что делать | Какие файлы читать | Какие файлы создавать |
|------------|-------------------|----------------------|
| Изучить роль | .claude/agents/validator.md | — |
| Проверить артефакты | docs/**/*.md | — |
| Создать RTM | — | docs/rtm.md |

### Этап 8: Деплой

| Что делать | Какие файлы читать | Какие файлы создавать |
|------------|-------------------|----------------------|
| Изучить роль | .claude/agents/validator.md | — |
| Изучить инфру | templates/infrastructure/* | — |
| Запустить | docker-compose.yml | — |

## Быстрый поиск

### По типу файла

| Тип | Паттерн | Назначение |
|-----|---------|-----------|
| Агенты | `.claude/agents/*.md` | Инструкции для ролей |
| Команды | `.claude/commands/*.md` | Определения slash-команд |
| Шаблоны сервисов | `templates/services/*/` | Шаблоны кода |
| База знаний | `knowledge/*/` | Справочная информация |
| Артефакты PRD | `docs/prd/*.md` | Документы требований |
| Артефакты планов | `docs/architecture/*.md` | Архитектурные планы |
```

#### Файлы для создания
- [ ] `docs/NAVIGATION.md`

---

## 🟠 HIGH: Проблемы высокого приоритета (10)

### [ ] P-005: Дублирование ответственности QA и Ревьюера

**Приоритет**: 🟠 HIGH
**Тип**: Дублирование информации

#### Проблема
Обе роли проверяют одни и те же аспекты (DRY, KISS, YAGNI).

#### Решение

**Шаг 1**: Разграничить ответственность

Обновить `.claude/agents/reviewer.md`:

```markdown
## Ответственность Ревьюера

Ревьюер проверяет **архитектурные и дизайн аспекты**:
- Соответствие архитектурному плану
- Соблюдение DRY, KISS, YAGNI
- Качество абстракций
- Читаемость кода
- Именование

**НЕ проверяет** (ответственность QA):
- Покрытие тестами
- Прохождение тестов
- Функциональную корректность
```

Обновить `.claude/agents/qa.md`:

```markdown
## Ответственность QA

QA проверяет **функциональные аспекты**:
- Покрытие тестами (≥75%)
- Прохождение всех тестов
- Функциональная корректность
- Edge cases

**НЕ проверяет** (ответственность Ревьюера):
- DRY, KISS, YAGNI
- Архитектурные решения
- Стиль кода
```

**Шаг 2**: Добавить матрицу ответственности в workflow.md

```markdown
## Матрица ответственности

| Аспект | Ревьюер | QA |
|--------|---------|-----|
| DRY/KISS/YAGNI | ✅ | ❌ |
| Архитектура | ✅ | ❌ |
| Покрытие тестами | ❌ | ✅ |
| Функциональность | ❌ | ✅ |
| Именование | ✅ | ❌ |
| Edge cases | ❌ | ✅ |
```

#### Файлы для изменения
- [ ] `.claude/agents/reviewer.md` — разграничить ответственность
- [ ] `.claude/agents/qa.md` — разграничить ответственность
- [ ] `workflow.md` — добавить матрицу ответственности

---

### [ ] P-006: Отсутствие алгоритма определения режима CREATE/FEATURE

**Приоритет**: 🟠 HIGH
**Тип**: Неполнота пайплайна

#### Проблема
Нет чёткого алгоритма определения режима CREATE или FEATURE.

#### Решение

**Шаг 1**: Определить алгоритм в workflow.md

```markdown
## Алгоритм определения режима

### Автоматическое определение

```python
def determine_mode() -> str:
    """Определить режим на основе существующей структуры."""

    # Признаки существующего проекта
    has_services = glob("services/*/")
    has_src = Path("src/").exists()
    has_docker_compose = Path("docker-compose.yml").exists()

    if has_services or has_src or has_docker_compose:
        return "FEATURE"
    else:
        return "CREATE"
```

### Ручное переопределение

Пользователь может явно указать режим:
```
/idea --mode=CREATE "описание"
/idea --mode=FEATURE "описание"
```

### Момент определения

Режим определяется на этапе `/idea` (Аналитик):
1. Проверить существующую структуру
2. Определить режим
3. Записать в .pipeline-state.json
4. Сообщить пользователю

### Индикаторы режима

| Режим | Индикаторы |
|-------|-----------|
| CREATE | Нет services/, нет src/, нет docker-compose.yml |
| FEATURE | Есть хотя бы один из: services/, src/, docker-compose.yml |
```

**Шаг 2**: Обновить .claude/commands/idea.md

```markdown
## Определение режима

### Автоматическое определение

1. Проверить наличие `services/` → если есть, режим FEATURE
2. Проверить наличие `src/` → если есть, режим FEATURE
3. Проверить наличие `docker-compose.yml` → если есть, режим FEATURE
4. Иначе → режим CREATE

### Вывод режима

```
Определён режим: CREATE
Причина: Не найдены существующие сервисы

или

Определён режим: FEATURE
Причина: Найдены существующие сервисы в services/
```
```

#### Файлы для изменения
- [ ] `workflow.md` — добавить алгоритм определения режима
- [ ] `.claude/commands/idea.md` — добавить логику определения
- [ ] `.claude/agents/analyst.md` — добавить инструкции

---

### [ ] P-007: Несогласованные пути артефактов

**Приоритет**: 🟠 HIGH
**Тип**: Конфликт документов

#### Проблема
Разные документы указывают разные пути для одних артефактов.

#### Решение

**Шаг 1**: Создать единую таблицу путей в CLAUDE.md

```markdown
## Стандартные пути артефактов

| Артефакт | Путь | Шаблон |
|----------|------|--------|
| PRD | `docs/prd/{project}-prd.md` | templates/documents/prd-template.md |
| Архитектурный план | `docs/architecture/{project}-plan.md` | templates/documents/architecture-template.md |
| План фичи | `docs/plans/{feature}-plan.md` | — |
| Отчёт ревью | `docs/reports/review-{project}.md` | — |
| Отчёт QA | `docs/reports/qa-{project}.md` | templates/documents/qa-report-template.md |
| RTM | `docs/rtm.md` | — |
| Tasklist | `docs/tasklists/{project}-tasks.md` | templates/documents/tasklist-template.md |
| Состояние | `.pipeline-state.json` | — |

> **ВАЖНО**: Все пути относительны к корню проекта.
```

**Шаг 2**: Синхронизировать все документы с этой таблицей

Проверить и обновить:
- workflow.md
- Все агенты
- Все команды

#### Файлы для изменения
- [ ] `CLAUDE.md` — добавить таблицу путей
- [ ] `workflow.md` — синхронизировать пути
- [ ] `.claude/agents/planner.md` — проверить пути
- [ ] Все `.claude/commands/*.md` — проверить пути

---

### [ ] P-008: Неполная документация команды /feature-plan

**Приоритет**: 🟠 HIGH
**Тип**: Неполнота документации

#### Проблема
Команда /feature-plan минимально документирована по сравнению с /plan.

#### Решение

**Шаг 1**: Расширить .claude/commands/feature-plan.md

```markdown
# /feature-plan — Планирование добавления фичи

## Обзор

Команда для создания плана интеграции новой функциональности
в существующий проект.

## Агент
**Архитектор** (`.claude/agents/planner.md`)

## Предусловия
| Ворота | Требование |
|--------|------------|
| `PRD_READY` | PRD для фичи создан |
| `RESEARCH_DONE` | Существующий код проанализирован |

## Входные артефакты
| Артефакт | Паттерн |
|----------|---------|
| PRD фичи | `docs/prd/*-prd.md` (последний) |
| Существующая архитектура | `docs/architecture/*-plan.md` |

## Выходные артефакты
| Артефакт | Путь |
|----------|------|
| План фичи | `docs/plans/{feature}-plan.md` |

## Структура плана фичи

```markdown
# План фичи: {название}

## 1. Контекст интеграции

### Существующие компоненты
- Какие сервисы затрагиваются
- Какие API будут изменены
- Какие модели данных затронуты

### Точки интеграции
- Где именно добавляется код
- Какие файлы изменяются

## 2. Изменения по компонентам

### Сервис A
- Новые эндпоинты
- Изменения в существующих
- Новые модели

### Сервис B
- ...

## 3. Миграции данных
- Изменения схемы БД
- Скрипты миграции

## 4. Обратная совместимость
- Что может сломаться
- Как избежать

## 5. План тестирования
- Какие тесты добавить
- Какие существующие могут сломаться
```

## Пример использования

```bash
/feature-plan

# Вывод:
Создаю план для фичи "email notifications"...
Анализирую существующую архитектуру...
План сохранён: docs/plans/email-notifications-plan.md
```
```

**Шаг 2**: Создать шаблон плана фичи

Создать `templates/documents/feature-plan-template.md`:

```markdown
# План фичи: {название}

**Дата**: {дата}
**PRD**: {ссылка на PRD}
**Режим**: FEATURE

---

## 1. Контекст интеграции

### 1.1 Существующие компоненты

| Компонент | Тип | Затрагивается |
|-----------|-----|---------------|
| | | Да/Нет |

### 1.2 Точки интеграции

| Файл | Изменение |
|------|-----------|
| | |

---

## 2. Изменения по компонентам

### 2.1 {Название сервиса}

**Новые файлы**:
-

**Изменённые файлы**:
-

**Новые эндпоинты**:
| Метод | Путь | Описание |
|-------|------|----------|
| | | |

---

## 3. Миграции данных

- [ ] Нужны миграции: Да/Нет

### Изменения схемы

```sql
-- Миграция
```

---

## 4. Обратная совместимость

### Риски
-

### Митигация
-

---

## 5. План тестирования

### Новые тесты
-

### Изменения существующих
-

---

## 6. Чек-лист готовности

- [ ] Точки интеграции определены
- [ ] Изменения по компонентам описаны
- [ ] Миграции спланированы
- [ ] Риски оценены
- [ ] Тесты спланированы
```

#### Файлы для изменения
- [ ] `.claude/commands/feature-plan.md` — расширить
- [ ] Создать `templates/documents/feature-plan-template.md`

---

### [ ] P-009: Неясная механика качественных ворот

**Приоритет**: 🟠 HIGH
**Тип**: Неполнота документации

#### Проблема
Ворота описаны, но механика их проверки не определена.

#### Решение

**Шаг 1**: Добавить детальное описание в workflow.md

```markdown
## Механика качественных ворот

### Типы проверки

| Ворота | Проверяет | Как |
|--------|-----------|-----|
| PRD_READY | AI (Аналитик) | Чек-лист в промпте |
| RESEARCH_DONE | AI (Исследователь) | Автоматически после анализа |
| PLAN_APPROVED | Пользователь | Явное подтверждение "Утвердить план?" |
| IMPLEMENT_OK | AI (Реализатор) | pytest, make build |
| REVIEW_OK | AI (Ревьюер) | Чек-лист в промпте |
| QA_PASSED | AI (QA) | pytest --cov, coverage ≥75% |
| ALL_GATES_PASSED | AI (Валидатор) | Проверка всех ворот |
| DEPLOYED | AI (Валидатор) | docker-compose up, health check |

### Фиксация прохождения

Прохождение ворот фиксируется в `.pipeline-state.json`:

```json
{
  "gates": {
    "PRD_READY": {
      "passed": true,
      "passed_at": "2025-12-21T10:00:00Z",
      "checked_by": "analyst",
      "evidence": "docs/prd/booking-prd.md"
    }
  }
}
```

### Чек-листы ворот

#### PRD_READY
- [ ] Все секции PRD заполнены
- [ ] Нет блокирующих вопросов
- [ ] Требования конкретные и измеримые

#### PLAN_APPROVED
- [ ] Пользователь явно подтвердил план
- [ ] Ответ содержит "да", "утверждаю", "ок"

#### IMPLEMENT_OK
- [ ] Все файлы созданы согласно плану
- [ ] pytest проходит
- [ ] make build успешен

#### REVIEW_OK
- [ ] Код соответствует conventions.md
- [ ] DRY соблюдён
- [ ] KISS соблюдён
- [ ] YAGNI соблюдён

#### QA_PASSED
- [ ] pytest проходит
- [ ] Coverage ≥75%
- [ ] Нет критических багов

#### ALL_GATES_PASSED
- [ ] Все предыдущие ворота пройдены
- [ ] RTM создан
- [ ] Артефакты консистентны

#### DEPLOYED
- [ ] docker-compose up успешен
- [ ] Health check проходит
- [ ] Логи без ошибок
```

#### Файлы для изменения
- [ ] `workflow.md` — добавить механику ворот
- [ ] Все `.claude/commands/*.md` — добавить чек-листы

---

### [ ] P-010: Конфликт settings.json с командами

**Приоритет**: 🟠 HIGH
**Тип**: Конфликт документов

#### Проблема
Глобальные разрешения в settings.json конфликтуют с локальными в командах.

#### Решение

**Шаг 1**: Определить модель разрешений

```markdown
## Модель разрешений

### Уровни разрешений (от общего к частному)

1. **settings.json** — глобальные разрешения (все сессии)
2. **commands/*.md** — разрешения команды (конкретная команда)

### Правило объединения

```
Итоговые разрешения = settings.json ∩ command.allowed-tools
```

Если команда не указывает allowed-tools, используются глобальные.

### Пример

```json
// settings.json
"allow": ["Bash(git :*)", "Bash(make :*)", "Bash(mkdir :*)"]
```

```markdown
# generate.md
allowed-tools: Bash(make :*)
```

```
Итог для /generate: только Bash(make :*)
```
```

**Шаг 2**: Синхронизировать settings.json и команды

Добавить недостающие разрешения в settings.json:
- `Bash(curl :*)` — для deploy.md

Обновить команды с полными списками.

#### Файлы для изменения
- [ ] `.claude/settings.json` — добавить `Bash(curl :*)`
- [ ] `.claude/commands/generate.md` — добавить `Bash(mkdir :*)`
- [ ] Документировать модель разрешений в CLAUDE.md

---

### [ ] P-023: Несогласованность между .claude/agents/ и roles/

**Приоритет**: 🟠 HIGH
**Тип**: Конфликт документов

#### Проблема
Агенты ссылаются на файлы в roles/, но нет проверки их наличия.

#### Решение

**Шаг 1**: Проверить все ссылки

```bash
# Проверить ссылки в analyst.md
grep -o "roles/[^|]*" .claude/agents/analyst.md | while read path; do
  if [ ! -f "$path" ]; then
    echo "BROKEN: $path"
  fi
done
```

**Шаг 2**: Исправить битые ссылки

```markdown
# analyst.md — исправить:
| `docs/prd/template.md` | → | `templates/documents/prd-template.md` |
```

**Шаг 3**: Добавить проверку в CI (опционально)

```yaml
# .github/workflows/check-links.yml
- name: Check internal links
  run: |
    find .claude/agents -name "*.md" -exec grep -l "roles/" {} \; | \
    xargs -I {} sh -c 'grep -o "roles/[^|)]*" {} | while read path; do
      [ ! -f "$path" ] && echo "BROKEN in {}: $path"
    done'
```

#### Файлы для изменения
- [ ] `.claude/agents/analyst.md` — исправить ссылку на шаблон
- [ ] `.claude/agents/planner.md` — проверить ссылки
- [ ] `.claude/agents/coder.md` — проверить ссылки
- [ ] `.claude/agents/validator.md` — проверить ссылки

---

### [ ] P-024: Нет карты зависимостей шаблонов

**Приоритет**: 🟠 HIGH
**Тип**: Неполнота документации

#### Проблема
Шаблоны существуют, но нет документа описывающего их взаимосвязи.

#### Решение

**Шаг 1**: Создать templates/README.md

```markdown
# Шаблоны сервисов AIDD-MVP

## Структура

```
templates/
├── services/              # Шаблоны типов сервисов
│   ├── fastapi_business_api/   # Business API
│   ├── aiogram_bot/            # Telegram Bot
│   ├── asyncio_worker/         # Background Worker
│   ├── postgres_data_api/      # Data API (PostgreSQL)
│   └── mongo_data_api/         # Data API (MongoDB)
├── shared/                # Общие компоненты
│   ├── http_client/           # HTTP клиент
│   ├── logging/               # Логирование
│   └── config/                # Конфигурация
└── infrastructure/        # Инфраструктура
    ├── docker/                # Docker файлы
    ├── nginx/                 # Nginx конфигурация
    └── github/                # GitHub Actions
```

## Матрица зависимостей

```
                    ┌─────────────┐
                    │   shared/   │
                    │ (обязательно│
                    │  для всех)  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ business_api  │  │    bot        │  │   worker      │
│ (опционально) │  │ (опционально) │  │ (опционально) │
└───────┬───────┘  └───────────────┘  └───────────────┘
        │
        │ HTTP
        ▼
┌───────────────┐
│   data_api    │
│ (обязательно  │
│  при наличии  │
│  business)    │
└───────────────┘
```

## Какие шаблоны использовать

### Минимальный MVP (API + БД)
- [x] `shared/` — обязательно
- [x] `fastapi_business_api/` — бизнес-логика
- [x] `postgres_data_api/` — доступ к данным
- [x] `infrastructure/docker/` — контейнеризация

### MVP с ботом
- [x] Всё из "Минимальный MVP"
- [x] `aiogram_bot/` — Telegram интерфейс

### MVP с фоновыми задачами
- [x] Всё из "Минимальный MVP"
- [x] `asyncio_worker/` — фоновые процессы

## Порядок использования

1. **Всегда первым**: `shared/`
2. **Затем**: `infrastructure/docker/`
3. **Затем**: Нужные сервисы (`business_api`, `data_api`, etc.)
4. **В конце**: `infrastructure/nginx/` (если нужен gateway)

## Плейсхолдеры

| Плейсхолдер | Замена | Пример |
|-------------|--------|--------|
| `{project}` | Название проекта | `booking` |
| `{service}` | Название сервиса | `booking_api` |
| `{port}` | Порт сервиса | `8000` |
```

#### Файлы для создания
- [ ] `templates/README.md`

---

### [ ] P-025: Пайплайн FEATURE не детализирован

**Приоритет**: 🟠 HIGH
**Тип**: Неполнота пайплайна

#### Проблема
Режим FEATURE упоминается, но детализация минимальна.

#### Решение

**Шаг 1**: Добавить детальное описание в workflow.md

```markdown
## Пайплайн FEATURE

### Отличия от CREATE

| Аспект | CREATE | FEATURE |
|--------|--------|---------|
| Структура | Создаётся с нуля | Используется существующая |
| Шаблоны | Полные | Только недостающие |
| docker-compose | Новый | Обновляется |
| shared/ | Создаётся | Переиспользуется |
| Тесты | Новые | Добавляются к существующим |

### Этапы FEATURE

#### 1. Идея (/idea)
- Анализ PRD фичи
- Определение режима = FEATURE (автоматически)

#### 2. Исследование (/research)
- Анализ существующего кода
- Поиск точек интеграции
- Идентификация переиспользуемых компонентов

#### 3. Планирование (/feature-plan)
- План интеграции, НЕ полная архитектура
- Указание изменяемых файлов
- Оценка влияния на существующий код

#### 4. Реализация (/generate)
- Модификация существующих файлов
- Добавление новых только при необходимости
- Обновление docker-compose.yml

#### 5-8. Ревью, QA, Валидация, Деплой
- Аналогично CREATE
- Проверка обратной совместимости

### Интеграция с существующим кодом

#### Обновление docker-compose.yml

```yaml
# Добавить новый сервис
services:
  existing_service:
    # ... существующая конфигурация ...

  new_feature_service:  # <-- Добавляется
    build: ./services/new_feature
    # ...
```

#### Обновление shared/

```python
# Если нужен новый общий компонент:
# 1. Проверить нет ли похожего в shared/
# 2. Если есть — использовать существующий
# 3. Если нет — добавить в shared/, не дублировать
```

#### Обновление RTM

```markdown
# docs/rtm.md

## Требования

| ID | Требование | Статус |
|----|-----------|--------|
| R-001 | Существующее | ✅ |
| R-002 | Существующее | ✅ |
| R-NEW-001 | Новое из фичи | ⏳ |  <-- Добавляется
```
```

#### Файлы для изменения
- [ ] `workflow.md` — добавить детальное описание FEATURE
- [ ] `.claude/commands/feature-plan.md` — расширить
- [ ] `.claude/agents/planner.md` — добавить секцию FEATURE

---

### [ ] P-026: Нет проверки предусловий команд

**Приоритет**: 🟠 HIGH
**Тип**: Целостность пайплайна

#### Проблема
Команды объявляют предусловия, но нет механизма их проверки.

#### Решение

**Шаг 1**: Добавить проверку в каждую команду

```markdown
## Проверка предусловий

### Обязательная проверка перед выполнением

1. Прочитать `.pipeline-state.json`
2. Проверить статус ворот:
   ```
   Для /generate требуется:
   - PLAN_APPROVED = true

   Если не выполнено:
   - Сообщить пользователю
   - НЕ продолжать выполнение
   ```

### Сообщение при невыполненных предусловиях

```
❌ Невозможно выполнить /generate

Предусловия не выполнены:
- PLAN_APPROVED: не пройдены

Выполните сначала:
1. /plan — создать архитектурный план
2. Утвердить план (ответить "да")
```
```

**Шаг 2**: Обновить каждую команду

Добавить в начало каждой команды:

```markdown
## Проверка предусловий

Перед выполнением команды ОБЯЗАТЕЛЬНО:

1. Проверить `.pipeline-state.json`:
   ```
   gates.{REQUIRED_GATE}.passed === true
   ```

2. Если предусловие не выполнено:
   ```
   Вывести сообщение об ошибке
   Указать какие команды выполнить
   НЕ продолжать
   ```
```

#### Файлы для изменения
- [ ] `.claude/commands/research.md` — добавить проверку PRD_READY
- [ ] `.claude/commands/plan.md` — добавить проверку RESEARCH_DONE
- [ ] `.claude/commands/feature-plan.md` — добавить проверку RESEARCH_DONE
- [ ] `.claude/commands/generate.md` — добавить проверку PLAN_APPROVED
- [ ] `.claude/commands/review.md` — добавить проверку IMPLEMENT_OK
- [ ] `.claude/commands/test.md` — добавить проверку IMPLEMENT_OK
- [ ] `.claude/commands/validate.md` — добавить проверку QA_PASSED
- [ ] `.claude/commands/deploy.md` — добавить проверку ALL_GATES_PASSED

---

## 🟡 MEDIUM: Проблемы среднего приоритета (9)

### [ ] P-011: Отсутствие документации по интеграции фич

**Приоритет**: 🟡 MEDIUM
**Тип**: Неполнота документации

#### Решение
Решается в рамках P-025 (Пайплайн FEATURE не детализирован).

---

### [ ] P-012: Нет документации по структуре шаблонов

**Приоритет**: 🟡 MEDIUM
**Тип**: Неполнота документации

#### Решение
Решается в рамках P-024 (Нет карты зависимостей шаблонов).

---

### [ ] P-013: Философия "Артефакты = Память" без реализации

**Приоритет**: 🟡 MEDIUM
**Тип**: Неполнота документации

#### Решение
Решается в рамках P-020 (Нет механизма передачи состояния).

---

### [ ] P-014: Несогласованность именования файлов

**Приоритет**: 🟡 MEDIUM
**Тип**: Несогласованность

#### Проблема
Соглашения указывают kebab-case, но некоторые файлы используют snake_case.

#### Решение

**Шаг 1**: Уточнить conventions.md

```markdown
## Именование файлов

### Документация (.md)
- **Стиль**: kebab-case
- **Примеры**: `prd-template.md`, `api-contracts.md`

### Код Python (.py)
- **Стиль**: snake_case
- **Примеры**: `user_service.py`, `booking_repository.py`

### Директории
- **Для ролей**: snake_case (`roles/analyst/`)
- **Для документов**: kebab-case (`docs/prd/`)
- **Для кода**: snake_case (`services/booking_api/`)

### Исключения
- `CLAUDE.md`, `README.md` — UPPERCASE допускается
```

#### Файлы для изменения
- [ ] `conventions.md` — уточнить правила именования

---

### [ ] P-015: Отсутствие версионирования артефактов

**Приоритет**: 🟡 MEDIUM
**Тип**: Неполнота документации

#### Решение
Частично решается в P-020 (хеши артефактов) и P-028.

---

### [ ] P-027: RTM не имеет шаблона

**Приоритет**: 🟡 MEDIUM
**Тип**: Неполнота документации

#### Проблема
Валидатор должен создать RTM, но шаблон отсутствует.

#### Решение

**Шаг 1**: Создать templates/documents/rtm-template.md

```markdown
# Requirements Traceability Matrix (RTM)

**Проект**: {project_name}
**Дата**: {date}
**Версия**: 1.0

---

## 1. Матрица требований

| ID | Требование | Приоритет | Статус | Реализация | Тест |
|----|-----------|-----------|--------|------------|------|
| R-001 | | HIGH/MED/LOW | ✅/⏳/❌ | `path/to/file.py` | `test_*.py` |
| R-002 | | | | | |

### Легенда статусов
- ✅ Реализовано и протестировано
- ⏳ В процессе
- ❌ Не начато

---

## 2. Покрытие требований

| Требование | Код | Тест | Документация |
|-----------|-----|------|--------------|
| R-001 | ✅ | ✅ | ✅ |
| R-002 | ✅ | ⏳ | ❌ |

### Сводка
- **Всего требований**: X
- **Реализовано**: Y (Z%)
- **Покрыто тестами**: W (V%)

---

## 3. Трассировка PRD → Код

### R-001: {название требования}

**Из PRD**:
> {цитата из PRD}

**Реализация**:
- `services/booking_api/domain/models.py:15-30`
- `services/booking_api/api/endpoints.py:45-60`

**Тесты**:
- `tests/unit/test_booking.py::test_create_booking`
- `tests/integration/test_api.py::test_booking_flow`

---

## 4. История изменений

| Дата | Версия | Изменение |
|------|--------|-----------|
| {date} | 1.0 | Первоначальная версия |
```

#### Файлы для создания
- [ ] `templates/documents/rtm-template.md`

---

### [ ] P-028: Нет версионирования артефактов

**Приоритет**: 🟡 MEDIUM
**Тип**: Неполнота пайплайна

#### Решение
Частично решается в P-020 (хеши артефактов в state file).

Дополнительно:

**Шаг 1**: Добавить секцию "История изменений" в шаблоны

```markdown
---

## История изменений

| Версия | Дата | Описание |
|--------|------|----------|
| 1.0 | {date} | Первоначальная версия |
```

#### Файлы для изменения
- [ ] `templates/documents/prd-template.md` — добавить историю
- [ ] `templates/documents/architecture-template.md` — добавить историю

---

### [ ] P-029: Отсутствует диаграмма зависимостей файлов

**Приоритет**: 🟡 MEDIUM
**Тип**: Неполнота документации

#### Решение
Решается в рамках P-019 (INDEX.md) и P-036 (Navigation Matrix).

---

### [ ] P-030: Конфликт пути tasklists/

**Приоритет**: 🟡 MEDIUM
**Тип**: Несогласованность

#### Проблема
workflow.md упоминает docs/tasklists/, но директория не существует.

#### Решение
Решается в рамках P-001 (создание директорий).

---

## 🟢 LOW: Проблемы низкого приоритета (4)

### [ ] P-016: Строгое требование Python 3.11+

**Приоритет**: 🟢 LOW
**Тип**: Ограничение

#### Проблема
README указывает Python 3.11+, но большинство зависимостей совместимы с 3.10+.

#### Решение

**Опция A**: Оставить 3.11+ (рекомендуется)
- Современный синтаксис (match/case, TypedDict improvements)
- Лучшая производительность

**Опция B**: Ослабить до 3.10+
- Обновить README.md

#### Файлы для изменения (если выбрать B)
- [ ] `README.md` — изменить "Python 3.11+" на "Python 3.10+"

---

### [ ] P-017: Ссылка на несуществующий раздел agents в CLAUDE.md

**Приоритет**: 🟢 LOW
**Тип**: Косметическое

#### Проблема
Путь с `/` в начале может не работать в некоторых системах.

#### Решение

```markdown
# Было:
| [.claude/agents/](/.claude/agents/) |

# Стало:
| [.claude/agents/](.claude/agents/) |
```

#### Файлы для изменения
- [ ] `CLAUDE.md` — убрать начальный `/` в ссылке

---

### [ ] P-018: Избыточные пути с "tasklists/"

**Приоритет**: 🟢 LOW
**Тип**: Несогласованность

#### Решение
Решается в рамках P-001 (создание директорий) и P-030.

---

### [ ] P-031: Нет отдельного агента Deployer

**Приоритет**: 🟢 LOW
**Тип**: Архитектурное решение

#### Проблема
Команда /deploy использует агента Валидатор, хотя деплой — отдельная функция.

#### Решение

**Опция A**: Оставить как есть (рекомендуется для MVP)
- Меньше агентов = проще
- Валидатор уже имеет нужные инструменты

**Опция B**: Создать отдельного агента (для масштабирования)
- Создать `.claude/agents/deployer.md`
- Обновить `/deploy` команду

#### Решение для MVP
Оставить как есть, добавить комментарий:

```markdown
# В .claude/agents/validator.md

> **Примечание**: Валидатор также выполняет функции Deployer.
> При масштабировании проекта рекомендуется выделить отдельную роль.
```

#### Файлы для изменения
- [ ] `.claude/agents/validator.md` — добавить примечание

---

## Порядок выполнения

### Фаза 1: Критическая структура (блокирует остальное)
1. [ ] P-001 — Создать директории
2. [ ] P-002 — Исправить ссылку на шаблон
3. [ ] P-022 — Bootstrap процесс

### Фаза 2: Состояние и навигация
4. [ ] P-019 — INDEX.md
5. [ ] P-020 — Pipeline state
6. [ ] P-021 — Алгоритм обнаружения
7. [ ] P-036 — Navigation Matrix

### Фаза 3: Консистентность документации
8. [ ] P-003 — Конфликт инструментов
9. [ ] P-007 — Пути артефактов
10. [ ] P-034 — docs/ vs ai-docs/
11. [ ] P-023 — Ссылки agents → roles

### Фаза 4: Пайплайн
12. [ ] P-004 — Откат при неудаче
13. [ ] P-009 — Механика ворот
14. [ ] P-006 — CREATE/FEATURE
15. [ ] P-026 — Проверка предусловий

### Фаза 5: Документация
16. [ ] P-005 — QA vs Ревьюер
17. [ ] P-008 — /feature-plan
18. [ ] P-010 — settings.json
19. [ ] P-024 — Карта шаблонов
20. [ ] P-025 — FEATURE пайплайн
21. [ ] P-027 — RTM шаблон

### Фаза 6: Политики
22. [ ] P-032 — Политика .ai-framework
23. [ ] P-033 — 8 стадий
24. [ ] P-035 — Не интегрировать submodule

### Фаза 7: Косметика
25. [ ] P-014 — Именование
26. [ ] P-015 / P-028 — Версионирование
27. [ ] P-016 — Python версия
28. [ ] P-017 — Ссылка в CLAUDE.md
29. [ ] P-031 — Примечание о Deployer

---

## Чек-лист завершения

- [ ] Все 36 проблем отмечены как решённые
- [ ] Директории созданы и содержат README
- [ ] INDEX.md создан
- [ ] NAVIGATION.md создан
- [ ] Pipeline state задокументирован
- [ ] Все ссылки проверены (нет битых)
- [ ] Пути артефактов синхронизированы
- [ ] Механика ворот документирована
- [ ] Алгоритм CREATE/FEATURE описан
- [ ] Шаблоны созданы (RTM, feature-plan)
- [ ] Прогресс обновлён до 100%

---

**Создан**: 2025-12-21
**Автор**: AI Agent
