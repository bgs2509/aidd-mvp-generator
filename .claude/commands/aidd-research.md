---
allowed-tools: Read(*), Glob(*), Grep(*), Bash(git :*)
description: Анализ кодовой базы и технологий
---

# Команда: /research

> Запускает Исследователя для анализа кодовой базы и технологий.

---

## Синтаксис

```bash
/research
```

---

## Описание

Команда `/aidd-research` выполняет анализ существующего кода (для FEATURE)
или анализ требований и технологий (для CREATE).

> **VERIFY BEFORE ACT**: Перед созданием файлов/директорий проверьте их
> существование (см. CLAUDE.md, раздел "Критические правила").

---

## Агент

**Исследователь** (`.claude/agents/researcher.md`)

---

## Порядок чтения файлов

> **Принцип**: Сначала контекст ЦП, потом инструкции фреймворка.
> **Подробнее**: [docs/initialization.md](../../docs/initialization.md)

### Фаза 1: Контекст целевого проекта

| # | Файл | Условие | Зачем |
|---|------|---------|-------|
| 1 | `./CLAUDE.md` | Если существует | Специфика проекта |
| 2 | `./.pipeline-state.json` | Обязательно | Режим, этап, ворота |
| 3 | `./ai-docs/docs/prd/*.md` | Обязательно | PRD для анализа |
| 4 | `./services/` | Для FEATURE | Существующий код |

### Фаза 2: Предусловия

| Ворота | Проверка |
|--------|----------|
| `PRD_READY` | `.pipeline-state.json → gates.PRD_READY.passed == true` |

### Фаза 3: Инструкции фреймворка

| # | Файл | Зачем |
|---|------|-------|
| 5 | `.aidd/CLAUDE.md` | Правила фреймворка |
| 6 | `.aidd/workflow.md` | Процесс и ворота |
| 7 | `.aidd/.claude/commands/research.md` | Этот файл |
| 8 | `.aidd/.claude/agents/researcher.md` | Инструкции роли |

### Фаза 4: База знаний

| # | Файл | Условие |
|---|------|---------|
| 9 | `.aidd/knowledge/architecture/*.md` | По необходимости |

---

## Режимы

| Режим | Поведение |
|-------|-----------|
| **CREATE** | Анализ требований из PRD, выбор технологий |
| **FEATURE** | Анализ существующего кода, выявление паттернов |

---

## Предусловия

| Ворота | Требование |
|--------|------------|
| `PRD_READY` | PRD документ должен существовать |

### Алгоритм проверки

```
1. Проверить существование .pipeline-state.json
2. Если файл отсутствует:
   ❌ Пайплайн не инициализирован
   → Сначала выполните /idea
3. Проверить gates.PRD_READY.passed == true
4. Если ворота не пройдены:
   ❌ Ворота PRD_READY не пройдены
   → Сначала выполните /idea
5. Продолжить выполнение
```

---

## Выходные артефакты

| Артефакт | Путь |
|----------|------|
| Research Report | `ai-docs/docs/research/{YYYY-MM-DD}_{FID}_{slug}-research.md` |

### Именование артефакта

FID и slug берутся из `current_feature` в `.pipeline-state.json`:

```python
# Получить данные из state
fid = state["current_feature"]["id"]      # F001
slug = state["current_feature"]["name"]    # table-booking
date = datetime.now().strftime("%Y-%m-%d") # 2024-12-23

# Сформировать имя файла
filename = f"{date}_{fid}_{slug}-research.md"
# → 2024-12-23_F001_table-booking-research.md
```

### Обновление .pipeline-state.json

После создания отчёта обновить `current_feature.artifacts`:

```json
{
  "current_feature": {
    "id": "F001",
    "name": "table-booking",
    "stage": "RESEARCH",
    "artifacts": {
      "prd": "prd/2024-12-23_F001_table-booking-prd.md",
      "research": "research/2024-12-23_F001_table-booking-research.md"
    }
  }
}
```

---

## Качественные ворота

### RESEARCH_DONE

| Критерий | Описание |
|----------|----------|
| Анализ кода | Существующий код изучен (для FEATURE) |
| Паттерны | Архитектурные паттерны выявлены |
| Ограничения | Технические ограничения определены |
| Рекомендации | Сформулированы рекомендации |

---

## Примеры использования

```bash
# После /idea
/research
```

---

## Следующий шаг

После прохождения ворот `RESEARCH_DONE`:

```bash
/plan          # для CREATE
/feature-plan  # для FEATURE
```
