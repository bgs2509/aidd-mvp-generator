# Соглашения об именовании

> **Назначение**: Единые правила именования в проекте.

---

## Общие принципы

```
1. Консистентность — одинаковые правила везде
2. Читаемость — понятные имена
3. Контекст — имя отражает назначение
```

---

## Сводная таблица

| Элемент | Стиль | Пример |
|---------|-------|--------|
| Python пакет | snake_case | `booking_api` |
| Python модуль | snake_case | `user_service.py` |
| Python класс | PascalCase | `UserService` |
| Python функция | snake_case | `create_user` |
| Python переменная | snake_case | `user_id` |
| Python константа | UPPER_SNAKE | `MAX_RETRIES` |
| Docker сервис | kebab-case | `booking-api` |
| API путь | kebab-case | `/api/v1/user-profiles` |
| Query параметр | snake_case | `?user_id=123` |
| JSON поле | snake_case | `{"user_name": "..."}` |
| Таблица БД | snake_case, мн.ч. | `users` |
| Колонка БД | snake_case | `created_at` |
| Переменная окружения | UPPER_SNAKE | `DATABASE_URL` |

---

## Контекст проекта

```
{context} — короткое имя проекта

Требования:
- 2-15 символов
- snake_case
- Описательное

Примеры:
- booking
- finance
- inventory
- orders
```

---

## Домен

```
{domain} — основная сущность

Требования:
- Существительное
- Единственное число
- snake_case

Примеры:
- restaurant
- transaction
- product
- order
```

---

## Детальные правила

- `services.md` — именование сервисов
- `python.md` — именование в Python

---

## Quick Reference

### Сервисы

```
Python пакет:  {context}_{type}     → booking_api
Docker:        {context}-{type}     → booking-api
Директория:    services/{context}_{type}/
```

### Модели

```
Класс:         {Entity}             → Restaurant
Таблица:       {entities}           → restaurants
Файл:          {entity}.py          → restaurant.py
```

### API

```
Путь:          /api/v1/{resources}  → /api/v1/restaurants
Эндпоинт:      POST /api/v1/{resources}/{id}
```

### Тесты

```
Файл:          test_{module}.py     → test_user_service.py
Класс:         Test{Feature}        → TestUserCreation
Функция:       test_{scenario}      → test_create_user_success
```
