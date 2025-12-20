# Гибридная архитектура AIDD-MVP

> **Назначение**: Описание улучшенной гибридной архитектуры фреймворка.

---

## Обзор

AIDD-MVP использует гибридную архитектуру, сочетающую:
- **DDD (Domain-Driven Design)** — для организации бизнес-логики
- **Hexagonal Architecture** — для изоляции от внешних зависимостей
- **HTTP-only Data Access** — для разделения сервисов

---

## Основные принципы

### 1. Разделение на сервисы

```
┌─────────────────────────────────────────────────────────────┐
│                    AIDD-MVP Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Business API │    │ Telegram Bot │    │   Worker     │  │
│  │  (FastAPI)   │    │  (aiogram)   │    │  (asyncio)   │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │           │
│         │     HTTP calls    │                   │           │
│         └───────────────────┼───────────────────┘           │
│                             │                               │
│                             ▼                               │
│                    ┌──────────────┐                        │
│                    │   Data API   │                        │
│                    │  (FastAPI)   │                        │
│                    └──────┬───────┘                        │
│                           │                                │
│                           │ SQL                            │
│                           ▼                                │
│                    ┌──────────────┐                        │
│                    │  PostgreSQL  │                        │
│                    └──────────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2. HTTP-only доступ к данным

```
ПРАВИЛО: Бизнес-сервисы НИКОГДА не обращаются к БД напрямую.

Business API ──HTTP──▶ Data API ──SQL──▶ Database

Почему:
- Изоляция сервисов
- Независимое масштабирование
- Чёткие контракты (API)
- Упрощение тестирования
```

### 3. DDD внутри сервиса

```
service/
├── api/                 ← Входящий адаптер (HTTP)
│   └── v1/
│       └── routes.py
├── application/         ← Сервисы приложения
│   ├── services/
│   └── dtos/
├── domain/              ← Ядро (бизнес-логика)
│   ├── entities/
│   ├── value_objects/
│   └── services/
└── infrastructure/      ← Исходящие адаптеры
    └── http/            (HTTP клиенты, не SQL!)
```

---

## Компоненты системы

### Business API

```python
"""Сервис бизнес-логики."""

# Использует HTTP клиент для Data API
from infrastructure.http import DataApiClient

class OrderService:
    def __init__(self, data_client: DataApiClient):
        self.data_client = data_client

    async def create_order(self, data: CreateOrderDTO) -> Order:
        # Бизнес-логика
        validated = self.validate(data)

        # Сохранение через Data API (HTTP!)
        result = await self.data_client.create_order(validated)

        return Order.from_dict(result)
```

### Data API

```python
"""Сервис доступа к данным."""

# Единственный сервис с доступом к БД
from sqlalchemy.ext.asyncio import AsyncSession

class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> Order:
        order = Order(**data)
        self.session.add(order)
        await self.session.commit()
        return order
```

### Telegram Bot

```python
"""Telegram бот использует Business API."""

from infrastructure.http import BusinessApiClient

@router.message(Command("order"))
async def create_order(message: Message, api_client: BusinessApiClient):
    # Вызов бизнес-логики через HTTP
    result = await api_client.create_order({
        "user_id": message.from_user.id,
        "items": [...],
    })

    await message.answer(f"Заказ {result['id']} создан!")
```

---

## Преимущества

### 1. Изоляция

```
- Каждый сервис независим
- Можно менять реализацию внутри сервиса
- Чёткие границы ответственности
```

### 2. Масштабируемость

```
- Независимое масштабирование сервисов
- Data API может кэшировать результаты
- Business API можно дублировать
```

### 3. Тестируемость

```
- Моки для HTTP клиентов
- Изолированные unit тесты
- Integration тесты через HTTP
```

### 4. Maintainability

```
- Понятная структура
- Легко добавлять новые сервисы
- Минимальные зависимости между сервисами
```

---

## Правила архитектуры

### DO (Делать)

```
✓ Использовать HTTP клиенты для межсервисного взаимодействия
✓ Держать бизнес-логику в domain слое
✓ Определять чёткие API контракты
✓ Использовать DI для зависимостей
✓ Писать async код
```

### DON'T (Не делать)

```
✗ Импортировать SQLAlchemy в бизнес-сервисы
✗ Обращаться к БД напрямую из Business API
✗ Создавать циклические зависимости
✗ Смешивать слои DDD
✗ Использовать синхронный код в async приложении
```

---

## Порты по умолчанию

| Сервис | Порт | Описание |
|--------|------|----------|
| Business API | 8000 | REST API для клиентов |
| Data API | 8001 | Доступ к PostgreSQL |
| Data API Mongo | 8002 | Доступ к MongoDB |
| PostgreSQL | 5432 | Основная БД |
| MongoDB | 27017 | Документная БД |
| Redis | 6379 | Кэш, сессии |

---

## Связанные документы

| Документ | Описание |
|----------|----------|
| `ddd-hexagonal.md` | DDD и Hexagonal принципы |
| `data-access.md` | HTTP-only доступ к данным |
| `service-separation.md` | Разделение сервисов |
