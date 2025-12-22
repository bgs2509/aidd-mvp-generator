# Функция: Проверка Quality Gates

> **Назначение**: Верификация прохождения всех качественных ворот.

---

## Цель

Проверить, что все качественные ворота пайплайна
были успешно пройдены перед релизом.

---

## Качественные ворота AIDD-MVP

### Полный список ворот

| # | Ворота | Этап | Описание |
|---|--------|------|----------|
| 1 | PRD_READY | Анализ | PRD документ готов |
| 2 | RESEARCH_DONE | Исследование | Анализ кода завершён |
| 3 | PLAN_APPROVED | Архитектура | План утверждён |
| 4 | IMPLEMENT_OK | Реализация | Код написан |
| 5 | REVIEW_OK | Ревью | Код прошёл ревью |
| 6 | QA_PASSED | Тестирование | Тесты прошли |
| 7 | ALL_GATES_PASSED | Валидация | Всё проверено |
| 8 | DEPLOYED | Деплой | Задеплоено |

---

## Критерии каждых ворот

### 1. PRD_READY

```markdown
Критерии:
- [ ] Все секции PRD заполнены
- [ ] Требования имеют уникальные ID
- [ ] Приоритеты расставлены (Must/Should/Could)
- [ ] Критерии приёмки определены для Must
- [ ] Нет блокирующих открытых вопросов

Артефакт: ai-docs/docs/prd/{name}-prd.md
```

### 2. RESEARCH_DONE

```markdown
Критерии:
- [ ] Структура кода проанализирована
- [ ] Паттерны идентифицированы
- [ ] Ограничения выявлены
- [ ] Пайплайн уточнён

Артефакт: ai-docs/docs/research/{name}-research.md
```

### 3. PLAN_APPROVED

```markdown
Критерии:
- [ ] Архитектура спроектирована
- [ ] Компоненты определены
- [ ] API контракты описаны
- [ ] Implementation Plan создан
- [ ] Трассировка требований есть

Артефакты:
- ai-docs/docs/architecture/{name}-arch.md
- ai-docs/docs/plans/{name}-plan.md
```

### 4. IMPLEMENT_OK

```markdown
Критерии:
- [ ] Все сервисы созданы по плану
- [ ] Код соответствует архитектуре
- [ ] Docker compose работает
- [ ] Health checks проходят
- [ ] Базовые тесты написаны

Артефакт: services/
```

### 5. REVIEW_OK

```markdown
Критерии:
- [ ] Архитектурные принципы соблюдены
- [ ] Конвенции соблюдены
- [ ] Нет критических проблем
- [ ] Автоматические проверки проходят

Артефакт: ai-docs/docs/reports/review-report.md
```

### 6. QA_PASSED

```markdown
Критерии:
- [ ] 100% тестов проходят
- [ ] Coverage ≥75%
- [ ] 100% Must требований покрыто тестами
- [ ] Нет критических дефектов
- [ ] CI pipeline проходит

Артефакт: ai-docs/docs/reports/qa-report.md
```

### 7. ALL_GATES_PASSED

```markdown
Критерии:
- [ ] Все предыдущие ворота пройдены
- [ ] RTM актуальна и полна
- [ ] Все артефакты на месте
- [ ] Нет открытых блокирующих вопросов

Артефакт: ai-docs/docs/reports/validation-report.md
```

### 8. DEPLOYED

```markdown
Критерии:
- [ ] Приложение задеплоено
- [ ] Smoke тесты прошли
- [ ] Мониторинг настроен (Level 3+)

Артефакт: Deployment URL / CI/CD logs
```

---

## Процесс верификации

### Шаг 1: Проверка артефактов

```bash
# Проверить наличие всех артефактов

# PRD
ls ai-docs/docs/prd/

# Архитектура
ls ai-docs/docs/architecture/

# План
ls ai-docs/docs/plans/

# Отчёты
ls ai-docs/docs/reports/

# RTM
cat ai-docs/docs/rtm.md
```

### Шаг 2: Проверка статусов

```markdown
## Статус ворот

| Ворота | Артефакт | Статус | Дата |
|--------|----------|--------|------|
| PRD_READY | prd.md | ✓ | 2024-01-10 |
| RESEARCH_DONE | research.md | ✓ | 2024-01-10 |
| PLAN_APPROVED | plan.md | ✓ | 2024-01-11 |
| IMPLEMENT_OK | services/ | ✓ | 2024-01-13 |
| REVIEW_OK | review-report.md | ✓ | 2024-01-14 |
| QA_PASSED | qa-report.md | ✓ | 2024-01-15 |
```

### Шаг 3: Валидация каждых ворот

```python
# Псевдокод валидации

def validate_prd_ready():
    prd = read("ai-docs/docs/prd/*.md")
    assert prd.has_all_sections()
    assert prd.requirements_have_ids()
    assert prd.no_blocking_questions()
    return True

def validate_implement_ok():
    services = glob("services/*/")
    for service in services:
        assert docker_compose_works(service)
        assert health_check_passes(service)
    return True

def validate_qa_passed():
    qa_report = read("ai-docs/docs/reports/qa-report.md")
    assert qa_report.status in ["PASSED", "PASSED_WITH_ISSUES"]
    assert qa_report.coverage >= 75
    assert qa_report.all_tests_pass()
    return True

def validate_all_gates():
    gates = [
        validate_prd_ready,
        validate_plan_approved,
        validate_implement_ok,
        validate_review_ok,
        validate_qa_passed,
    ]
    return all(gate() for gate in gates)
```

---

## Результат проверки

```markdown
## Верификация Quality Gates

### Общий статус: ALL_GATES_PASSED / BLOCKED

### Детальный статус

| Ворота | Статус | Артефакт | Комментарий |
|--------|--------|----------|-------------|
| PRD_READY | ✓ PASSED | prd.md | — |
| RESEARCH_DONE | ✓ PASSED | research.md | — |
| PLAN_APPROVED | ✓ PASSED | plan.md | — |
| IMPLEMENT_OK | ✓ PASSED | services/ | — |
| REVIEW_OK | ✓ PASSED | review-report.md | — |
| QA_PASSED | ✓ PASSED | qa-report.md | — |

### Блокирующие проблемы

| # | Ворота | Проблема | Действие |
|---|--------|----------|----------|
| — | — | Нет блокирующих проблем | — |
```

---

## Критерии прохождения

```
ALL_GATES_PASSED:
- Все 6 ворот (PRD → QA) пройдены
- Все артефакты существуют и актуальны
- Нет блокирующих проблем

BLOCKED:
- Хотя бы одни ворота не пройдены
- Отсутствует обязательный артефакт
- Есть блокирующие проблемы
```

---

## Источники

| Документ | Описание |
|----------|----------|
| `workflow.md` | Описание ворот |
| `.claude/settings.json` | Хуки для проверки |
