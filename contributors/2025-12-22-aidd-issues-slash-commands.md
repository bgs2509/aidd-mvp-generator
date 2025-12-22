# Найденные проблемы фреймворка AIDD-MVP Generator

> **Дата**: 2025-12-22
> **Контекст**: Выполнение команды `/idea` в проекте `Prognosis` после `/init`
> **Версия фреймворка**: Текущая (git submodule)

---

## Issue #1: Slash-команды из submodule не регистрируются в Claude Code

### Описание

При использовании AIDD-MVP Generator как Git Submodule (`.aidd/`) slash-команды, определённые в `.aidd/.claude/commands/`, **не распознаются** Claude Code.

### Воспроизведение

```bash
# 1. Подключить фреймворк как submodule
git submodule add https://github.com/your-org/aidd-mvp-generator.git .aidd

# 2. Запустить Claude Code
claude

# 3. Попробовать выполнить команду
/idea "Описание проекта"

# Результат:
# Unknown slash command: idea
```

### Причина

Claude Code ищет slash-команды **только** в:
```
{project}/.claude/commands/*.md
```

Claude Code **НЕ ищет** в:
```
{project}/.aidd/.claude/commands/*.md    ← submodule игнорируется
{project}/submodule/.claude/commands/    ← любой submodule
```

### Почему так сделано в Claude Code

| Причина | Объяснение |
|---------|------------|
| **Безопасность** | Submodule может содержать произвольный код от третьих лиц. Автоматическая регистрация команд создаёт риск выполнения недоверенного кода. |
| **Простота** | Claude Code использует фиксированный путь `.claude/` относительно корня проекта без рекурсивного поиска. |
| **Изоляция** | Каждый проект имеет свои команды, submodule не должен их переопределять автоматически. |

### Текущий workaround

Ручное копирование команд:
```bash
mkdir -p .claude/commands
cp .aidd/.claude/commands/*.md .claude/commands/
```

**Минусы**:
- Требует ручного обновления при изменении фреймворка
- Пользователь может забыть выполнить копирование
- Нет в документации `/init`

### Приоритет

**Высокий** — блокирует основной use-case фреймворка. Пользователь не может использовать slash-команды без дополнительных действий.

---

## Рекомендуемое решение: Включение команд в CLAUDE.md.template

### Идея

Вместо использования отдельных `.md` файлов для slash-команд, **встроить инструкции всех команд напрямую в `CLAUDE.md`**, который генерируется в целевом проекте при инициализации.

### Преимущества

| Преимущество | Описание |
|--------------|----------|
| **Работает сразу** | Не требует копирования файлов или symlink |
| **Единая точка входа** | AI читает CLAUDE.md и получает все инструкции |
| **Автообновление** | При обновлении submodule — перегенерировать CLAUDE.md |
| **Совместимость** | Не зависит от реализации Claude Code |

### Структура нового CLAUDE.md.template

```markdown
# {{PROJECT_NAME}}

> Точка входа для AI-агентов

## Состояние проекта
...

## Slash-команды

### /init
[Полное содержимое init.md]

### /idea
[Полное содержимое idea.md]

### /research
[Полное содержимое research.md]

### /plan
[Полное содержимое plan.md]

### /feature-plan
[Полное содержимое feature-plan.md]

### /generate
[Полное содержимое generate.md]

### /review
[Полное содержимое review.md]

### /test
[Полное содержимое test.md]

### /validate
[Полное содержимое validate.md]

### /deploy
[Полное содержимое deploy.md]

## Роли AI-агентов

### Аналитик
[Содержимое analyst.md]

### Архитектор
[Содержимое architect.md]

...
```

### Алгоритм генерации

```python
def generate_claude_md(project_name: str, project_slug: str) -> str:
    """
    Генерирует CLAUDE.md для целевого проекта,
    включая все slash-команды и роли агентов.
    """
    # 1. Загрузить базовый шаблон
    template = Path(".aidd/templates/project/CLAUDE.md.template").read_text()

    # 2. Собрать все команды
    commands_content = []
    commands_dir = Path(".aidd/.claude/commands")
    for cmd_file in sorted(commands_dir.glob("*.md")):
        cmd_name = cmd_file.stem  # "idea" из "idea.md"
        cmd_content = cmd_file.read_text()
        commands_content.append(f"### /{cmd_name}\n\n{cmd_content}")

    # 3. Собрать все роли агентов
    agents_content = []
    agents_dir = Path(".aidd/.claude/agents")
    for agent_file in sorted(agents_dir.glob("*.md")):
        agent_name = agent_file.stem
        agent_content = agent_file.read_text()
        agents_content.append(f"### {agent_name.title()}\n\n{agent_content}")

    # 4. Подставить в шаблон
    result = template.replace("{{PROJECT_NAME}}", project_name)
    result = result.replace("{{COMMANDS}}", "\n\n".join(commands_content))
    result = result.replace("{{AGENTS}}", "\n\n".join(agents_content))

    return result
```

### Изменения в /init

1. **Добавить шаг генерации CLAUDE.md** с включением всех команд
2. **Обновить документацию** — убрать упоминание о необходимости копирования

### Альтернативные решения (менее предпочтительные)

| Решение | Плюсы | Минусы |
|---------|-------|--------|
| **Symlink** | Автообновление | Не работает на Windows; требует ручного создания |
| **Git hook post-checkout** | Автоматизация | Сложнее настроить; не всегда выполняется |
| **Копирование в /init** | Просто | Не обновляется при `git submodule update` |

---

## Затронутые файлы для исправления

| Файл | Изменение |
|------|-----------|
| `.aidd/templates/project/CLAUDE.md.template` | Добавить секции `{{COMMANDS}}` и `{{AGENTS}}` |
| `.aidd/.claude/commands/init.md` | Добавить шаг генерации CLAUDE.md с командами |
| `.aidd/CLAUDE.md` | Документировать новый подход |
| `.aidd/README.md` | Обновить инструкции быстрого старта |

---

## Резюме

| # | Issue | Приоритет | Статус |
|---|-------|-----------|--------|
| 1 | Slash-команды из submodule не регистрируются | Высокий | Открыт |

### Рекомендуемое решение

**Встроить содержимое всех slash-команд и ролей агентов напрямую в `CLAUDE.md.template`**, который генерируется в целевом проекте командой `/init`.

Это обеспечит:
- Работу "из коробки" без дополнительных действий пользователя
- Независимость от механизма регистрации команд Claude Code
- Единую точку входа для AI-агента

---

*Файл создан во время выполнения `/init` для проекта Prognosis*
