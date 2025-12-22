# Функция: Проверка артефактов

> **Назначение**: Верификация наличия и полноты всех артефактов.

---

## Цель

Проверить, что все артефакты, созданные на этапах пайплайна,
существуют, актуальны и соответствуют требованиям.

---

## Список артефактов

### Документация (ai-docs/)

| Артефакт | Путь | Этап | Обязательный |
|----------|------|------|--------------|
| PRD | `ai-docs/docs/prd/{name}-prd.md` | Анализ | Да |
| Research Report | `ai-docs/docs/research/{name}-research.md` | Исследование | Да |
| Architecture | `ai-docs/docs/architecture/{name}-arch.md` | Архитектура | Да |
| Implementation Plan | `ai-docs/docs/plans/{name}-plan.md` | Архитектура | Да |
| Review Report | `ai-docs/docs/reports/review-report.md` | Ревью | Да |
| QA Report | `ai-docs/docs/reports/qa-report.md` | QA | Да |
| RTM | `ai-docs/docs/rtm.md` | Все этапы | Да |

### Код (services/)

| Артефакт | Путь | Описание |
|----------|------|----------|
| Business API | `services/{context}_api/` | REST API сервис |
| Data API | `services/{context}_data/` | Сервис данных |
| Telegram Bot | `services/{context}_bot/` | Бот (опционально) |
| Background Worker | `services/{context}_worker/` | Воркер (опционально) |

### Инфраструктура

| Артефакт | Путь | Описание |
|----------|------|----------|
| Docker Compose | `docker-compose.yml` | Основная конфигурация |
| Docker Compose Dev | `docker-compose.dev.yml` | Dev overrides |
| Environment | `.env.example` | Пример переменных |
| Makefile | `Makefile` | Команды |
| CI Pipeline | `.github/workflows/ci.yml` | CI конфигурация |

### Тесты

| Артефакт | Путь | Описание |
|----------|------|----------|
| Unit Tests | `services/*/tests/unit/` | Unit тесты |
| Integration Tests | `services/*/tests/integration/` | Integration тесты |
| conftest.py | `services/*/tests/conftest.py` | Фикстуры |
| Coverage Report | `htmlcov/` | HTML отчёт |

---

## Процесс верификации

### Шаг 1: Проверка документации

```bash
# Проверить наличие документов

# PRD
if [ -f "ai-docs/docs/prd/*-prd.md" ]; then
    echo "✓ PRD exists"
else
    echo "✗ PRD missing"
fi

# Research Report
if ls ai-docs/docs/research/*-research.md >/dev/null 2>&1; then
    echo "✓ Research Report exists"
else
    echo "✗ Research Report missing"
fi

# Architecture
if [ -f "ai-docs/docs/architecture/*-arch.md" ]; then
    echo "✓ Architecture exists"
else
    echo "✗ Architecture missing"
fi

# Plan
if [ -f "ai-docs/docs/plans/*-plan.md" ]; then
    echo "✓ Plan exists"
else
    echo "✗ Plan missing"
fi

# Reports
ls ai-docs/docs/reports/

# RTM
if [ -f "ai-docs/docs/rtm.md" ]; then
    echo "✓ RTM exists"
else
    echo "✗ RTM missing"
fi
```

### Шаг 2: Проверка кода

```bash
# Проверить структуру сервисов

for service in services/*/; do
    echo "Checking $service..."

    # Основные файлы
    [ -f "$service/Dockerfile" ] && echo "  ✓ Dockerfile" || echo "  ✗ Dockerfile"
    [ -f "$service/requirements.txt" ] && echo "  ✓ requirements.txt" || echo "  ✗ requirements.txt"
    [ -d "$service/src/" ] && echo "  ✓ src/" || echo "  ✗ src/"
    [ -d "$service/tests/" ] && echo "  ✓ tests/" || echo "  ✗ tests/"
done
```

### Шаг 3: Проверка инфраструктуры

```bash
# Проверить инфраструктурные файлы

[ -f "docker-compose.yml" ] && echo "✓ docker-compose.yml" || echo "✗ docker-compose.yml"
[ -f "docker-compose.dev.yml" ] && echo "✓ docker-compose.dev.yml" || echo "✗ docker-compose.dev.yml"
[ -f ".env.example" ] && echo "✓ .env.example" || echo "✗ .env.example"
[ -f "Makefile" ] && echo "✓ Makefile" || echo "✗ Makefile"
[ -f ".github/workflows/ci.yml" ] && echo "✓ CI Pipeline" || echo "✗ CI Pipeline"
```

### Шаг 4: Валидация содержимого

```python
# Псевдокод валидации содержимого

def validate_prd(path):
    """Проверить структуру PRD."""
    content = read(path)

    required_sections = [
        "## 1. Обзор",
        "## 2. Функциональные требования",
        "## 3. UI/UX требования",
        "## 4. Нефункциональные требования",
        "## 5. Ограничения",
    ]

    for section in required_sections:
        if section not in content:
            return False, f"Missing section: {section}"

    # Проверка ID требований
    if not re.search(r"FR-\d{3}", content):
        return False, "No FR IDs found"

    return True, "Valid"


def validate_rtm(path):
    """Проверить RTM."""
    content = read(path)

    # Должна содержать все FR из PRD
    prd = read("ai-docs/docs/prd/*.md")
    fr_ids = extract_fr_ids(prd)

    for fr_id in fr_ids:
        if fr_id not in content:
            return False, f"Missing {fr_id} in RTM"

    return True, "Valid"
```

---

## Чек-лист артефактов

### Документация

- [ ] PRD существует и содержит все секции
- [ ] Architecture документ существует
- [ ] Implementation Plan существует
- [ ] Review Report существует
- [ ] QA Report существует
- [ ] RTM существует и актуальна

### Код

- [ ] Business API сервис создан
- [ ] Data API сервис создан
- [ ] Telegram Bot создан (если требуется)
- [ ] Background Worker создан (если требуется)
- [ ] Все сервисы имеют Dockerfile
- [ ] Все сервисы имеют tests/

### Инфраструктура

- [ ] docker-compose.yml существует и валиден
- [ ] docker-compose.dev.yml существует
- [ ] .env.example содержит все переменные
- [ ] Makefile содержит основные команды
- [ ] CI pipeline настроен

### Тесты

- [ ] Unit тесты существуют для всех сервисов
- [ ] Integration тесты существуют
- [ ] Coverage report сгенерирован
- [ ] Coverage ≥75%

---

## Результат проверки

```markdown
## Верификация артефактов

### Общий статус: COMPLETE / INCOMPLETE

### Документация

| Артефакт | Статус | Путь | Комментарий |
|----------|--------|------|-------------|
| PRD | ✓ | ai-docs/docs/prd/booking-prd.md | — |
| Architecture | ✓ | ai-docs/docs/architecture/booking-arch.md | — |
| Plan | ✓ | ai-docs/docs/plans/booking-plan.md | — |
| Review Report | ✓ | ai-docs/docs/reports/review-report.md | — |
| QA Report | ✓ | ai-docs/docs/reports/qa-report.md | — |
| RTM | ✓ | ai-docs/docs/rtm.md | Актуальна |

### Код

| Сервис | Статус | Dockerfile | Tests | Комментарий |
|--------|--------|------------|-------|-------------|
| booking_api | ✓ | ✓ | ✓ | — |
| booking_data | ✓ | ✓ | ✓ | — |
| booking_bot | ✓ | ✓ | ✓ | — |

### Инфраструктура

| Артефакт | Статус | Комментарий |
|----------|--------|-------------|
| docker-compose.yml | ✓ | Валиден |
| docker-compose.dev.yml | ✓ | — |
| .env.example | ✓ | 15 переменных |
| Makefile | ✓ | 20 команд |
| CI Pipeline | ✓ | — |

### Отсутствующие артефакты

| # | Артефакт | Причина | Действие |
|---|----------|---------|----------|
| — | Нет отсутствующих | — | — |
```

---

## Критерии прохождения

```
COMPLETE:
- Все обязательные артефакты существуют
- Документы содержат требуемые секции
- Код соответствует структуре
- Тесты присутствуют

INCOMPLETE:
- Отсутствует хотя бы один обязательный артефакт
- Документ не содержит обязательных секций
- Сервис не имеет тестов
```

---

## Источники

| Документ | Описание |
|----------|----------|
| `workflow.md` | Описание артефактов по этапам |
| `knowledge/architecture/project-structure.md` | Структура проекта |
