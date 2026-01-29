# Функция: Выбор по уровню зрелости

> **Назначение**: Определение компонентов по уровню зрелости проекта.

---

## Цель

Выбрать правильный набор компонентов и практик
в зависимости от уровня зрелости проекта.

---

## Уровни зрелости

### Level 1: PoC (Proof of Concept)

```
Цель: Быстрая проверка идеи
Время: 1-2 дня

Компоненты:
├── Один сервис (монолит)
├── SQLite или JSON файлы
└── Минимальный UI

Что ВКЛЮЧЕНО:
- Базовая функциональность
- Простейшее хранилище
- Консольный или простой web интерфейс

Что ИСКЛЮЧЕНО:
- Docker
- Тесты
- Логирование
- CI/CD
```

### Level 2: MVP (Minimum Viable Product) ⭐ ОСНОВНОЙ

```
Цель: Первый продукт для пользователей
Время: 1-2 недели

Компоненты:
├── Business API (FastAPI)
├── Data API (PostgreSQL/MongoDB)
├── Telegram Bot (опционально)
├── Background Worker (опционально)
├── Redis (опционально)
└── Docker Compose

Что ВКЛЮЧЕНО:
✓ DDD/Hexagonal архитектура
✓ HTTP-only доступ к данным
✓ Docker контейнеризация
✓ Тесты (coverage ≥75%)
✓ Структурированное логирование
✓ CI pipeline (GitHub Actions)
✓ Базовая документация

Что ИСКЛЮЧЕНО:
✗ Prometheus/Grafana
✗ Nginx (прямой доступ к API)
✗ SSL сертификаты
✗ CD pipeline
✗ Rate limiting
✗ Распределённое трейсинг
```

### Level 3: Production

```
Цель: Готовность к продакшену
Время: 3-4 недели

Компоненты (добавляются к Level 2):
├── Nginx reverse proxy
├── SSL/TLS
├── Prometheus + Grafana
├── CD pipeline
└── Rate limiting

Что ДОБАВЛЕНО к Level 2:
+ Nginx как API Gateway
+ SSL сертификаты
+ Метрики (Prometheus)
+ Мониторинг (Grafana)
+ CD pipeline
+ Rate limiting
+ Health checks
```

### Level 4: Enterprise

```
Цель: Масштабируемость и отказоустойчивость
Время: 2+ месяца

Компоненты (добавляются к Level 3):
├── Kubernetes
├── Service Mesh (Istio)
├── Distributed Tracing (Jaeger)
├── Centralized Logging (ELK)
└── Multi-region deployment

Что ДОБАВЛЕНО к Level 3:
+ Kubernetes оркестрация
+ Горизонтальное масштабирование
+ Service mesh
+ Распределённый трейсинг
+ Централизованные логи
+ Multi-region
```

---

## AIDD-MVP Framework = Level 2

```
ВАЖНО: Этот фреймворк ВСЕГДА работает на Level 2 (MVP).

Почему:
1. MVP — оптимальный баланс качества и скорости
2. Достаточно для первых пользователей
3. Можно легко расширить до Level 3
4. Не избыточен как Level 3-4
```

---

## Матрица компонентов по уровням

| Компонент | L1 | L2 | L3 | L4 |
|-----------|----|----|----|----|
| FastAPI | ✓ | ✓ | ✓ | ✓ |
| PostgreSQL | — | ✓ | ✓ | ✓ |
| MongoDB | — | ○ | ○ | ○ |
| Redis | — | ○ | ✓ | ✓ |
| Docker | — | ✓ | ✓ | ✓ |
| Docker Compose | — | ✓ | ✓ | — |
| Kubernetes | — | — | — | ✓ |
| Nginx | — | — | ✓ | ✓ |
| SSL | — | — | ✓ | ✓ |
| Prometheus | — | — | ✓ | ✓ |
| Grafana | — | — | ✓ | ✓ |
| CI (GitHub Actions) | — | ✓ | ✓ | ✓ |
| CD | — | — | ✓ | ✓ |
| Unit тесты | — | ✓ | ✓ | ✓ |
| Integration тесты | — | ✓ | ✓ | ✓ |
| E2E тесты | — | — | ✓ | ✓ |

**Легенда**: ✓ = обязательно, ○ = опционально, — = не нужно

---

## Условные правила для Level 2

### Когда добавлять компоненты

```python
# Псевдокод принятия решений

if "REST API" in FR or "эндпоинт" in FR:
    add_component("Business API")

if "хранить" in FR or "данные" in FR:
    add_component("Data API PostgreSQL")

if "документы" in FR or "логи" in FR:
    add_component("Data API MongoDB")

if "Telegram" in FR or "бот" in FR:
    add_component("Telegram Bot")

if "фоновая задача" in FR or "по расписанию" in FR:
    add_component("Background Worker")

if "кэш" in FR or "сессии" in FR:
    add_component("Redis")
```

### Стандартный набор Level 2

```
Минимальный MVP:
├── Business API (FastAPI) — порт 8000
├── Data API (PostgreSQL) — порт 8001
├── PostgreSQL — порт 5432
└── Docker Compose

Расширенный MVP (если нужно):
├── + Telegram Bot
├── + Background Worker
├── + Redis — порт 6379
└── + MongoDB — порт 27017
```

---

## Результат выбора

```markdown
## Уровень зрелости

**Выбранный уровень**: Level 2 (MVP)

## Обоснование

AIDD-MVP Framework всегда работает на Level 2, что обеспечивает:
- Качественную архитектуру (DDD/Hexagonal)
- Тестирование (≥75% coverage)
- Контейнеризацию (Docker)
- CI pipeline

## Компоненты для данного проекта

| Компонент | Включён | Обоснование |
|-----------|---------|-------------|
| Business API | Да | FR-001, FR-002 требуют REST API |
| Data API PG | Да | Хранение основных данных |
| Telegram Bot | Да/Нет | {Обоснование} |
| Redis | Да/Нет | {Обоснование} |

## Исключённые компоненты (Level 3+)

- Nginx — не нужен для MVP
- Prometheus/Grafana — не нужны для MVP
- SSL — настраивается при деплое
```

---

## Источники

| Документ | Описание |
|----------|----------|
| `knowledge/architecture/quality-standards.md` | Стандарты качества |
| `workflow.md` | Описание Level 2 |
