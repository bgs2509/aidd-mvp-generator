---
allowed-tools: Read(*), Glob(*), Grep(*), Edit(**/*.md), Write(**/*.md), Bash(mkdir :*)
argument-hint: "[описание идеи проекта или фичи]"
description: Создать PRD документ из идеи пользователя
---

# Команда: /idea

> Запускает Аналитика для создания PRD документа из идеи.

---

## Синтаксис

```bash
/idea "Описание идеи проекта или фичи"
```

---

## Описание

Команда `/idea` — точка входа в пайплайн AIDD-MVP. Преобразует текстовое
описание идеи в структурированный PRD (Product Requirements Document).

> **VERIFY BEFORE ACT**: Перед созданием файлов/директорий проверьте их
> существование (см. CLAUDE.md, раздел "Критические правила").

---

## Агент

**Аналитик** (`.claude/agents/analyst.md`)

---

## Порядок чтения файлов

> **Принцип**: Сначала контекст ЦП, потом инструкции фреймворка.
> **Подробнее**: [docs/initialization.md](../../docs/initialization.md)

### Фаза 1: Контекст целевого проекта

| # | Файл | Условие | Зачем |
|---|------|---------|-------|
| 1 | `./CLAUDE.md` | Если существует | Специфика проекта |
| 2 | `./.pipeline-state.json` | Если существует | Режим, этап, ворота |
| 3 | `./ai-docs/docs/prd/` | Если существует | Существующий PRD (для FEATURE) |

### Фаза 2: Предусловия

Нет — `/idea` это первый этап пайплайна.

### Фаза 3: Инструкции фреймворка

| # | Файл | Зачем |
|---|------|-------|
| 4 | `.aidd/CLAUDE.md` | Правила фреймворка |
| 5 | `.aidd/workflow.md` | Процесс и ворота |
| 6 | `.aidd/.claude/commands/idea.md` | Этот файл |
| 7 | `.aidd/.claude/agents/analyst.md` | Инструкции роли |

### Фаза 4: Шаблоны

| # | Файл | Условие |
|---|------|---------|
| 8 | `.aidd/templates/documents/prd-template.md` | Если PRD не существует |

---

## Bootstrap: Проверка и инициализация

> **Важно**: Перед созданием PRD команда `/idea` автоматически проверяет
> готовность окружения (Bootstrap Pipeline). При ошибках — предлагает `/init`.

### Алгоритм Bootstrap-проверок

```python
def auto_bootstrap() -> bool:
    """
    Автоматическая проверка и инициализация перед /idea.

    Returns:
        True если BOOTSTRAP_READY, False если нужен /init
    """
    # 1. Проверить, пройден ли уже BOOTSTRAP_READY
    if Path(".pipeline-state.json").exists():
        state = read_json(".pipeline-state.json")
        if state.get("gates", {}).get("BOOTSTRAP_READY", {}).get("passed"):
            return True  # Уже инициализирован

    # 2. Выполнить проверки окружения
    checks = {
        "git": run("git rev-parse --git-dir").ok,
        "framework": Path(".aidd/CLAUDE.md").exists(),
        "python": check_python_version() >= (3, 11),
        "docker": run("docker --version").ok,
    }

    # 3. Если все проверки пройдены — автоинициализация
    if all(checks.values()):
        # Создать структуру
        create_directory_structure()
        # Создать .pipeline-state.json
        create_pipeline_state()
        # Создать CLAUDE.md
        create_project_claude_md()
        return True

    # 4. Если есть ошибки — сообщить и предложить /init
    failed = [k for k, v in checks.items() if not v]
    print(f"❌ Проверки не пройдены: {failed}")
    print("→ Выполните /init для диагностики и исправления")
    return False
```

### Действия при первом запуске

> **VERIFY BEFORE ACT**: Перед созданием директорий и файлов проверяем их существование.

```bash
# 1. Определить режим
if [ -d "services" ] || [ -f "docker-compose.yml" ]; then
    MODE="FEATURE"
else
    MODE="CREATE"
fi

# 2. VERIFY: Проверить существующую структуру артефактов
if [ -d "ai-docs/docs" ]; then
    existing_count=$(ls -d ai-docs/docs/*/ 2>/dev/null | wc -l)
    echo "✓ Структура ai-docs/docs/ уже существует ($existing_count директорий)"
fi

# 3. ACT: Создать только недостающие директории
for dir in prd architecture plans reports research; do
    if [ ! -d "ai-docs/docs/$dir" ]; then
        mkdir -p "ai-docs/docs/$dir"
        echo "✓ Создана директория: ai-docs/docs/$dir"
    fi
done

# 4. Инициализировать состояние пайплайна (если не существует)
if [ ! -f ".pipeline-state.json" ]; then
    echo '{"project_name":"","mode":"'$MODE'","current_stage":1,"gates":{"BOOTSTRAP_READY":{"passed":true}}}' > .pipeline-state.json
    echo "✓ Создан .pipeline-state.json"
else
    echo "✓ .pipeline-state.json уже существует"
fi

# 5. Создать CLAUDE.md если не существует
if [ ! -f "CLAUDE.md" ]; then
    echo "# Project\n\nСм. .aidd/CLAUDE.md" > CLAUDE.md
    echo "✓ Создан CLAUDE.md"
else
    echo "✓ CLAUDE.md уже существует"
fi
```

### Предусловия

| Ворота | Проверка |
|--------|----------|
| `BOOTSTRAP_READY` | Авто-проверка при запуске `/idea` |

Если `BOOTSTRAP_READY` не пройден:
```
❌ Окружение не готово. Ошибки:
- framework: Фреймворк .aidd/ не найден
- docker: Docker не установлен

→ Выполните /init для детальной диагностики
```

---

## Режимы

| Режим | Условие | Поведение |
|-------|---------|-----------|
| **CREATE** | Нет `services/` или `docker-compose.yml` | Создаёт полный PRD для нового MVP |
| **FEATURE** | Есть существующий код | Создаёт FEATURE_PRD для новой функции |

---

## Предусловия

Нет — это первый этап пайплайна.

---

## Выходные артефакты (в целевом проекте)

| Артефакт | Путь |
|----------|------|
| PRD документ | `ai-docs/docs/prd/{name}-prd.md` |
| Состояние | `.pipeline-state.json` |

---

## Качественные ворота

### PRD_READY

| Критерий | Описание |
|----------|----------|
| Все секции | PRD полностью заполнен |
| ID требований | Каждое требование имеет уникальный ID |
| Приоритеты | Must/Should/Could для всех требований |
| Критерии приёмки | Определены для всех FR |
| Открытые вопросы | Нет блокирующих вопросов |
| Состояние | `.pipeline-state.json` обновлён |

---

## Примеры использования

### Создание нового MVP

```bash
/idea "Создать сервис бронирования столиков в ресторанах.
Пользователи могут искать рестораны по кухне и локации,
смотреть свободные столики и бронировать на нужное время.
Рестораны получают уведомления о бронях в Telegram."
```

### Добавление фичи

```bash
/idea "Добавить систему email-уведомлений для подтверждения бронирования
и напоминания за 2 часа до визита."
```

### Краткое описание

```bash
/idea "Сервис учёта личных финансов с категоризацией расходов"
```

---

## Следующий шаг

После прохождения ворот `PRD_READY`:

```bash
/research
```
