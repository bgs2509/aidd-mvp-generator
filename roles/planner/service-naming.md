# Функция: Именование сервисов

> **Назначение**: Определение имён сервисов и компонентов.

---

## Цель

Выбрать консистентные и понятные имена для всех
компонентов системы согласно конвенциям фреймворка.

---

## Соглашения об именовании

### Контекст проекта

```
{context} — короткое имя проекта (2-15 символов)

Примеры:
- booking (бронирование)
- finance (финансы)
- inventory (инвентарь)
- orders (заказы)
```

### Домен

```
{domain} — основная сущность домена

Примеры:
- restaurant (ресторан)
- transaction (транзакция)
- product (продукт)
- order (заказ)
```

---

## Паттерны именования

### Сервисы

| Тип | Паттерн | Пример |
|-----|---------|--------|
| Business API | `{context}_api` | `booking_api` |
| Data API (PG) | `{context}_data` | `booking_data` |
| Data API (Mongo) | `{context}_docs` | `booking_docs` |
| Telegram Bot | `{context}_bot` | `booking_bot` |
| Background Worker | `{context}_worker` | `booking_worker` |

### Docker сервисы

| Тип | Паттерн | Пример |
|-----|---------|--------|
| Business API | `{context}-api` | `booking-api` |
| Data API | `{context}-data` | `booking-data` |
| PostgreSQL | `{context}-postgres` | `booking-postgres` |
| MongoDB | `{context}-mongo` | `booking-mongo` |
| Redis | `{context}-redis` | `booking-redis` |
| Bot | `{context}-bot` | `booking-bot` |
| Worker | `{context}-worker` | `booking-worker` |

### Директории

```
services/
├── {context}_api/           # Business API
│   └── src/
│       └── {context}_api/   # Python пакет
├── {context}_data/          # Data API
│   └── src/
│       └── {context}_data/
├── {context}_bot/           # Telegram Bot
│   └── src/
│       └── {context}_bot/
└── {context}_worker/        # Background Worker
    └── src/
        └── {context}_worker/
```

### Python пакеты

| Элемент | Стиль | Пример |
|---------|-------|--------|
| Пакет | snake_case | `booking_api` |
| Модуль | snake_case | `user_service.py` |
| Класс | PascalCase | `UserService` |
| Функция | snake_case | `create_user` |
| Переменная | snake_case | `user_id` |
| Константа | UPPER_SNAKE | `MAX_RETRIES` |

### API эндпоинты

| Элемент | Стиль | Пример |
|---------|-------|--------|
| Путь | kebab-case | `/api/v1/user-profiles` |
| Query параметр | snake_case | `?user_id=123` |
| Body поле | snake_case | `{"user_name": "..."}` |

### База данных

| Элемент | Стиль | Пример |
|---------|-------|--------|
| Таблица | snake_case, множ. | `users`, `order_items` |
| Колонка | snake_case | `created_at` |
| Индекс | `ix_{table}_{column}` | `ix_users_email` |
| FK | `fk_{table}_{ref}` | `fk_orders_user_id` |

---

## Процесс именования

### Шаг 1: Определить контекст

```markdown
Проект: Сервис бронирования столиков
Контекст: booking
Домен: restaurant
```

### Шаг 2: Определить сервисы

```markdown
| Сервис | Имя Python | Имя Docker | Порт |
|--------|------------|------------|------|
| Business API | booking_api | booking-api | 8000 |
| Data API | booking_data | booking-data | 8001 |
| Telegram Bot | booking_bot | booking-bot | — |
| PostgreSQL | — | booking-postgres | 5432 |
| Redis | — | booking-redis | 6379 |
```

### Шаг 3: Определить модели

```markdown
| Модель | Таблица | Класс |
|--------|---------|-------|
| Ресторан | restaurants | Restaurant |
| Бронирование | bookings | Booking |
| Пользователь | users | User |
```

### Шаг 4: Определить эндпоинты

```markdown
| Эндпоинт | Сервис | Путь |
|----------|--------|------|
| Список ресторанов | booking_api | /api/v1/restaurants |
| Создать бронь | booking_api | /api/v1/bookings |
| Получить ресторан | booking_data | /api/v1/restaurants/{id} |
```

---

## Чек-лист именования

### Сервисы
- [ ] Контекст определён (2-15 символов, snake_case)
- [ ] Все сервисы используют паттерн `{context}_{type}`
- [ ] Docker сервисы используют паттерн `{context}-{type}`
- [ ] Порты не конфликтуют

### Python код
- [ ] Пакеты в snake_case
- [ ] Классы в PascalCase
- [ ] Функции в snake_case
- [ ] Константы в UPPER_SNAKE_CASE

### API
- [ ] Пути в kebab-case
- [ ] Параметры в snake_case
- [ ] Версионирование (/api/v1/)

### База данных
- [ ] Таблицы в snake_case, множественное число
- [ ] Колонки в snake_case
- [ ] Индексы по паттерну ix_{table}_{column}

---

## Результат именования

```markdown
## Контекст проекта

| Параметр | Значение |
|----------|----------|
| Контекст | {context} |
| Домен | {domain} |

## Сервисы

| Сервис | Python | Docker | Порт |
|--------|--------|--------|------|
| Business API | {context}_api | {context}-api | 8000 |
| Data API | {context}_data | {context}-data | 8001 |

## Модели данных

| Сущность | Таблица | Класс Python |
|----------|---------|--------------|
| {Entity} | {entities} | {Entity} |

## API эндпоинты

| Сервис | Префикс |
|--------|---------|
| Business API | /api/v1/{resource} |
| Data API | /api/v1/{resource} |
```

---

## Источники

| Документ | Описание |
|----------|----------|
| `knowledge/architecture/naming/README.md` | Общие правила |
| `knowledge/architecture/naming/services.md` | Именование сервисов |
| `knowledge/architecture/naming/python.md` | Python конвенции |
| `conventions.md` | Соглашения проекта |
