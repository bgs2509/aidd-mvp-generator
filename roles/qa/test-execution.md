# Функция: Выполнение тестов

> **Назначение**: Запуск тестов и сбор результатов.

---

## Цель

Выполнить все тестовые сценарии и собрать результаты
для формирования QA отчёта.

---

## Инструменты тестирования

### pytest

```bash
# Основной инструмент для Python тестов

# Запуск всех тестов
pytest

# С подробным выводом
pytest -v

# Конкретный файл
pytest tests/unit/test_service.py

# Конкретный тест
pytest tests/unit/test_service.py::test_create_entity

# С покрытием
pytest --cov=src --cov-report=html

# Параллельный запуск
pytest -n auto
```

### Команды Makefile

```bash
# Все тесты всех сервисов
make test

# Тесты конкретного сервиса
make test-api
make test-data

# С покрытием
make coverage

# Unit тесты
make test-unit

# Integration тесты
make test-integration
```

---

## Процесс выполнения

### Шаг 1: Подготовка окружения

```bash
# Запустить все сервисы
make up

# Проверить статус
docker-compose ps

# Убедиться, что все healthy
curl http://localhost:8000/api/v1/health
curl http://localhost:8001/api/v1/health
```

### Шаг 2: Запуск Unit тестов

```bash
# Запуск unit тестов для каждого сервиса

# Business API
docker-compose exec {context}-api pytest tests/unit -v

# Data API
docker-compose exec {context}-data pytest tests/unit -v

# Bot (если есть)
docker-compose exec {context}-bot pytest tests/unit -v

# Worker (если есть)
docker-compose exec {context}-worker pytest tests/unit -v
```

### Шаг 3: Запуск Integration тестов

```bash
# Integration тесты требуют запущенных сервисов

# Business API
docker-compose exec {context}-api pytest tests/integration -v

# Data API
docker-compose exec {context}-data pytest tests/integration -v
```

### Шаг 4: Проверка покрытия

```bash
# Запуск с измерением покрытия
docker-compose exec {context}-api pytest --cov=src --cov-report=term --cov-report=html

# Проверка минимального покрытия (75%)
docker-compose exec {context}-api pytest --cov=src --cov-fail-under=75
```

### Шаг 5: Запуск линтеров

```bash
# Ruff (линтинг)
docker-compose exec {context}-api ruff check src tests

# Ruff (форматирование)
docker-compose exec {context}-api ruff format --check src tests

# Mypy (типы)
docker-compose exec {context}-api mypy src
```

---

## Сбор результатов

### Формат вывода pytest

```
==================== test session starts ====================
platform linux -- Python 3.11.x, pytest-7.x.x
plugins: asyncio-0.x.x, cov-4.x.x
collected 50 items

tests/unit/test_service.py::test_create_entity PASSED    [  2%]
tests/unit/test_service.py::test_get_entity PASSED       [  4%]
tests/unit/test_service.py::test_update_entity PASSED    [  6%]
...
tests/integration/test_api.py::test_full_flow PASSED     [100%]

==================== 50 passed in 5.23s ====================
```

### Формат отчёта о покрытии

```
---------- coverage: platform linux, python 3.11.x ----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/{context}_api/__init__.py               0      0   100%
src/{context}_api/main.py                  25      2    92%
src/{context}_api/api/v1/routes.py         45      3    93%
src/{context}_api/application/services/    80      8    90%
...
-----------------------------------------------------------
TOTAL                                     500     50    90%
```

---

## Обработка ошибок

### Падающий тест

```
FAILED tests/unit/test_service.py::test_create_entity

E   AssertionError: assert 'Expected' == 'Actual'
E     - Actual
E     + Expected

tests/unit/test_service.py:42: AssertionError
```

### Действия при падении

```
1. Записать упавший тест в отчёт
2. Определить причину:
   - Баг в коде → создать задачу на исправление
   - Баг в тесте → исправить тест
   - Изменились требования → обновить тест
3. Продолжить выполнение остальных тестов
```

---

## Таблица результатов

```markdown
## Результаты выполнения тестов

### Unit тесты

| Сервис | Всего | Passed | Failed | Skipped | Время |
|--------|-------|--------|--------|---------|-------|
| {context}_api | 30 | 30 | 0 | 0 | 2.1s |
| {context}_data | 25 | 25 | 0 | 0 | 1.8s |
| {context}_bot | 15 | 14 | 1 | 0 | 1.2s |
| **Итого** | **70** | **69** | **1** | **0** | **5.1s** |

### Integration тесты

| Сервис | Всего | Passed | Failed | Skipped | Время |
|--------|-------|--------|--------|---------|-------|
| {context}_api | 15 | 15 | 0 | 0 | 8.5s |
| {context}_data | 10 | 10 | 0 | 0 | 6.2s |
| **Итого** | **25** | **25** | **0** | **0** | **14.7s** |

### Покрытие кода

| Сервис | Statements | Missing | Coverage |
|--------|------------|---------|----------|
| {context}_api | 500 | 50 | 90% |
| {context}_data | 300 | 25 | 92% |
| {context}_bot | 200 | 30 | 85% |
| **Итого** | **1000** | **105** | **89%** |

### Линтеры

| Инструмент | Статус | Ошибок |
|------------|--------|--------|
| ruff check | PASSED | 0 |
| ruff format | PASSED | 0 |
| mypy | PASSED | 0 |
```

---

## Автоматизация в CI

### GitHub Actions

```yaml
# .github/workflows/ci.yml

jobs:
  test:
    steps:
      - name: Run unit tests
        run: pytest tests/unit -v --junitxml=junit-unit.xml

      - name: Run integration tests
        run: pytest tests/integration -v --junitxml=junit-integration.xml

      - name: Check coverage
        run: pytest --cov=src --cov-fail-under=75 --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

---

## Критерии успеха

### Минимальные требования (Level 2)

```
✓ Все unit тесты проходят
✓ Все integration тесты проходят
✓ Coverage ≥75%
✓ Линтеры проходят без ошибок
```

### Допустимые отклонения

```
- Skipped тесты допустимы с обоснованием
- Flaky тесты должны быть помечены и задокументированы
```

---

## Источники

| Документ | Описание |
|----------|----------|
| `knowledge/quality/testing/pytest-setup.md` | Настройка pytest |
| `roles/implementer/testing.md` | Создание тестов |
