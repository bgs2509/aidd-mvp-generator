# Enhancement: Автоматическое копирование slash-команд в /init

> **Дата**: 2025-12-23
> **Автор**: bgs
> **Контекст**: Slash-команды AIDD (`/idea`, `/research`, `/plan` и др.) не отображаются в автодополнении Claude Code CLI
> **Тип**: Enhancement (улучшение)

---

## Проблема

Claude Code CLI ищет slash-команды **только** в `{project}/.claude/commands/`. Когда фреймворк AIDD подключен как git submodule (`.aidd/`), команды из `.aidd/.claude/commands/` **не регистрируются автоматически** и не отображаются в автодополнении.

### Симптомы

1. При вводе `/idea` в CLI показывается только `/ide` (встроенная команда IDE integrations)
2. Команды `/research`, `/plan`, `/generate` и другие не появляются в автодополнении
3. Пользователь не знает о доступных командах фреймворка

### Текущее "решение" в документации

В `.aidd/CLAUDE.md` описан workaround:

```
Пользователь: /idea "описание"
     ↓
AI читает: ./CLAUDE.md (таблица команд → агент: Аналитик)
     ↓
AI читает: ./.aidd/.claude/commands/idea.md (полные инструкции)
```

**Проблема**: Это требует, чтобы пользователь **знал** о существовании команды и ввёл её вручную. Без автодополнения команды "невидимы".

---

## Предлагаемое решение

### Копирование файлов команд при `/init`

Добавить в `/init` автоматическое копирование файлов из `.aidd/.claude/commands/` в `.claude/commands/`:

```bash
# В рамках /init, после создания .claude/
mkdir -p .claude/commands
cp .aidd/.claude/commands/*.md .claude/commands/
```

### Результат

```
{project}/
├── .aidd/                          ← Git Submodule (read-only, источник)
│   └── .claude/
│       └── commands/
│           ├── init.md
│           ├── idea.md
│           ├── research.md
│           ├── plan.md
│           └── ...
│
└── .claude/                        ← Локальная папка проекта
    └── commands/
        ├── init.md                 ← Копия из .aidd/
        ├── idea.md                 ← Копия из .aidd/
        ├── research.md             ← Копия из .aidd/
        ├── plan.md                 ← Копия из .aidd/
        └── ...
```

### Сравнение подходов

| Подход | Плюсы | Минусы |
|--------|-------|--------|
| **Копирование (предлагается)** | Работает везде (Windows, Linux, macOS), файлы в git | Требует повторного копирования при обновлении submodule |
| Симлинки | Автообновление | Не работает на Windows без Developer Mode |
| Ничего не делать (текущее) | — | Команды невидимы в CLI |

---

## Алгоритм копирования команд

```python
import shutil
from pathlib import Path
from datetime import datetime


def copy_command_files() -> None:
    """
    Копирует файлы slash-команд из .aidd/ в .claude/commands/.

    Запускается как часть /init после создания .claude/.
    """
    project_commands = Path(".claude/commands")
    framework_commands = Path(".aidd/.claude/commands")

    if not framework_commands.exists():
        print("⚠️ Директория .aidd/.claude/commands/ не найдена")
        return

    # Создать директорию если не существует
    project_commands.mkdir(parents=True, exist_ok=True)

    copied_count = 0
    skipped_count = 0
    updated_count = 0

    for cmd_file in framework_commands.glob("*.md"):
        target_path = project_commands / cmd_file.name

        if target_path.exists():
            # Сравнить содержимое
            source_content = cmd_file.read_text()
            target_content = target_path.read_text()

            if source_content == target_content:
                print(f"✓ {cmd_file.name} — актуален")
                skipped_count += 1
                continue
            else:
                # Файл изменился в .aidd/ — обновить
                shutil.copy2(cmd_file, target_path)
                print(f"↻ {cmd_file.name} — обновлён")
                updated_count += 1
        else:
            # Файл не существует — скопировать
            shutil.copy2(cmd_file, target_path)
            print(f"+ {cmd_file.name} — скопирован")
            copied_count += 1

    print(f"\n✓ Команды: {copied_count} скопировано, {updated_count} обновлено, {skipped_count} без изменений")
    print("  Команды теперь доступны в автодополнении Claude Code CLI")
```

---

## Изменения в init.md

Добавить в секцию "Действия инициализации" после "Создание структуры папок":

```markdown
### 4. Копирование slash-команд

> **Назначение**: Сделать команды AIDD видимыми в автодополнении Claude Code CLI.

```bash
# VERIFY: Проверить существование .aidd/.claude/commands/
if [ ! -d ".aidd/.claude/commands" ]; then
    echo "⚠️ Фреймворк не подключен или повреждён"
    exit 1
fi

# ACT: Создать директорию и скопировать файлы
mkdir -p .claude/commands

for f in .aidd/.claude/commands/*.md; do
    name=$(basename "$f")
    target=".claude/commands/$name"

    if [ -f "$target" ]; then
        # Сравнить файлы
        if cmp -s "$f" "$target"; then
            echo "✓ $name — актуален"
        else
            cp "$f" "$target"
            echo "↻ $name — обновлён"
        fi
    else
        cp "$f" "$target"
        echo "+ $name — скопирован"
    fi
done
```

**Результат**:
```
.claude/
└── commands/
    ├── init.md
    ├── idea.md
    ├── research.md
    ├── plan.md
    ├── feature-plan.md
    ├── generate.md
    ├── review.md
    ├── test.md
    ├── validate.md
    └── deploy.md
```
```

---

## Обновление при `git submodule update`

При обновлении submodule `.aidd/` команды могут измениться. Рекомендуется:

1. **Автоматически**: Добавить post-checkout hook в `.git/hooks/`
2. **Вручную**: Повторно запустить `/init` после обновления submodule

### Git hook (опционально)

`.git/hooks/post-checkout`:
```bash
#!/bin/bash
# Обновить команды после checkout/submodule update
if [ -d ".aidd/.claude/commands" ] && [ -d ".claude/commands" ]; then
    cp .aidd/.claude/commands/*.md .claude/commands/ 2>/dev/null
    echo "✓ Команды AIDD обновлены"
fi
```

---

## Обновление .gitignore

**НЕ добавлять** `.claude/commands/` в `.gitignore` — файлы команд должны быть в репозитории для:

1. Работы команд сразу после `git clone` (без `/init`)
2. Версионирования вместе с проектом
3. Возможности кастомизации команд под проект

---

## Обновление вывода /init

```
┌─────────────────────────────────────────────────────────────────┐
│                    BOOTSTRAP PIPELINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Проверка окружения:                                             │
│  ✓ Git репозиторий инициализирован                              │
│  ✓ Фреймворк .aidd/ подключен                                   │
│  ✓ Python 3.12.0 >= 3.11                                        │
│  ✓ Docker установлен                                            │
│                                                                  │
│  Инициализация:                                                  │
│  ✓ Создана структура ai-docs/docs/                              │
│  ✓ Создана папка .claude/                                       │
│  ✓ Скопировано 10 команд в .claude/commands/                    │  ← НОВОЕ
│  ✓ Создан .pipeline-state.json                                  │
│  ✓ Создан CLAUDE.md                                             │
│                                                                  │
│  ────────────────────────────────────────────────────────────── │
│  ✓ BOOTSTRAP_READY                                               │
│                                                                  │
│  Доступные команды: /idea /research /plan /generate /review     │  ← НОВОЕ
│                     /test /validate /deploy /feature-plan       │
│                                                                  │
│  Следующий шаг: /idea "Описание вашего проекта"                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Затрагиваемые файлы

| Файл | Изменения |
|------|-----------|
| `.aidd/.claude/commands/init.md` | Добавить секцию копирования команд |
| `.aidd/CLAUDE.md` | Обновить раздел "Особенности работы с командами" |

---

## Приоритет

**Высокий** — без этого изменения slash-команды AIDD "невидимы" для пользователей CLI.

---

## Статус

| Этап | Статус |
|------|--------|
| Проектирование | ✅ Завершено (этот документ) |
| Реализация | ⏳ Ожидает |
| Тестирование | ⏳ Ожидает |
| Документация | ⏳ Ожидает |

---

*Создано: 2025-12-23*
*Автор: bgs (с помощью Claude Code)*
