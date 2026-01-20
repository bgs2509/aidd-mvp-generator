# placeholder: Решение проблем AIDD-MVP Generator

**Дата создания**: 2025-12-19
**Автор**: AI Agent (Анализатор)
**Статус**: К выполнению
**Источник**: Комплексный анализ проекта

---

## Сводка

| # | Проблема | Критичность | Статус |
|---|----------|-------------|--------|
| 1 | Несогласованность путей к артефактам | 🔴 Critical | [ ] |
| 2 | Отсутствует metrics.md | 🔴 Critical | [ ] |
| 3 | Неверные ссылки на шаблон PRD | 🔴 Critical | [ ] |
| 4 | Нет рабочего примера проекта | 🟡 Important | [ ] |
| 5 | Quality Gates не автоматизированы | 🟡 Important | [ ] |
| 6 | Нет скрипта инициализации проекта | 🟡 Important | [ ] |
| 7 | RTM путь неоднозначен | 🟢 Minor | [ ] |
| 8 | Нет версионирования шаблонов | 🟢 Minor | [ ] |
| 9 | Дублирование информации agent/role | 🟢 Minor | [ ] |

---

# КРИТИЧЕСКИЕ ПРОБЛЕМЫ (🔴)

---

## Проблема №1: Несогласованность путей к артефактам

### Описание проблемы

Разные файлы документации указывают разные пути для хранения артефактов.
Это создаёт путаницу для AI-агентов и может привести к потере документов.

**Конфликтующие пути:**

| Файл | Указанный путь |
|------|----------------|
| `templates/documents/README.md` | `ai-docs/prd/{name}-prd.md` |
| `templates/documents/README.md` | `ai-docs/architecture/{name}.md` |
| `templates/documents/README.md` | `ai-docs/plans/{name}.md` |
| `templates/documents/README.md` | `ai-docs/reports/` |
| `templates/documents/README.md` | `ai-docs/rtm.md` |
| `.claude/agents/analyst.md` | `docs/prd/{name}-prd.md` |
| `workflow.md` | `docs/prd/{name}-prd.md` |
| `roles/analyst/prd-formation.md` | `docs/prd/` |

**Затронутые файлы (16 штук):**

```
templates/documents/README.md
templates/documents/validation-report-template.md
knowledge/architecture/project-structure.md
roles/validator/validation-report.md
roles/validator/artifact-verification.md
roles/validator/quality-gates.md
roles/qa/qa-report.md
roles/qa/test-scenarios.md
roles/reviewer/review-report.md
roles/reviewer/architecture-compliance.md
roles/implementer/infrastructure-setup.md
roles/architect/api-contracts.md
roles/architect/implementation-plan.md
roles/architect/architecture-design.md
```

**Влияние:**
- AI-агент не знает, куда сохранять файлы
- Документы могут оказаться в разных местах
- Нарушается трассировка требований

### Решение проблемы №1

**Стандарт:** Использовать `docs/` как единый корень для всех артефактов.

**Целевая структура:**

```
docs/
├── prd/                        # PRD документы
│   ├── {project}-prd.md
│   └── {feature}-feature-prd.md
├── architecture/               # Архитектурные документы
│   └── {project}-architecture.md
├── plans/                      # Планы реализации
│   ├── {project}-implementation-plan.md
│   └── {feature}-plan.md
├── reports/                    # Отчёты
│   ├── review-{name}.md
│   ├── qa-{name}.md
│   └── validation-{name}.md
├── templates/                  # Шаблоны (уже есть)
│   └── ...
└── rtm.md                      # Матрица трассировки
```

**Задачи:**

- [ ] **1.1** Обновить `templates/documents/README.md`:
  - Заменить все `ai-docs/` на `docs/`

- [ ] **1.2** Обновить файлы в `roles/`:
  - `roles/validator/validation-report.md`
  - `roles/validator/artifact-verification.md`
  - `roles/validator/quality-gates.md`
  - `roles/qa/qa-report.md`
  - `roles/qa/test-scenarios.md`
  - `roles/reviewer/review-report.md`
  - `roles/reviewer/architecture-compliance.md`
  - `roles/implementer/infrastructure-setup.md`
  - `roles/architect/api-contracts.md`
  - `roles/architect/implementation-plan.md`
  - `roles/architect/architecture-design.md`

- [ ] **1.3** Обновить `knowledge/architecture/project-structure.md`

- [ ] **1.4** Обновить `templates/documents/validation-report-template.md`

- [ ] **1.5** Создать директории:
  ```bash
  mkdir -p docs/prd
  mkdir -p docs/architecture
  mkdir -p docs/plans
  mkdir -p docs/reports
  ```

**Паттерн замены:**

```
БЫЛО:                           СТАЛО:
ai-docs/prd/                    docs/prd/
ai-docs/architecture/           docs/architecture/
ai-docs/plans/                  docs/plans/
ai-docs/reports/                docs/reports/
ai-docs/rtm.md                  docs/rtm.md
```

---

## Проблема №2: Отсутствует metrics.md

### Описание проблемы

В плане реализации (`docs/history/2025-12-19-aidd-mvp-implementation-todo.md`)
указан файл `roles/implementer/metrics.md` для инструкций по настройке метрик.

**Запланировано в Фазе 2:**

```
| 2.4.8 | [ ] | roles/implementer/metrics.md | Метрики (Level ≥ 3) |
```

**Фактически существует (8 файлов вместо 9):**

```
roles/implementer/
├── infrastructure-setup.md   ✓
├── data-service.md           ✓
├── business-api.md           ✓
├── telegram-bot.md           ✓
├── background-worker.md      ✓
├── testing.md                ✓
├── logging.md                ✓
├── metrics.md                ✗ ОТСУТСТВУЕТ
└── nginx.md                  ✓
```

**Влияние:**
- Реализатор не получает инструкции по Prometheus
- Проекты Level 3+ не имеют гайда по метрикам
- Нарушается полнота документации

### Решение проблемы №2

**Задача:** Создать файл `roles/implementer/metrics.md`

**Содержимое файла:**

```markdown
# Функция: Настройка метрик (Stage 4.8)

> **Назначение**: Настройка Prometheus метрик для мониторинга.
> Применяется для проектов Level ≥ 3.

---

## Цель

Добавить сбор метрик для мониторинга производительности и здоровья сервисов.

---

## Когда применять

| Уровень зрелости | Метрики |
|------------------|---------|
| Level 1 (Prototype) | Не требуется |
| Level 2 (MVP) | Не требуется |
| Level 3 (Production) | **Обязательно** |
| Level 4 (Scale) | **Обязательно** |

---

## Что создаётся

### 1. Prometheus метрики

Файл: `src/core/metrics.py`

- Счётчики запросов (request_count)
- Гистограммы времени ответа (request_latency)
- Gauge для активных соединений
- Кастомные бизнес-метрики

### 2. Эндпоинт /metrics

Файл: `src/api/v1/metrics.py`

- Prometheus-совместимый формат
- Защита через internal network

### 3. Docker конфигурация

Файл: `docker-compose.prod.yml`

- Сервис Prometheus
- Сервис Grafana
- Сеть для метрик

---

## Стандартные метрики

| Метрика | Тип | Описание |
|---------|-----|----------|
| http_requests_total | Counter | Общее число запросов |
| http_request_duration_seconds | Histogram | Время обработки |
| http_requests_in_progress | Gauge | Активные запросы |
| db_connections_active | Gauge | Соединения с БД |

---

## Шаблон кода

### metrics.py

from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

---

## Источники

| Документ | Описание |
|----------|----------|
| knowledge/quality/metrics/prometheus-setup.md | Настройка Prometheus |
| knowledge/quality/metrics/custom-metrics.md | Кастомные метрики |
| .ai-framework/docs/atomic/observability/ | Оригинальная документация |
```

**Задачи:**

- [ ] **2.1** Создать файл `roles/implementer/metrics.md` с содержимым выше
- [ ] **2.2** Добавить ссылку в `.claude/agents/implementer.md`
- [ ] **2.3** Создать `knowledge/quality/metrics/prometheus-setup.md`
- [ ] **2.4** Создать `knowledge/quality/metrics/custom-metrics.md`

---

## Проблема №3: Неверные ссылки на шаблон PRD

### Описание проблемы

Несколько файлов ссылаются на несуществующий путь `docs/prd/template.md`:

**Файлы со сломанными ссылками:**

| Файл | Ссылка |
|------|--------|
| `.claude/agents/analyst.md` | `docs/prd/template.md` |
| `roles/analyst/prd-formation.md` | `docs/prd/template.md` |

**Реальное расположение шаблона:**

```
templates/documents/prd-template.md  ← Шаблон здесь
```

**Влияние:**
- AI-агент Аналитик не найдёт шаблон
- PRD будет генерироваться без структуры
- Качество документации снизится

### Решение проблемы №3

**Вариант A (рекомендуется):** Обновить ссылки в файлах

**Задачи:**

- [ ] **3.1** Обновить `.claude/agents/analyst.md`:
  ```
  БЫЛО:  docs/prd/template.md
  СТАЛО: templates/documents/prd-template.md
  ```

- [ ] **3.2** Обновить `roles/analyst/prd-formation.md`:
  ```
  БЫЛО:  docs/prd/template.md
  СТАЛО: templates/documents/prd-template.md
  ```

- [ ] **3.3** Проверить другие файлы на сломанные ссылки:
  ```bash
  grep -r "docs/prd/template" --include="*.md"
  ```

**Вариант B (альтернатива):** Создать символическую ссылку

```bash
mkdir -p docs/prd
ln -s ../templates/prd-template.md docs/prd/template.md
```

---

# ВАЖНЫЕ ПРОБЛЕМЫ (🟡)

---

## Проблема №4: Нет рабочего примера проекта

### Описание проблемы

Фреймворк содержит 523 файла документации и шаблонов, но нет ни одного
рабочего примера, демонстрирующего результат работы.

**Текущее состояние:**

```
aidd-mvp-generator/
├── .claude/           # Агенты и команды ✓
├── roles/             # Инструкции ролей ✓
├── knowledge/         # База знаний ✓
├── templates/         # Шаблоны сервисов ✓
├── docs/              # Документация ✓
└── examples/          # ✗ НЕ СУЩЕСТВУЕТ
```

**Влияние:**
- Пользователь не видит конечный результат
- Невозможно протестировать фреймворк
- Сложно понять реальный flow работы
- Высокий барьер входа для новых пользователей

### Решение проблемы №4

**Задача:** Создать полный пример проекта "Бронирование ресторанов"

**Целевая структура:**

```
examples/
└── booking-restaurant/
    ├── README.md                           # Описание примера
    ├── docs/
    │   ├── prd/
    │   │   └── booking-restaurant-prd.md   # Готовый PRD
    │   ├── architecture/
    │   │   └── booking-restaurant-arch.md  # Архитектура
    │   ├── plans/
    │   │   └── booking-restaurant-plan.md  # План реализации
    │   └── rtm.md                          # RTM
    ├── services/
    │   ├── booking_api/                    # Business API
    │   │   ├── src/
    │   │   ├── tests/
    │   │   ├── Dockerfile
    │   │   └── requirements.txt
    │   └── booking_data/                   # Data API
    │       ├── src/
    │       ├── tests/
    │       ├── Dockerfile
    │       └── requirements.txt
    ├── docker-compose.yml
    ├── docker-compose.dev.yml
    ├── Makefile
    └── .env.example
```

**Задачи:**

- [ ] **4.1** Создать директорию `examples/booking-restaurant/`
- [ ] **4.2** Написать `README.md` с описанием примера
- [ ] **4.3** Создать заполненный PRD документ
- [ ] **4.4** Создать архитектурный документ
- [ ] **4.5** Создать план реализации
- [ ] **4.6** Реализовать `booking_data` сервис (Data API)
- [ ] **4.7** Реализовать `booking_api` сервис (Business API)
- [ ] **4.8** Настроить docker-compose
- [ ] **4.9** Добавить тесты с coverage ≥ 75%
- [ ] **4.10** Проверить работоспособность примера

---

## Проблема №5: Quality Gates не автоматизированы

### Описание проблемы

В `settings.json` описаны хуки для проверки качественных ворот:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "check_gate PRD_READY"
      }
    ]
  }
}
```

Однако скрипты проверки не существуют. Ворота проверяются только документально
через чек-листы в markdown файлах.

**Влияние:**
- Можно случайно пропустить этап
- Переход между этапами не контролируется
- Quality Gates существуют только на бумаге

### Решение проблемы №5

**Задача:** Создать систему автоматической проверки ворот

**Целевая структура:**

```
scripts/
├── __init__.py
├── gates/
│   ├── __init__.py
│   ├── base.py                 # Базовый класс Gate
│   ├── prd_ready.py            # PRD_READY
│   ├── research_done.py        # RESEARCH_DONE
│   ├── plan_approved.py        # PLAN_APPROVED
│   ├── implement_ok.py         # IMPLEMENT_OK
│   ├── review_ok.py            # REVIEW_OK
│   ├── qa_passed.py            # QA_PASSED
│   └── all_gates_passed.py     # ALL_GATES_PASSED
├── check_gate.py               # CLI для проверки
└── requirements.txt
```

**Пример реализации:**

```python
# scripts/gates/prd_ready.py
"""Проверка качественных ворот PRD_READY."""

from pathlib import Path
from typing import List, Tuple
import re


class PRDReadyGate:
    """Проверяет готовность PRD документа."""

    def __init__(self, prd_path: str):
        """
        Инициализация проверки.

        Args:
            prd_path: Путь к PRD файлу
        """
        self.prd_path = Path(prd_path)
        self.errors: List[str] = []

    def check(self) -> Tuple[bool, List[str]]:
        """
        Выполняет все проверки PRD_READY.

        Returns:
            Tuple[bool, List[str]]: (passed, errors)
        """
        self._check_file_exists()
        self._check_sections()
        self._check_requirements_have_id()
        self._check_priorities()
        self._check_acceptance_criteria()
        self._check_no_blocking_questions()

        return len(self.errors) == 0, self.errors

    def _check_file_exists(self):
        """Проверяет существование файла."""
        if not self.prd_path.exists():
            self.errors.append(f"PRD файл не найден: {self.prd_path}")

    def _check_sections(self):
        """Проверяет наличие всех обязательных секций."""
        required_sections = [
            "## 1. Обзор",
            "## 2. Функциональные требования",
            "## 3. UI/UX требования",
            "## 4. Нефункциональные требования",
            "## 5. Ограничения и допущения",
            "## 6. Открытые вопросы",
        ]
        content = self.prd_path.read_text()
        for section in required_sections:
            if section not in content:
                self.errors.append(f"Отсутствует секция: {section}")

    def _check_requirements_have_id(self):
        """Проверяет наличие ID у всех требований."""
        content = self.prd_path.read_text()
        # Ищем строки с требованиями без ID
        pattern = r"\|\s*\|\s*[^|]+\s*\|"  # | | Something |
        if re.search(pattern, content):
            self.errors.append("Найдены требования без ID")

    def _check_priorities(self):
        """Проверяет наличие приоритетов."""
        content = self.prd_path.read_text()
        if "Must" not in content and "Should" not in content:
            self.errors.append("Не указаны приоритеты (Must/Should/Could)")

    def _check_acceptance_criteria(self):
        """Проверяет критерии приёмки для Must требований."""
        # Логика проверки
        pass

    def _check_no_blocking_questions(self):
        """Проверяет отсутствие блокирующих вопросов."""
        content = self.prd_path.read_text()
        if "| Open |" in content or "|Open|" in content:
            self.errors.append("Есть открытые блокирующие вопросы")
```

**CLI скрипт:**

```python
# scripts/check_gate.py
#!/usr/bin/env python3
"""CLI для проверки качественных ворот."""

import argparse
import sys
from gates.prd_ready import PRDReadyGate


def main():
    parser = argparse.ArgumentParser(description="Проверка Quality Gates")
    parser.add_argument("gate", choices=[
        "PRD_READY", "RESEARCH_DONE", "PLAN_APPROVED",
        "IMPLEMENT_OK", "REVIEW_OK", "QA_PASSED", "ALL_GATES_PASSED"
    ])
    parser.add_argument("--path", required=True, help="Путь к артефакту")

    args = parser.parse_args()

    if args.gate == "PRD_READY":
        gate = PRDReadyGate(args.path)
        passed, errors = gate.check()

        if passed:
            print("✅ PRD_READY: Все проверки пройдены")
            sys.exit(0)
        else:
            print("❌ PRD_READY: Обнаружены проблемы:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)


if __name__ == "__main__":
    main()
```

**Задачи:**

- [ ] **5.1** Создать директорию `scripts/gates/`
- [ ] **5.2** Реализовать `base.py` — базовый класс Gate
- [ ] **5.3** Реализовать `prd_ready.py` — PRD_READY
- [ ] **5.4** Реализовать `research_done.py` — RESEARCH_DONE
- [ ] **5.5** Реализовать `plan_approved.py` — PLAN_APPROVED
- [ ] **5.6** Реализовать `implement_ok.py` — IMPLEMENT_OK
- [ ] **5.7** Реализовать `review_ok.py` — REVIEW_OK
- [ ] **5.8** Реализовать `qa_passed.py` — QA_PASSED
- [ ] **5.9** Реализовать `all_gates_passed.py` — ALL_GATES_PASSED
- [ ] **5.10** Создать `check_gate.py` CLI
- [ ] **5.11** Добавить тесты для скриптов
- [ ] **5.12** Обновить `settings.json` с реальными командами

---

## Проблема №6: Нет скрипта инициализации проекта

### Описание проблемы

Пользователь должен вручную создавать структуру директорий перед началом работы.
Это создаёт барьер входа и вероятность ошибок.

**Текущий процесс:**

```bash
# Пользователь должен вручную:
mkdir -p my-project/docs/prd
mkdir -p my-project/docs/architecture
mkdir -p my-project/docs/plans
mkdir -p my-project/docs/reports
mkdir -p my-project/services
# ... и так далее
```

**Влияние:**
- Высокий барьер входа
- Вероятность ошибок в структуре
- Потеря времени на рутину

### Решение проблемы №6

**Задача:** Создать скрипт инициализации проекта

**Использование:**

```bash
python scripts/init_project.py --name "my-mvp" --mode CREATE
python scripts/init_project.py --name "my-mvp" --mode FEATURE --existing-path /path/to/project
```

**Реализация:**

```python
# scripts/init_project.py
#!/usr/bin/env python3
"""
Скрипт инициализации нового AIDD-MVP проекта.

Создаёт структуру директорий и базовые файлы для начала работы.
"""

import argparse
import shutil
from pathlib import Path
from datetime import date


DIRS_CREATE_MODE = [
    "docs/prd",
    "docs/architecture",
    "docs/plans",
    "docs/reports",
    "services",
    ".claude",
]

DIRS_FEATURE_MODE = [
    "docs/prd",
    "docs/plans",
    "docs/reports",
]


def create_project(name: str, mode: str, base_path: Path = None):
    """
    Создаёт структуру проекта.

    Args:
        name: Название проекта
        mode: Режим (CREATE или FEATURE)
        base_path: Базовый путь (для FEATURE режима)
    """
    if mode == "CREATE":
        project_path = Path(name)
        project_path.mkdir(exist_ok=True)

        for dir_path in DIRS_CREATE_MODE:
            (project_path / dir_path).mkdir(parents=True, exist_ok=True)

        # Создать CLAUDE.md
        create_claude_md(project_path, name)

        # Создать .gitignore
        create_gitignore(project_path)

        # Копировать settings.json
        copy_settings(project_path)

        print(f"✅ Проект '{name}' создан")
        print(f"📁 Путь: {project_path.absolute()}")
        print(f"\n🚀 Следующий шаг:")
        print(f'   /idea "Описание вашей идеи"')

    elif mode == "FEATURE":
        if not base_path:
            raise ValueError("Для режима FEATURE требуется --existing-path")

        project_path = Path(base_path)

        for dir_path in DIRS_FEATURE_MODE:
            (project_path / dir_path).mkdir(parents=True, exist_ok=True)

        print(f"✅ Структура для фичи '{name}' создана")


def create_claude_md(path: Path, name: str):
    """Создаёт CLAUDE.md файл."""
    content = f'''# CLAUDE.md — {name}

> Этот файл — точка входа для AI-агента.

## Проект

- **Название**: {name}
- **Дата создания**: {date.today().isoformat()}
- **Режим**: CREATE

## Документация

1. Прочитай `conventions.md` — соглашения о коде
2. Прочитай `workflow.md` — процесс разработки
3. Используй `/idea` для начала работы

## Ссылки

- [Conventions](conventions.md)
- [Workflow](workflow.md)
'''
    (path / "CLAUDE.md").write_text(content)


def create_gitignore(path: Path):
    """Создаёт .gitignore файл."""
    content = '''# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Environment
.env
*.secret

# IDE
.idea/
.vscode/

# Docker
*.log
'''
    (path / ".gitignore").write_text(content)


def copy_settings(path: Path):
    """Копирует settings.json."""
    # Логика копирования из шаблона
    pass


def main():
    parser = argparse.ArgumentParser(
        description="Инициализация AIDD-MVP проекта"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Название проекта"
    )
    parser.add_argument(
        "--mode",
        choices=["CREATE", "FEATURE"],
        default="CREATE",
        help="Режим: CREATE (новый) или FEATURE (добавление)"
    )
    parser.add_argument(
        "--existing-path",
        help="Путь к существующему проекту (для режима FEATURE)"
    )

    args = parser.parse_args()

    create_project(
        name=args.name,
        mode=args.mode,
        base_path=args.existing_path
    )


if __name__ == "__main__":
    main()
```

**Задачи:**

- [ ] **6.1** Создать `scripts/init_project.py`
- [ ] **6.2** Добавить шаблоны для копирования (CLAUDE.md, .gitignore)
- [ ] **6.3** Добавить поддержку режима FEATURE
- [ ] **6.4** Добавить тесты
- [ ] **6.5** Обновить документацию (README.md)

---

# НЕЗНАЧИТЕЛЬНЫЕ ПРОБЛЕМЫ (🟢)

---

## Проблема №7: RTM путь неоднозначен

### Описание проблемы

Requirements Traceability Matrix (RTM) упоминается с разными путями:

| Файл | Указанный путь |
|------|----------------|
| `templates/documents/README.md` | `ai-docs/rtm.md` |
| `workflow.md` | `docs/rtm.md` |
| `.claude/agents/analyst.md` | `docs/rtm.md` |

**Влияние:** Путаница с местом хранения RTM.

### Решение проблемы №7

**Стандарт:** `docs/rtm.md`

**Задачи:**

- [ ] **7.1** Обновить `templates/documents/README.md`:
  ```
  БЫЛО:  ai-docs/rtm.md
  СТАЛО: docs/rtm.md
  ```

- [ ] **7.2** Проверить все ссылки на RTM:
  ```bash
  grep -r "rtm.md" --include="*.md"
  ```

---

## Проблема №8: Нет версионирования шаблонов

### Описание проблемы

Шаблоны в `templates/documents/` и `templates/services/` не имеют версий.
При изменении шаблона нет возможности отследить историю.

**Влияние:**
- Сложно понять, какая версия использовалась
- Нет changelog для шаблонов

### Решение проблемы №8

**Задачи:**

- [ ] **8.1** Добавить версию в каждый шаблон:
  ```markdown
  **Версия шаблона**: 1.0.0
  **Последнее обновление**: 2025-12-19
  ```

- [ ] **8.2** Создать `templates/documents/CHANGELOG.md`

- [ ] **8.3** Добавить версию в шаблоны сервисов:
  ```python
  # templates/services/fastapi_business_api/src/core/config.py
  TEMPLATE_VERSION = "1.0.0"
  ```

---

## Проблема №9: Дублирование информации agent/role

### Описание проблемы

Файлы агентов (`.claude/agents/*.md`) содержат информацию, которая
дублируется в файлах ролей (`roles/**/*.md`).

**Пример дублирования:**

| Информация | .claude/agents/analyst.md | roles/analyst/*.md |
|------------|---------------------------|-------------------|
| Входные данные | ✓ | ✓ |
| Выходные данные | ✓ | ✓ |
| Инструкции | Краткие | Детальные |
| Качественные ворота | ✓ | ✓ |

**Влияние:**
- При изменении нужно обновлять оба места
- Риск рассинхронизации

### Решение проблемы №9

**Подход:** Агенты — точка входа, роли — детали.

**Задачи:**

- [ ] **9.1** Рефакторинг агентов:
  - Оставить только краткое описание
  - Убрать детальные инструкции
  - Добавить ссылки на `roles/`

- [ ] **9.2** Шаблон для агента:
  ```markdown
  # Роль: {Название}

  > **Назначение**: {Одно предложение}

  ## Входные данные
  {Таблица}

  ## Выходные данные
  {Таблица}

  ## Качественные ворота
  {Название ворот}

  ## Детальные инструкции
  → См. `roles/{role}/`
  ```

- [ ] **9.3** Применить шаблон ко всем агентам

---

# ПОРЯДОК ВЫПОЛНЕНИЯ

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ПРИОРИТЕТ ВЫПОЛНЕНИЯ                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  КРИТИЧЕСКИЕ (сначала):                                                  │
│  ├── Проблема #1: Унификация путей (~2 часа)                            │
│  ├── Проблема #3: Ссылки на шаблон PRD (~30 мин)                        │
│  └── Проблема #2: Создать metrics.md (~1 час)                           │
│                                                                          │
│  ВАЖНЫЕ (после критических):                                             │
│  ├── Проблема #6: Скрипт инициализации (~2 часа)                        │
│  ├── Проблема #5: Автоматизация Gates (~4 часа)                         │
│  └── Проблема #4: Пример проекта (~6 часов)                             │
│                                                                          │
│  НЕЗНАЧИТЕЛЬНЫЕ (по возможности):                                        │
│  ├── Проблема #7: RTM путь (~30 мин)                                    │
│  ├── Проблема #8: Версионирование (~1 час)                              │
│  └── Проблема #9: Дедупликация agent/role (~2 часа)                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

Общее время: ~19 часов
```

---

# ЧЕКЛИСТ ВЫПОЛНЕНИЯ

## Критические

- [ ] **#1** Унификация путей (16 файлов)
  - [ ] 1.1 templates/documents/README.md
  - [ ] 1.2 roles/ (11 файлов)
  - [ ] 1.3 knowledge/architecture/project-structure.md
  - [ ] 1.4 templates/documents/validation-report-template.md
  - [ ] 1.5 Создать директории

- [ ] **#2** Создать metrics.md
  - [ ] 2.1 roles/implementer/metrics.md
  - [ ] 2.2 Обновить implementer.md
  - [ ] 2.3 knowledge/quality/metrics/prometheus-setup.md
  - [ ] 2.4 knowledge/quality/metrics/custom-metrics.md

- [ ] **#3** Исправить ссылки на PRD
  - [ ] 3.1 .claude/agents/analyst.md
  - [ ] 3.2 roles/analyst/prd-formation.md
  - [ ] 3.3 Проверить другие файлы

## Важные

- [ ] **#4** Создать пример проекта
  - [ ] 4.1-4.10 (см. детали выше)

- [ ] **#5** Автоматизация Quality Gates
  - [ ] 5.1-5.12 (см. детали выше)

- [ ] **#6** Скрипт инициализации
  - [ ] 6.1-6.5 (см. детали выше)

## Незначительные

- [ ] **#7** RTM путь
  - [ ] 7.1-7.2

- [ ] **#8** Версионирование
  - [ ] 8.1-8.3

- [ ] **#9** Дедупликация
  - [ ] 9.1-9.3

---

**Создано**: 2025-12-19
**Автор**: AI Agent
