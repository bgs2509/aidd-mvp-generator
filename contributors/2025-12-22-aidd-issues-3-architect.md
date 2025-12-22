# Найденные проблемы фреймворка AIDD-MVP Generator

> **Дата**: 2025-12-22
> **Контекст**: Выполнение команды `/plan` для проекта `fastapi-crud-aidd-generated`
> **Роль**: Архитектор (Stage 3)
> **Версия фреймворка**: Текущая (git submodule)

---

## Issue #4: Шаблон архитектуры не указывает расположение .env.example

### Описание

Шаблон `.aidd/templates/documents/architecture-template.md` не содержит явного указания, что `.env.example` должен быть **один файл в корне проекта**, а не per-service файлы.

### Проблема, которая возникла

При проектировании архитектуры AI спроектировал per-service файлы конфигурации:

```
services/
├── users_api/.env.example     ← НЕПРАВИЛЬНО
└── users_data/.env.example    ← НЕПРАВИЛЬНО
```

Вместо корректной структуры:

```
project_root/
└── .env.example               ← ПРАВИЛЬНО (один файл)
```

### Корневая причина

В шаблоне `architecture-template.md` секция "5. Инфраструктура" не содержит явного указания на расположение `.env.example`.

При этом в фреймворке уже есть корректные шаблоны:
- `.aidd/templates/project/.env.example.template` — корневой шаблон
- `.aidd/templates/infrastructure/docker-compose/.env.example` — детальный шаблон для docker-compose

### Затронутые файлы

| Файл | Проблема |
|------|----------|
| `.aidd/templates/documents/architecture-template.md` | Нет указания на корневой `.env.example` |

### Рекомендация

Добавить в секцию "5. Инфраструктура" шаблона `architecture-template.md` явное указание:

```markdown
### 5.2 Переменные окружения

**ВАЖНО**: Один файл `.env.example` в корне проекта (НЕ per-service)

Шаблон: `.aidd/templates/project/.env.example.template`

```env
# =============================================================================
# {PROJECT_NAME} — Переменные окружения
# =============================================================================

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB={project}_db

# Services
API_PORT=8000
DATA_API_PORT=8001
...
```

**Принцип**:
- Один `.env.example` в корне проекта
- Docker Compose использует этот файл для всех сервисов
- Сервисы читают переменные из окружения контейнера
```

### Альтернативный вариант

Добавить в секцию чеклиста `architecture-template.md`:

```markdown
## Чеклист архитектурного плана

- [ ] Переменные окружения описаны для корневого `.env.example` (НЕ per-service)
```

### Приоритет

**Средний** — предотвращает ошибки архитектурного планирования и обеспечивает консистентность конфигурации.

### Влияние

- Предотвращает создание дублирующих файлов конфигурации
- Упрощает управление переменными окружения
- Соответствует best practices Docker Compose

---

## Резюме

| # | Issue | Файл | Приоритет | Статус |
|---|-------|------|-----------|--------|
| 4 | .env.example должен быть в корне (не per-service) | `architecture-template.md` | Средний | Открыт |

---

*Файл создан автоматически во время выполнения `/plan`*
