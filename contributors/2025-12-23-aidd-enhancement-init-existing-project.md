# Enhancement: Интерактивный /init для существующих проектов

> **Дата**: 2025-12-23
> **Автор**: bgs
> **Контекст**: Выполнение `/init` в проекте `free-ai-selector` с уже существующей структурой
> **Тип**: Enhancement (улучшение)

---

## Проблема

Команда `/init` предполагает работу с пустым проектом и создаёт файлы/папки без проверки существующего содержимого. При выполнении в **уже существующем проекте** это приводит к:

1. Попыткам перезаписать существующие файлы (например, `CLAUDE.md`)
2. Созданию дублирующейся структуры папок
3. Потере пользовательских настроек и кастомизаций
4. Конфликтам между шаблонами фреймворка и реальной архитектурой проекта

### Пример конфликта

Проект `free-ai-selector` уже имеет:
- Собственный `CLAUDE.md` с описанием архитектуры 5 микросервисов
- Структуру `services/` вместо генерируемой `ai-docs/docs/`
- `docker-compose.yml` с продакшн-конфигурацией

При запуске `/init` фреймворк пытается создать шаблонный `CLAUDE.md`, что неправильно.

---

## Предлагаемое решение

### Режим работы: EXISTING_PROJECT

Добавить в `/init` автоопределение **существующего проекта** и интерактивный режим работы.

### Критерии определения существующего проекта

```python
def is_existing_project() -> bool:
    """
    Определяет, является ли проект существующим (не пустым).

    Returns:
        True если проект содержит значимые файлы/папки
    """
    indicators = [
        Path("services/").exists(),
        Path("src/").exists(),
        Path("app/").exists(),
        Path("docker-compose.yml").exists(),
        Path("CLAUDE.md").exists(),
        Path("README.md").exists() and Path("README.md").stat().st_size > 500,
        len(list(Path(".").glob("*.py"))) > 2,
    ]
    return any(indicators)
```

---

## Новый алгоритм /init

### Фаза 1: Детекция режима

```
┌─────────────────────────────────────────────────────────────────┐
│  /init запущен                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Проверка типа проекта:                                          │
│                                                                  │
│  ┌──────────────┐                    ┌──────────────────────┐   │
│  │ Пустой       │ ───────────────▶  │ Стандартный /init    │   │
│  │ проект       │                    │ (текущее поведение)  │   │
│  └──────────────┘                    └──────────────────────┘   │
│                                                                  │
│  ┌──────────────┐                    ┌──────────────────────┐   │
│  │ Существующий │ ───────────────▶  │ Интерактивный /init  │   │
│  │ проект       │                    │ (новое поведение)    │   │
│  └──────────────┘                    └──────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Фаза 2: Сканирование и сравнение

```python
@dataclass
class FileComparison:
    """Результат сравнения файла."""
    path: str
    exists_in_project: bool
    exists_in_template: bool
    content_differs: bool
    project_content: str | None
    template_content: str | None
    diff_summary: str | None  # Краткое описание различий


def scan_and_compare() -> List[FileComparison]:
    """
    Сканирует проект и сравнивает с шаблонами.

    Returns:
        Список сравнений для каждого файла/папки
    """
    comparisons = []

    # Файлы из шаблонов
    template_files = [
        ("CLAUDE.md", ".aidd/templates/project/CLAUDE.md.template"),
        ("README.md", ".aidd/templates/project/README.md.template"),
        (".gitignore", ".aidd/templates/project/.gitignore.template"),
        (".env.example", ".aidd/templates/project/.env.example.template"),
        (".pipeline-state.json", None),  # Генерируется динамически
    ]

    # Папки из шаблонов
    template_dirs = [
        "ai-docs/docs/prd",
        "ai-docs/docs/architecture",
        "ai-docs/docs/plans",
        "ai-docs/docs/reports",
        "ai-docs/docs/research",
        ".claude",
        "docs/api",
    ]

    for file_path, template_path in template_files:
        project_file = Path(file_path)
        comparison = FileComparison(
            path=file_path,
            exists_in_project=project_file.exists(),
            exists_in_template=template_path is not None,
            content_differs=False,
            project_content=None,
            template_content=None,
            diff_summary=None,
        )

        if project_file.exists() and template_path:
            template_file = Path(template_path)
            if template_file.exists():
                comparison.project_content = project_file.read_text()
                comparison.template_content = template_file.read_text()
                comparison.content_differs = (
                    comparison.project_content != comparison.template_content
                )
                if comparison.content_differs:
                    comparison.diff_summary = generate_diff_summary(
                        comparison.project_content,
                        comparison.template_content
                    )

        comparisons.append(comparison)

    return comparisons
```

### Фаза 3: Интерактивное подтверждение

```
┌─────────────────────────────────────────────────────────────────┐
│  ИНТЕРАКТИВНЫЙ /init — Обнаружен существующий проект            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📁 Существующие файлы:                                          │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ CLAUDE.md                                                  │  │
│  │ ├── Статус: ⚠️  ОТЛИЧАЕТСЯ от шаблона                      │  │
│  │ ├── Размер: 3.2 KB (проект) vs 1.1 KB (шаблон)            │  │
│  │ └── Различия:                                              │  │
│  │     • Проект: 5 микросервисов, HTTP-only архитектура       │  │
│  │     • Шаблон: Плейсхолдеры {{PROJECT_NAME}}                │  │
│  │                                                            │  │
│  │ Что делать?                                                │  │
│  │ [1] Сохранить текущую версию (рекомендуется)              │  │
│  │ [2] Заменить на шаблон                                     │  │
│  │ [3] Объединить (добавить секции из шаблона)               │  │
│  │ [4] Показать diff                                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ .pipeline-state.json                                       │  │
│  │ ├── Статус: ❌ Не существует                               │  │
│  │ └── Действие: Создать                                      │  │
│  │                                                            │  │
│  │ Создать файл? [Y/n]                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  📂 Папки:                                                       │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ ai-docs/docs/                                              │  │
│  │ ├── Статус: ❌ Не существует                               │  │
│  │ └── Примечание: Проект использует services/ вместо ai-docs│  │
│  │                                                            │  │
│  │ Создать структуру ai-docs/docs/? [y/N]                     │  │
│  │ (N — пропустить, структура проекта отличается)             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Опции для пользователя

### При различии файлов

| Опция | Описание | Когда использовать |
|-------|----------|-------------------|
| **Сохранить текущую** | Не трогать существующий файл | Проект уже настроен, файл кастомизирован |
| **Заменить на шаблон** | Перезаписать шаблоном фреймворка | Хотите начать с чистого шаблона |
| **Объединить (mix)** | Интеллектуальное слияние | Хотите добавить секции из шаблона к существующему |
| **Показать diff** | Отобразить различия | Для принятия решения |

### При отсутствии файла

| Опция | Описание |
|-------|----------|
| **Создать** | Создать файл из шаблона |
| **Пропустить** | Не создавать (проект использует другую структуру) |

---

## Алгоритм объединения (Mix)

```python
def merge_files(project_content: str, template_content: str, file_type: str) -> str:
    """
    Интеллектуальное объединение содержимого.

    Args:
        project_content: Содержимое файла проекта
        template_content: Содержимое шаблона
        file_type: Тип файла (md, json, yaml, etc.)

    Returns:
        Объединённое содержимое
    """
    if file_type == "md":
        return merge_markdown(project_content, template_content)
    elif file_type == "json":
        return merge_json(project_content, template_content)
    else:
        # Для остальных — показать side-by-side и спросить
        return interactive_merge(project_content, template_content)


def merge_markdown(project: str, template: str) -> str:
    """
    Слияние Markdown файлов по секциям.

    Алгоритм:
    1. Извлечь секции (## заголовки) из обоих файлов
    2. Сохранить все секции проекта
    3. Добавить секции из шаблона, которых нет в проекте
    """
    project_sections = extract_md_sections(project)
    template_sections = extract_md_sections(template)

    # Секции из шаблона, которых нет в проекте
    new_sections = []
    for title, content in template_sections.items():
        if title not in project_sections:
            new_sections.append((title, content))

    if new_sections:
        result = project.rstrip() + "\n\n"
        result += "<!-- Добавлено из шаблона AIDD -->\n\n"
        for title, content in new_sections:
            result += f"## {title}\n\n{content}\n\n"
        return result

    return project  # Нет новых секций
```

---

## Изменения в .pipeline-state.json

Добавить поле для отслеживания режима инициализации:

```json
{
  "project_name": "free-ai-selector",
  "mode": "FEATURE",
  "init_mode": "EXISTING_PROJECT",
  "init_decisions": {
    "CLAUDE.md": "kept_existing",
    "README.md": "kept_existing",
    ".pipeline-state.json": "created",
    "ai-docs/": "skipped",
    ".claude/": "created"
  },
  "current_stage": 0,
  "gates": { ... }
}
```

---

## Пример вывода

### Успешная интерактивная инициализация

```
┌─────────────────────────────────────────────────────────────────┐
│  BOOTSTRAP PIPELINE — Режим: EXISTING_PROJECT                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Проверка окружения:                                             │
│  ✓ Git репозиторий инициализирован                              │
│  ✓ Фреймворк .aidd/ подключен                                   │
│  ✓ Python 3.12.0 >= 3.11                                        │
│  ✓ Docker установлен                                            │
│                                                                  │
│  Обнаружен существующий проект:                                  │
│  • services/ — 5 микросервисов                                   │
│  • docker-compose.yml — продакшн конфигурация                    │
│  • CLAUDE.md — кастомная документация                            │
│                                                                  │
│  Решения пользователя:                                           │
│  ✓ CLAUDE.md — сохранена текущая версия                         │
│  ✓ README.md — сохранена текущая версия                         │
│  ✓ .pipeline-state.json — создан                                │
│  ⏭️  ai-docs/docs/ — пропущено (проект использует services/)     │
│  ✓ .claude/ — создана                                           │
│                                                                  │
│  ────────────────────────────────────────────────────────────── │
│  ✓ BOOTSTRAP_READY                                               │
│                                                                  │
│  Следующий шаг: /idea "Описание новой фичи"                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Затрагиваемые файлы

| Файл | Изменения |
|------|-----------|
| `.aidd/.claude/commands/init.md` | Добавить логику детекции и интерактивный режим |
| `.aidd/templates/documents/pipeline-state-template.json` | Добавить `init_mode` и `init_decisions` |
| `.aidd/knowledge/architecture/` | Документировать режим EXISTING_PROJECT |
| `.aidd/CLAUDE.md` | Описать новый режим в разделе "Два режима работы" |

---

## Приоритет

**Высокий** — критично для использования фреймворка в существующих проектах.

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
