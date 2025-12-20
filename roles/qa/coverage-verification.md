# Функция: Верификация coverage

> **Назначение**: Проверка покрытия кода тестами и требований.

---

## Цель

Верифицировать, что покрытие кода и требований
соответствует стандартам Level 2 (MVP).

---

## Типы покрытия

### 1. Code Coverage (покрытие кода)

```
Метрика: Процент исполненных строк кода при тестах.

Требование Level 2: ≥75%

Инструменты:
- pytest-cov
- coverage.py
```

### 2. Requirements Coverage (покрытие требований)

```
Метрика: Процент требований, покрытых тестами.

Требование: 100% для Must, ≥80% для Should

Инструмент:
- RTM (Requirements Traceability Matrix)
```

---

## Процесс верификации

### Шаг 1: Измерение Code Coverage

```bash
# Запуск тестов с измерением покрытия
pytest --cov=src --cov-report=term --cov-report=html --cov-report=xml

# Проверка минимального порога
pytest --cov=src --cov-fail-under=75
```

### Шаг 2: Анализ отчёта о покрытии

```
---------- coverage: platform linux, python 3.11.x ----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/booking_api/__init__.py                 0      0   100%
src/booking_api/main.py                    25      2    92%
src/booking_api/api/v1/routes.py           45      3    93%
src/booking_api/application/services/      80      8    90%
src/booking_api/infrastructure/http/       40     10    75%
-----------------------------------------------------------
TOTAL                                     190     23    88%
```

### Шаг 3: Идентификация непокрытого кода

```bash
# Просмотр непокрытых строк
coverage report --show-missing

# HTML отчёт с подсветкой
coverage html
# Открыть htmlcov/index.html
```

### Шаг 4: Обновление RTM

```markdown
## Requirements Traceability Matrix

| Req ID | Описание | Реализация | Тест | Статус |
|--------|----------|------------|------|--------|
| FR-001 | Создание ресторана | api/v1/routes.py:45 | test_create_restaurant | ✓ |
| FR-002 | Список ресторанов | api/v1/routes.py:60 | test_list_restaurants | ✓ |
| FR-003 | Поиск ресторана | api/v1/routes.py:75 | test_search_restaurant | ✓ |
| NF-001 | Время отклика <500ms | — | test_response_time | ✓ |
| NF-003 | Coverage ≥75% | — | CI check | ✓ |
```

---

## Анализ результатов

### Code Coverage

```markdown
### Анализ покрытия кода

| Сервис | Покрытие | Статус | Комментарий |
|--------|----------|--------|-------------|
| {context}_api | 88% | ✓ PASSED | Выше порога |
| {context}_data | 92% | ✓ PASSED | Выше порога |
| {context}_bot | 72% | ✗ FAILED | Ниже порога (75%) |
| **Общее** | **84%** | **✓ PASSED** | — |

### Непокрытые области

| Файл | Строки | Причина | Действие |
|------|--------|---------|----------|
| http_client.py | 45-52 | Error handling | Добавить тесты |
| handlers.py | 80-95 | Edge cases | Добавить тесты |
```

### Requirements Coverage

```markdown
### Анализ покрытия требований

| Приоритет | Всего | Покрыто | Процент | Статус |
|-----------|-------|---------|---------|--------|
| Must | 10 | 10 | 100% | ✓ PASSED |
| Should | 5 | 4 | 80% | ✓ PASSED |
| Could | 3 | 2 | 67% | — (не требуется) |
| **Итого** | **18** | **16** | **89%** | — |

### Непокрытые требования

| Req ID | Описание | Причина | Действие |
|--------|----------|---------|----------|
| UI-003 | Анимация кнопок | Сложно тестировать | Ручное тестирование |
| FR-008 | Экспорт отчётов | Не реализовано | Отложено |
```

---

## Критерии прохождения

### Code Coverage

```
Level 2 (MVP):
✓ Общее покрытие ≥75%
✓ Критические модули ≥80%
✓ Нет файлов с 0% покрытием

Исключения:
- __init__.py
- Конфигурационные файлы
- Абстрактные классы
```

### Requirements Coverage

```
✓ 100% Must требований покрыто тестами
✓ ≥80% Should требований покрыто
✓ Could — по возможности
✓ RTM актуальна
```

---

## Улучшение покрытия

### Приоритизация

```
1. Критические пути (создание, удаление)
2. Бизнес-логика
3. Обработка ошибок
4. Edge cases
```

### Типичные области для улучшения

```python
# 1. Обработка ошибок
try:
    result = await api_client.get_entity(id)
except DataApiError:  # ← Добавить тест
    raise NotFoundError()

# 2. Граничные случаи
if items and len(items) > 0:  # ← Добавить тест для пустого списка
    process(items)

# 3. Негативные сценарии
if not is_valid(data):  # ← Добавить тест с невалидными данными
    raise ValidationError()
```

### Пример тестов для улучшения покрытия

```python
# test_error_handling.py

@pytest.mark.asyncio
async def test_get_entity_data_api_error():
    """Тест обработки ошибки Data API."""
    mock_client = AsyncMock()
    mock_client.get_entity.side_effect = DataApiError("Connection failed")

    service = EntityService(mock_client)

    with pytest.raises(NotFoundError):
        await service.get_entity(uuid4())


@pytest.mark.asyncio
async def test_empty_list():
    """Тест обработки пустого списка."""
    mock_client = AsyncMock()
    mock_client.list_entities.return_value = {"items": [], "total": 0}

    service = EntityService(mock_client)
    result = await service.list_entities()

    assert result.items == []
    assert result.total == 0
```

---

## Результат верификации

```markdown
## Верификация покрытия

### Статус: PASSED / FAILED

### Code Coverage

| Метрика | Значение | Порог | Статус |
|---------|----------|-------|--------|
| Общее покрытие | 84% | 75% | ✓ |
| Критические модули | 90% | 80% | ✓ |
| Файлы с 0% | 0 | 0 | ✓ |

### Requirements Coverage

| Метрика | Значение | Порог | Статус |
|---------|----------|-------|--------|
| Must требования | 100% | 100% | ✓ |
| Should требования | 80% | 80% | ✓ |
| Общее покрытие | 89% | — | — |

### Рекомендации

1. {Рекомендация по улучшению}
2. {Области для дополнительных тестов}
```

---

## Источники

| Документ | Описание |
|----------|----------|
| `docs/rtm-template.md` | Шаблон RTM |
| `workflow.md` | Требования Level 2 |
