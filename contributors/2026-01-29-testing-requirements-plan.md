# План: Новая система требований к тестированию

## Цель

Внедрить 4-уровневую систему требований к тестированию в пайплайн AIDD-MVP с гибридной структурой:
- Внутри сервиса: smoke/unit/integration
- Глобально: e2e (сквозные сценарии между сервисами)

| Уровень | Тип | Обязательность | Описание |
|---------|-----|----------------|----------|
| 1 | **Smoke** | ✅ ОБЯЗАТЕЛЬНО | 100% endpoints + контейнеры запускаются + health checks 200 + БД доступна |
| 2 | **Unit** | ❓ Спрашивать | Coverage ≥ {порог} (по умолчанию 75%) с моками |
| 3 | **Integration** | ❓ Спрашивать | Критические пайплайны с testcontainers для БД из PRD |
| 4 | **E2E** | ❓ Спрашивать | Сквозные сценарии взаимодействия сервисов |

---

## Файлы для изменения

### Этап 1: PRD (aidd-analyze)

| # | Файл | Изменение |
|---|------|-----------|
| 1 | `templates/documents/prd-template.md` | Добавить секцию 6.5 "Требования к тестированию" |
| 2 | `.claude/commands/aidd-analyze.md` | Добавить вопросы пользователю о unit/integration/e2e |
| 3 | `.claude/agents/analyst.md` | Инструкции по сбору требований к тестированию |

### Этап 2: Research (aidd-research)

| # | Файл | Изменение |
|---|------|-----------|
| 4 | `templates/documents/research-report-template.md` | Секция "Анализ существующих тестов" |
| 5 | `.claude/commands/aidd-research.md` | Инструкция анализировать тесты |
| 6 | `.claude/agents/researcher.md` | Чеклист анализа тестов |

### Этап 3: Plan (aidd-plan / aidd-plan-feature)

| # | Файл | Изменение |
|---|------|-----------|
| 7 | `templates/documents/architecture-template.md` | Секция "План тестирования" |
| 8 | `.claude/commands/aidd-plan.md` | Пункт в чеклист о плане тестов |
| 9 | `.claude/commands/aidd-plan-feature.md` | Пункт в чеклист о плане тестов |
| 10 | `.claude/agents/planner.md` | Инструкции по планированию тестов |

### Этап 4: Code (aidd-code)

| # | Файл | Изменение |
|---|------|-----------|
| 11 | `.claude/commands/aidd-code.md` | Пункты в чеклист о реализации тестов |
| 12 | `.claude/agents/coder.md` | Инструкции по написанию тестов по плану |

### Этап 5: Validate (aidd-validate)

| # | Файл | Изменение |
|---|------|-----------|
| 13 | `.claude/commands/aidd-validate.md` | Верификация требований тестирования |
| 14 | `.claude/agents/validator.md` | Проверка соответствия PRD |
| 15 | `.claude/agents/testing-library.md` | Запуск тестов по категориям |

---

## Детальные изменения

### 1. PRD Template — Секция 6.5

**Файл**: `templates/documents/prd-template.md`

**Добавить после секции 6.4:**

```markdown
### 6.5 Требования к тестированию

#### Smoke тесты (ОБЯЗАТЕЛЬНО)
- [ ] 100% публичных endpoints имеют happy-path тест
- [ ] Все контейнеры запускаются без ошибок
- [ ] Health checks отвечают 200
- [ ] Базы данных доступны и отвечают

#### Unit тесты
- **Требуются**: {Да/Нет}
- **Порог покрытия**: {≥75%/другое}
- **Критические модули**: {список}

#### Integration тесты
- **Требуются**: {Да/Нет}
- **Критические пайплайны**: {список}
- **Тестовые БД**: testcontainers для {БД из PRD} (например PostgreSQL)

#### E2E тесты
- **Требуются**: {Да/Нет}
- **Сценарии межсервисных потоков**: {список}

#### Сводная таблица

| ID | Тип | Требование | Обязательно |
|----|-----|-----------|-------------|
| TRQ-001 | Smoke | 100% endpoints happy-path | ✅ Да |
| TRQ-002 | Smoke | Контейнеры запускаются | ✅ Да |
| TRQ-003 | Smoke | Health checks отвечают 200 | ✅ Да |
| TRQ-004 | Smoke | Базы данных доступны | ✅ Да |
| TRQ-005 | Unit | Coverage ≥ {порог} | {Да/Нет} |
| TRQ-006 | Integration | Критические пайплайны | {Да/Нет} |
| TRQ-007 | E2E | Сквозные сценарии | {Да/Нет} |
```

---

### 2. aidd-analyze — Вопросы пользователю

**Файл**: `.claude/commands/aidd-analyze.md`

**Добавить в секцию вопросов аналитика:**

```markdown
### Вопросы о тестировании

После сбора функциональных требований, задать пользователю:

1. **Unit тесты**: "Нужны ли unit тесты (coverage ≥ {порог} с моками)?"
   - Да → TRQ-005 = обязательно
   - Нет → TRQ-005 = не требуется

2. **Integration тесты**: "Нужны ли integration тесты для критических пайплайнов (с testcontainers для БД из PRD)?"
   - Да → TRQ-006 = обязательно, уточнить какие пайплайны
   - Нет → TRQ-006 = не требуется

3. **E2E тесты**: "Нужны ли E2E тесты (сквозные межсервисные сценарии)?"
   - Да → TRQ-007 = обязательно, уточнить сценарии
   - Нет → TRQ-007 = не требуется

**Smoke тесты (TRQ-001..TRQ-004) — ВСЕГДА обязательны, не спрашивать.**
```

**Добавить в чеклист PRD_READY:**

```markdown
- 🔴 Секция 6.5 "Требования к тестированию" заполнена
- 🔴 TRQ-001..TRQ-004 (smoke) отмечены как обязательные
- 🟡 Пользователь ответил на вопросы о unit/integration/e2e
```

---

### 3. Research Report — Анализ тестов

**Файл**: `templates/documents/research-report-template.md`

**Добавить секцию:**

```markdown
### 3.6 Анализ существующих тестов (FEATURE)

#### 3.6.1 Текущее состояние

| Тип | Найдено | Покрытие | Путь |
|-----|---------|----------|------|
| Smoke | {кол-во} | {%} | services/{service}/tests/smoke/ |
| Unit | {кол-во} | {%} | services/{service}/tests/unit/ |
| Integration | {кол-во} | {%} | services/{service}/tests/integration/ |
| E2E | {кол-во} | {%} | tests/e2e/ |

#### 3.6.2 Gaps (что нужно добавить)

На основе PRD секции 6.5:

| TRQ | Требование | Текущее | Нужно | Gap |
|-----|-----------|---------|-------|-----|
| TRQ-001 | 100% endpoints smoke | {X}% | 100% | +{Y} тестов |
| TRQ-002 | Контейнеры запускаются | {OK/Fail} | OK | {gap} |
| TRQ-003 | Health checks 200 | {X}/{Y} | 100% | +{Y} тестов |
| TRQ-004 | Базы данных доступны | {OK/Fail} | OK | {gap} |
| TRQ-005 | Coverage ≥ {порог} | {X}% | {порог}% | +{Y} тестов |
| TRQ-006 | Критические пайплайны | {X}/{Y} | 100% | +{Y} тестов |
| TRQ-007 | Сквозные сценарии | {X}/{Y} | 100% | +{Y} тестов |

#### 3.6.3 Рекомендации

- {Какие модули требуют тестов}
- {Какие зависимости нужно мокировать}
- {Какие пайплайны критичны для integration}
```

---

### 4. Architecture Template — План тестирования

**Файл**: `templates/documents/architecture-template.md`

**Добавить секцию:**

```markdown
## 9. План тестирования

### 9.1 Smoke тесты (обязательно, внутри сервисов)

| Сервис | Endpoint | Тест | Статус |
|--------|----------|------|--------|
| {api} | GET /health | test_health_check | План |
| {api} | POST /users | test_create_user_happy | План |

### 9.2 Unit тесты (если TRQ-005 = Да)

| Модуль | Функция | Тест | Моки |
|--------|---------|------|------|
| services/user | create_user() | test_create_user | DataApiClient |

### 9.3 Integration тесты (если TRQ-006 = Да)

| Пайплайн | Тест | Тестовая БД |
|----------|------|-------------|
| User registration | test_registration_flow | testcontainers для {БД из PRD} |

### 9.4 E2E тесты (если TRQ-007 = Да, глобально)

| Сценарий | Тест | Описание |
|----------|------|----------|
| {сценарий} | test_{name}_e2e | {описание} |
```

---

### 5. aidd-code — Реализация тестов

**Файл**: `.claude/commands/aidd-code.md`

**Добавить в чеклист IMPLEMENT_OK:**

```markdown
- 🔴 Smoke тесты реализованы (TRQ-001..TRQ-004)
- 🔴 Smoke тесты проходят
- 🟡 Unit тесты реализованы (TRQ-005, если требуется)
- 🟡 Integration тесты реализованы (TRQ-006, если требуется)
- ⚪ E2E тесты реализованы (TRQ-007, если требуется)
```

**Файл**: `.claude/agents/coder.md`

**Добавить/уточнить секцию Stage 4.6:**

```markdown
### Stage 4.6: Реализация тестов

Порядок реализации (последовательно):

1. **Smoke тесты** (ОБЯЗАТЕЛЬНО, внутри каждого сервиса)
   - services/{service}/tests/smoke/test_health.py — health checks
   - services/{service}/tests/smoke/test_containers.py — контейнеры запускаются
   - services/{service}/tests/smoke/test_endpoints_happy.py — 100% endpoints happy-path

2. **Unit тесты** (если TRQ-005 = Да)
   - services/{service}/tests/unit/ — coverage ≥ {порог}
   - Использовать AsyncMock для зависимостей

3. **Integration тесты** (если TRQ-006 = Да)
   - services/{service}/tests/integration/ — критические пайплайны
   - Использовать testcontainers для {БД из PRD}

4. **E2E тесты** (если TRQ-007 = Да, глобально)
   - tests/e2e/ — сквозные сценарии между сервисами
```

---

### 6. aidd-validate — Запуск и верификация

**Файл**: `.claude/commands/aidd-validate.md`

**Изменить Шаг 2 (Testing):**

```markdown
### Шаг 2: Testing

#### 2.1 Запуск тестов по категориям

```bash
# 1. Smoke (ОБЯЗАТЕЛЬНО, по сервисам)
for service in services/*; do
    pytest "$service/tests/smoke/" -v --tb=short
    # Должно быть: 100% passed
done

# 2. Unit (если TRQ-005 = Да, по сервисам)
for service in services/*; do
    pytest "$service/tests/unit/" -v --cov=src --cov-report=term
    # Проверить: coverage ≥ {порог}
done

# 3. Integration (если TRQ-006 = Да, по сервисам)
for service in services/*; do
    pytest "$service/tests/integration/" -v
    # Должно быть: 100% passed
done

# 4. E2E (если TRQ-007 = Да, глобально)
pytest tests/e2e/ -v
# Должно быть: 100% passed
```

#### 2.2 Верификация требований

| TRQ | Требование | Результат | Статус |
|-----|-----------|-----------|--------|
| TRQ-001 | 100% endpoints smoke | {X}/{Y} passed | ✅/❌ |
| TRQ-002 | Контейнеры запускаются | {passed/failed} | ✅/❌ |
| TRQ-003 | Health checks 200 | {X}/{Y} passed | ✅/❌ |
| TRQ-004 | Базы данных доступны | {passed/failed} | ✅/❌ |
| TRQ-005 | Coverage ≥ {порог} | {X}% coverage | ✅/❌/N/A |
| TRQ-006 | Integration критичных | {X}/{Y} passed | ✅/❌/N/A |
| TRQ-007 | E2E сценарии | {X}/{Y} passed | ✅/❌/N/A |
```

**Добавить в чеклист QA_PASSED:**

```markdown
- 🔴 TRQ-001: Все smoke тесты endpoints проходят
- 🔴 TRQ-002: Контейнеры запускаются успешно
- 🔴 TRQ-003: Health checks отвечают 200
- 🔴 TRQ-004: Базы данных доступны
- 🟡 TRQ-005: Unit coverage ≥ {порог} (если требуется)
- 🟡 TRQ-006: Integration тесты проходят (если требуется)
- ⚪ TRQ-007: E2E тесты проходят (если требуется)
```

---

## Структура тестов в целевом проекте

```
services/{service}/tests/
├── smoke/                    # ОБЯЗАТЕЛЬНО
│   ├── test_health.py        # Health checks
│   ├── test_containers.py    # Контейнеры запускаются
│   └── test_endpoints.py     # 100% endpoints happy-path
├── unit/                     # Если TRQ-005 = Да
│   └── test_*.py             # Coverage ≥ {порог}
└── integration/              # Если TRQ-006 = Да
    └── test_*.py             # Критические пайплайны

tests/
└── e2e/                      # Если TRQ-007 = Да
    └── test_*.py             # Сквозные сценарии между сервисами
```

---

## Порядок реализации

1. **PRD template + aidd-analyze** — определение требований
2. **Research template + aidd-research** — анализ существующих тестов
3. **Architecture template + aidd-plan** — планирование тестов
4. **aidd-code + coder** — реализация тестов
5. **aidd-validate + testing-library** — запуск и верификация

---

## Критерии успеха

- [ ] На этапе PRD пользователь отвечает на вопросы о тестировании
- [ ] Smoke тесты всегда обязательны (не спрашивать)
- [ ] Research показывает gaps в существующих тестах
- [ ] Plan содержит конкретный план тестов
- [ ] Code реализует тесты последовательно (smoke → unit → integration → e2e)
- [ ] Validate проверяет соответствие требованиям TRQ-*
