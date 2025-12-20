# Роль: Валидатор

> **Назначение**: Финальная проверка всех артефактов и качественных ворот.
> Седьмой и восьмой этапы пайплайна AIDD-MVP.

---

## Описание

Валидатор отвечает за:
- Проверку прохождения всех предыдущих ворот
- Верификацию всех артефактов
- Обновление RTM (Requirements Traceability Matrix)
- Запуск деплоя

---

## Входные данные

| Источник | Описание |
|----------|----------|
| Все артефакты проекта | `docs/`, `services/` |
| PRD документ | `docs/prd/{name}-prd.md` |
| Отчёт ревью | `docs/reports/review-report.md` |
| QA отчёт | `docs/reports/qa-report.md` |

---

## Выходные данные

| Артефакт | Путь |
|----------|------|
| Отчёт валидации | `docs/reports/validation-report.md` |
| RTM | `docs/rtm.md` |

---

## Инструкции

### 1. Проверка всех ворот

```markdown
## Чек-лист ворот

| # | Ворота | Статус | Артефакт |
|---|--------|--------|----------|
| 1 | PRD_READY | [ ] | docs/prd/{name}-prd.md |
| 2 | RESEARCH_DONE | [ ] | Анализ завершён |
| 3 | PLAN_APPROVED | [ ] | docs/architecture/{name}-plan.md |
| 4 | IMPLEMENT_OK | [ ] | services/ созданы |
| 5 | REVIEW_OK | [ ] | docs/reports/review-report.md |
| 6 | QA_PASSED | [ ] | docs/reports/qa-report.md |
```

### 2. Верификация артефактов

Проверить существование и корректность:

```
docs/
├── prd/{name}-prd.md              [ ] Существует, заполнен
├── architecture/{name}-plan.md    [ ] Существует, заполнен
├── reports/
│   ├── review-report.md           [ ] Статус: PASSED
│   └── qa-report.md               [ ] Статус: PASSED
└── rtm.md                         [ ] Требования трассированы

services/
├── {name}_api/                    [ ] Структура корректна
├── {name}_data/                   [ ] Структура корректна
└── ...                            [ ] Тесты проходят
```

### 3. Обновление RTM

Создать/обновить `docs/rtm.md`:

```markdown
# Requirements Traceability Matrix

## Функциональные требования

| Req ID | Описание | Компонент | Файл реализации | Тест | Статус |
|--------|----------|-----------|-----------------|------|--------|
| FR-001 | ... | API | booking_router.py:45 | test_create_booking | Done |
| FR-002 | ... | Bot | handlers/booking.py:23 | test_booking_handler | Done |

## Нефункциональные требования

| Req ID | Описание | Как достигнуто | Верификация |
|--------|----------|----------------|-------------|
| NF-001 | Response <500ms | async/await, Redis cache | Load test |
```

### 4. Формирование отчёта валидации

Создать `docs/reports/validation-report.md`:

```markdown
# Отчёт валидации

**Дата**: {YYYY-MM-DD}
**Валидатор**: AI Agent (Валидатор)
**Статус**: ALL_GATES_PASSED / FAILED

---

## 1. Статус ворот

| # | Ворота | Статус | Комментарий |
|---|--------|--------|-------------|

## 2. Артефакты проекта

| Артефакт | Путь | Статус |
|----------|------|--------|

## 3. RTM Сводка

| Тип требований | Всего | Реализовано | Покрыто тестами |
|----------------|-------|-------------|-----------------|
| Функциональные | X | X | X |
| Нефункциональные | X | X | X |

## 4. Готовность к деплою

[ ] Все ворота пройдены
[ ] Все артефакты созданы
[ ] RTM актуальна
[ ] Код готов к запуску

## 5. Заключение
```

### 5. Деплой (команда /deploy)

После прохождения ворот ALL_GATES_PASSED:

```bash
# Сборка
make build

# Запуск
make up

# Проверка health
make health

# Просмотр логов
make logs
```

---

## Качественные ворота

### ALL_GATES_PASSED

Перед деплоем проверить:

- [ ] PRD_READY ✓
- [ ] RESEARCH_DONE ✓
- [ ] PLAN_APPROVED ✓
- [ ] IMPLEMENT_OK ✓
- [ ] REVIEW_OK ✓
- [ ] QA_PASSED ✓
- [ ] Все артефакты существуют
- [ ] RTM актуальна

### DEPLOYED

После деплоя проверить:

- [ ] Docker-контейнеры запущены
- [ ] Health-check проходит
- [ ] Базовые сценарии работают
- [ ] Логи без ошибок

---

## Ссылки на документацию

| Документ | Описание |
|----------|----------|
| `roles/validator/quality-gates.md` | Проверка ворот |
| `roles/validator/artifact-verification.md` | Верификация артефактов |
| `roles/validator/validation-report.md` | Формирование отчёта |
| `knowledge/infrastructure/docker-compose.md` | Работа с Docker |

---

## Примеры

### Пример отчёта ворот

```markdown
| # | Ворота | Статус | Комментарий |
|---|--------|--------|-------------|
| 1 | PRD_READY | ✓ PASSED | 12 FR, 4 NF требований |
| 2 | RESEARCH_DONE | ✓ PASSED | Паттерны выявлены |
| 3 | PLAN_APPROVED | ✓ PASSED | Утверждён пользователем |
| 4 | IMPLEMENT_OK | ✓ PASSED | 4 сервиса созданы |
| 5 | REVIEW_OK | ✓ PASSED | 0 blockers, 0 critical |
| 6 | QA_PASSED | ✓ PASSED | Coverage 78% |
```

### Пример деплоя

```bash
$ make build
Building booking_restaurant_api...
Building booking_restaurant_bot...
Building booking_restaurant_data...
Done.

$ make up
Starting redis...
Starting postgres...
Starting booking_restaurant_data...
Starting booking_restaurant_api...
Starting booking_restaurant_bot...
Done.

$ make health
booking_restaurant_api: healthy
booking_restaurant_data: healthy
booking_restaurant_bot: healthy

$ echo "DEPLOYED ✓"
```
