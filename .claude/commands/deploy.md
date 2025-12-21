---
allowed-tools: Read(*), Glob(*), Grep(*), Bash(make :*), Bash(docker :*), Bash(curl :*)
description: Сборка и запуск Docker-контейнеров
---

# Команда: /deploy

> Запускает Валидатора для деплоя приложения.

---

## Синтаксис

```bash
/deploy
```

---

## Описание

Команда `/deploy` выполняет:
- Сборку Docker-контейнеров
- Запуск приложения
- Проверку health-check
- Верификацию работоспособности

---

## Агент

**Валидатор** (`.claude/agents/validator.md`)

---

## Порядок чтения файлов

> **Принцип**: Сначала контекст ЦП, потом инструкции фреймворка.
> **Подробнее**: [docs/initialization.md](../../docs/initialization.md)

### Фаза 1: Контекст целевого проекта

| # | Файл | Условие | Зачем |
|---|------|---------|-------|
| 1 | `./CLAUDE.md` | Если существует | Специфика проекта |
| 2 | `./.pipeline-state.json` | Обязательно | ВСЕ ворота |
| 3 | `./docker-compose.yml` | Обязательно | Инфраструктура |
| 4 | `./Makefile` | Обязательно | Команды сборки |

### Фаза 2: Предусловия

| Ворота | Проверка |
|--------|----------|
| `ALL_GATES_PASSED` | `.pipeline-state.json → gates.ALL_GATES_PASSED.passed == true` |
| Все предыдущие | PRD_READY, RESEARCH_DONE, PLAN_APPROVED, IMPLEMENT_OK, REVIEW_OK, QA_PASSED |

### Фаза 3: Инструкции фреймворка

| # | Файл | Зачем |
|---|------|-------|
| 5 | `.aidd/CLAUDE.md` | Правила фреймворка |
| 6 | `.aidd/workflow.md` | Процесс и ворота |
| 7 | `.aidd/.claude/commands/deploy.md` | Этот файл |
| 8 | `.aidd/.claude/agents/validator.md` | Инструкции роли |

### Фаза 4: База знаний

| # | Файл | Условие |
|---|------|---------|
| 9 | `.aidd/knowledge/infrastructure/docker.md` | Docker практики |

---

## Предусловия

| Ворота | Требование |
|--------|------------|
| `ALL_GATES_PASSED` | Все предыдущие ворота пройдены |

### Алгоритм проверки

```
1. Проверить существование .pipeline-state.json
2. Если файл отсутствует:
   ❌ Пайплайн не инициализирован
   → Сначала выполните /idea
3. Проверить gates.ALL_GATES_PASSED.passed == true
4. Если ворота не пройдены:
   ❌ Ворота ALL_GATES_PASSED не пройдены
   → Сначала выполните /validate
5. Проверить все предыдущие ворота:
   - PRD_READY ✓
   - RESEARCH_DONE ✓
   - PLAN_APPROVED ✓
   - IMPLEMENT_OK ✓
   - REVIEW_OK ✓
   - QA_PASSED ✓
6. Если какие-то ворота не пройдены:
   ❌ Не все ворота пройдены: {список}
7. Продолжить выполнение
```

---

## Качественные ворота

### DEPLOYED

| Критерий | Описание |
|----------|----------|
| Контейнеры | Docker-контейнеры запущены |
| Health | Health-check проходит |
| Сценарии | Базовые сценарии работают |
| Логи | Нет ошибок в логах |

---

## Команды деплоя

```bash
# Сборка
make build

# Запуск
make up

# Проверка health
make health

# Просмотр логов
make logs

# Остановка
make down
```

---

## Docker Compose команды

```bash
# Сборка образов
docker-compose build

# Запуск в фоне
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Проверка статуса
docker-compose ps

# Остановка
docker-compose down
```

---

## Примеры использования

```bash
# После /validate
/deploy

# Результат:
# ✓ Контейнеры собраны
# ✓ Приложение запущено
# ✓ Health-check: OK
# ✓ DEPLOYED
```

---

## Проверка после деплоя

```bash
# API Health
curl http://localhost:8000/health

# Data API Health
curl http://localhost:8001/health

# Базовый сценарий
curl http://localhost:8000/api/v1/...
```

---

## Готово!

После прохождения ворот `DEPLOYED` MVP готов к использованию.

```
┌─────────────────────────────────────────────┐
│                                             │
│   MVP успешно создан и запущен!             │
│                                             │
│   Время: ~10 минут                          │
│   Покрытие: ≥75%                            │
│   Качество: Production-ready                │
│                                             │
└─────────────────────────────────────────────┘
```
