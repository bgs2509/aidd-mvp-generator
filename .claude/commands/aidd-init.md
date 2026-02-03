---
allowed-tools: Read(*), Glob(*), Grep(*), Bash(git :*), Bash(python3 :*), Bash(docker :*), Bash(mkdir :*), Write(**/*.md), Write(**/*.json)
description: Инициализация целевого проекта (Bootstrap Pipeline)
---

> ⚠️ **ENFORCEMENT**: Перед завершением этой команды AI ОБЯЗАН:
> 1. Найти секцию "Чеклист ворот" в конце этого файла
> 2. Создать TodoWrite со ВСЕМИ пунктами (особенно 🔴)
> 3. Выполнить ВСЕ пункты и отметить completed
> 4. Команда завершена ТОЛЬКО когда все 🔴 пункты ✅
>
> Правила: `.aidd/CLAUDE.md` → "Выполнение команд /aidd-*"

# Команда: /init

> Запускает Bootstrap Pipeline для инициализации целевого проекта.

---

## Синтаксис

```bash
/init
```

---

## Описание

Команда `/aidd-init` выполняет проверку окружения и инициализацию структуры
целевого проекта для работы с AIDD-MVP Generator.

> **VERIFY BEFORE ACT**: Перед созданием файлов/директорий проверьте их
> существование (см. CLAUDE.md, раздел "Критические правила").

Эта команда:
- Проверяет готовность окружения (git, Python, Docker, фреймворк)
- Создаёт необходимую структуру папок
- Инициализирует `.pipeline-state.json`
- Создаёт `CLAUDE.md` в корне проекта

---

## Когда использовать

| Сценарий | Рекомендация |
|----------|--------------|
| Новый проект, первый запуск | `/aidd-init` (рекомендуется) или сразу `/aidd-analyze` |
| Проверить готовность окружения | `/aidd-init` |
| Исправить проблемы инициализации | `/aidd-init` |

**Примечание**: Команда `/aidd-analyze` автоматически выполняет проверки bootstrap,
но `/aidd-init` позволяет выполнить их явно и получить детальную диагностику.

---

## Проверки окружения

### Обязательные проверки

| # | Проверка | Команда | Критерий успеха |
|---|----------|---------|-----------------|
| 1 | Git репозиторий | `git rev-parse --git-dir` | Exit code 0 |
| 2 | Фреймворк подключен | Проверка `.aidd/CLAUDE.md` | Файл существует и читается |
| 3 | Python версия | `python3 --version` | >= 3.11 |
| 4 | Docker | `docker --version` | Установлен |

### Алгоритм проверок

```python
def check_bootstrap_ready() -> BootstrapResult:
    """
    Проверка готовности окружения для AIDD-MVP.

    Returns:
        BootstrapResult: {ready: bool, checks: list, errors: list}
    """
    checks = []
    errors = []

    # 1. Git репозиторий
    git_check = run_command("git rev-parse --git-dir")
    if git_check.exit_code == 0:
        checks.append(("git", True, "Git репозиторий инициализирован"))
    else:
        errors.append(("git", False, "Не git репозиторий. Выполните: git init"))

    # 2. Фреймворк подключен
    if Path(".aidd/CLAUDE.md").exists():
        checks.append(("framework", True, "Фреймворк .aidd/ подключен"))
    else:
        errors.append(("framework", False,
            "Фреймворк не найден. Выполните:\n"
            "git submodule add https://github.com/your-org/aidd-mvp-generator.git .aidd"))

    # 3. Python версия
    python_check = run_command("python3 --version")
    version = parse_version(python_check.stdout)  # "Python 3.11.5" -> (3, 11, 5)
    if version >= (3, 11):
        checks.append(("python", True, f"Python {version} >= 3.11"))
    else:
        errors.append(("python", False,
            f"Python {version} < 3.11. Требуется Python 3.11+"))

    # 4. Docker
    docker_check = run_command("docker --version")
    if docker_check.exit_code == 0:
        checks.append(("docker", True, "Docker установлен"))
    else:
        errors.append(("docker", False,
            "Docker не установлен. Установите Docker: https://docs.docker.com/get-docker/"))

    return BootstrapResult(
        ready=len(errors) == 0,
        checks=checks,
        errors=errors
    )
```

### VPS Detection (Автоопределение SSH)

> **БЕЗОПАСНОСТЬ**: При работе на VPS/production сервере рекомендуется
> использовать VPS Mode (только чтение).

#### Алгоритм детекции

```python
def detect_vps_session() -> bool:
    """
    Определяет, запущена ли сессия через SSH (VPS/production).

    Returns:
        True если обнаружена SSH-сессия
    """
    import os

    # Признаки SSH-сессии (любой из):
    ssh_indicators = [
        os.environ.get("SSH_CONNECTION"),  # IP клиента и сервера
        os.environ.get("SSH_CLIENT"),      # IP и порт клиента
        os.environ.get("SSH_TTY"),         # TTY сессии
    ]

    return any(ssh_indicators)
```

#### Вывод предупреждения

Если обнаружена SSH-сессия:

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  ОБНАРУЖЕНА SSH-СЕССИЯ (VPS/Production)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Для безопасной работы на production сервере рекомендуется      │
│  активировать VPS Mode (только чтение):                          │
│                                                                  │
│  1. Скопируйте шаблон VPS settings:                              │
│     cp .aidd/templates/project/.claude/settings.vps.json.example │
│        .claude/settings.json                                     │
│                                                                  │
│  2. Перезапустите Claude Code:                                   │
│     claude                                                       │
│                                                                  │
│  В VPS Mode AI может:                                            │
│  ✓ Читать файлы и логи                                          │
│  ✓ Анализировать конфигурации                                   │
│  ✓ Диагностировать проблемы                                     │
│                                                                  │
│  В VPS Mode AI НЕ может:                                         │
│  ✗ Редактировать файлы                                          │
│  ✗ Выполнять docker exec/run                                    │
│  ✗ Перезапускать сервисы                                        │
│                                                                  │
│  Подробнее: knowledge/security/vps-mode.md                       │
│                                                                  │
│  [Продолжить без VPS Mode? y/N]                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Bash-эквивалент

```bash
# Проверка SSH-сессии
if [ -n "$SSH_CONNECTION" ] || [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    echo "⚠️  Обнаружена SSH-сессия. Рекомендуется VPS Mode."
    echo ""
    echo "Активировать VPS Mode (только чтение):"
    echo "  cp .aidd/templates/project/.claude/settings.vps.json.example \\"
    echo "     .claude/settings.json"
    echo ""
    read -p "Продолжить без VPS Mode? [y/N] " -n 1 -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Активируйте VPS Mode и перезапустите claude."
        exit 1
    fi
fi
```

---

### Проверка существующих файлов

> **ВАЖНО**: Эта проверка выполняется для проектов, где уже есть файлы
> (например, после `uv init` или `poetry init`).

#### Проверяемые файлы

| Файл | Проблема | Тип | Действие |
|------|----------|-----|----------|
| `main.py` | Заглушка "Hello from..." | ⚠️ Предупреждение | Рекомендация удалить |
| `app.py` | Заглушка | ⚠️ Предупреждение | Рекомендация удалить |
| `__main__.py` | Заглушка | ⚠️ Предупреждение | Рекомендация удалить |
| `pyproject.toml` | `requires-python >= 3.13` | ❌ **Блокирующая** | Изменить на `>= 3.11` |
| `.python-version` | Версия 3.13+ | ⚠️ Предупреждение | Рекомендация 3.11 или 3.12 |
| `uv.lock` / `poetry.lock` | Устаревший lock | ⚠️ Предупреждение | Пересоздать после изменений |

#### Алгоритм проверки

```python
from dataclasses import dataclass
from pathlib import Path
from typing import List
import re


@dataclass
class FileWarning:
    """Предупреждение о файле."""
    file: str
    issue: str
    action: str
    blocking: bool = False


def check_existing_files() -> List[FileWarning]:
    """
    Проверка существующих файлов на совместимость с фреймворком.

    Выполняется для проектов, где уже есть файлы (после uv init, poetry init и т.д.).

    Returns:
        List[FileWarning]: Список предупреждений о файлах
    """
    warnings = []

    # 1. Проверка заглушек
    stub_files = ["main.py", "app.py", "__main__.py"]
    for stub in stub_files:
        path = Path(stub)
        if path.exists():
            content = path.read_text()
            # Типичные признаки заглушки
            if "Hello from" in content or len(content.strip()) < 100:
                warnings.append(FileWarning(
                    file=stub,
                    issue="Заглушка, созданная менеджером пакетов",
                    action="Удалить (код будет в services/)",
                    blocking=False
                ))

    # 2. Проверка pyproject.toml
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        content = pyproject_path.read_text()

        # Проверка requires-python
        match = re.search(r'requires-python\s*=\s*["\']>=\s*([\d.]+)["\']', content)
        if match:
            version = match.group(1)
            major_minor = tuple(map(int, version.split(".")[:2]))
            if major_minor >= (3, 13):
                warnings.append(FileWarning(
                    file="pyproject.toml",
                    issue=f'requires-python >= {version}',
                    action='Изменить на >= 3.11 (фреймворк требует 3.11+)',
                    blocking=True  # Блокирующая ошибка!
                ))

    # 3. Проверка .python-version
    python_version_path = Path(".python-version")
    if python_version_path.exists():
        version = python_version_path.read_text().strip()
        if version.startswith("3.13") or version.startswith("3.14"):
            warnings.append(FileWarning(
                file=".python-version",
                issue=f"Указана версия {version}",
                action="Рекомендуется 3.11 или 3.12 для совместимости",
                blocking=False
            ))

    # 4. Проверка lock-файлов при изменении pyproject.toml
    lock_files = ["uv.lock", "poetry.lock"]
    has_pyproject_warning = any(w.file == "pyproject.toml" for w in warnings)
    if has_pyproject_warning:
        for lock_file in lock_files:
            if Path(lock_file).exists():
                warnings.append(FileWarning(
                    file=lock_file,
                    issue="Lock-файл устареет после изменения pyproject.toml",
                    action=f"Пересоздать: {'uv lock' if lock_file == 'uv.lock' else 'poetry lock'}",
                    blocking=False
                ))

    return warnings
```

#### Пример вывода предупреждений

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  Обнаружены файлы, требующие внимания:                       │
├─────────────────────────────────────────────────────────────────┤
│  ⚠️ main.py — заглушка, рекомендуется удалить                    │
│  ❌ pyproject.toml — requires-python >= 3.13, требуется >= 3.11  │
│  ⚠️ .python-version — 3.13, рекомендуется 3.12 или 3.11          │
│  ⚠️ uv.lock — пересоздать после изменения pyproject.toml         │
├─────────────────────────────────────────────────────────────────┤
│  ❌ БЛОКИРУЮЩИЕ ОШИБКИ: 1                                        │
│                                                                 │
│  Исправьте pyproject.toml:                                      │
│  Замените: requires-python = ">= 3.13"                          │
│  На:       requires-python = ">= 3.11"                          │
└─────────────────────────────────────────────────────────────────┘
```

#### Логика блокировки

Инициализация **блокируется** только при критических несовместимостях:

| Проблема | Почему блокирующая |
|----------|-------------------|
| `requires-python >= 3.13` | Зависимости могут не работать на Python 3.11/3.12, которые поддерживает фреймворк |

Все остальные проблемы — **предупреждения**, пользователь сам решает, исправлять или нет.

---

## Детекция типа проекта

> **VERIFY BEFORE ACT**: Перед выполнением действий определить тип проекта.

### Критерии существующего проекта

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

### Режимы инициализации

| Режим | Условие | Поведение |
|-------|---------|-----------|
| `NEW_PROJECT` | Проект пустой (ни один индикатор не сработал) | Стандартная инициализация |
| `EXISTING_PROJECT` | Есть значимые файлы/папки | Интерактивный режим |

### Вывод при детекции

```
┌─────────────────────────────────────────────────────────────────┐
│  Детекция типа проекта:                                          │
│                                                                  │
│  Обнаружен EXISTING_PROJECT:                                     │
│  • services/ — найдена директория сервисов                       │
│  • docker-compose.yml — найден Docker Compose                    │
│  • CLAUDE.md — найдена документация (2.3 KB)                     │
│                                                                  │
│  Переход в интерактивный режим...                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Интерактивный режим (EXISTING_PROJECT)

При обнаружении существующего проекта AI переходит в интерактивный режим
и задаёт вопросы пользователю для каждого файла/папки.

### Фаза 1: Сканирование и сравнение

AI сканирует проект и сравнивает с шаблонами фреймворка:

| Файл/Папка | Проверка |
|------------|----------|
| `CLAUDE.md` | Существует? Отличается от шаблона? |
| `README.md` | Существует? Размер > 500 байт (не заглушка)? |
| `.gitignore` | Существует? |
| `.env.example` | Существует? |
| `.pipeline-state.json` | Существует? |
| `ai-docs/docs/` | Существует? |
| `.claude/` | Существует? |

### Фаза 2: Интерактивные вопросы

Для каждого файла, где есть конфликт, AI задаёт вопрос пользователю через чат.

#### Пример для CLAUDE.md (существует и отличается)

```
📄 Обнаружен существующий CLAUDE.md

Размер: 3.2 KB (проект) vs 7.5 KB (шаблон)

Различия:
• Проект: описание вашей архитектуры, сервисов
• Шаблон: таблицы Slash-команд, ролей AI-агентов, порядок чтения файлов

Что делать?
1. Сохранить текущую версию (рекомендуется для кастомных проектов)
2. Заменить на шаблон (начать с чистого шаблона)
3. Объединить (добавить секции Slash-команды и Агенты из шаблона в конец)

Ваш выбор (1/2/3)?
```

#### Пример для отсутствующего файла

```
📄 Файл .pipeline-state.json не найден.

Этот файл необходим для отслеживания состояния пайплайна и пройденных ворот.

Создать файл состояния пайплайна? [Y/n]
```

#### Пример для папки ai-docs/

```
📁 Папка ai-docs/docs/ не найдена.

Проект использует структуру: services/

Создать структуру ai-docs/docs/ для AI-артефактов?
[y/N] (N — пропустить, если используете другую структуру)
```

### Фаза 3: Выполнение решений

После сбора всех ответов AI выполняет действия и записывает решения
в `.pipeline-state.json`.

### Опции для пользователя

| Опция | Описание | Ключ в `init_decisions` |
|-------|----------|------------------------|
| Сохранить текущую | Не трогать существующий файл | `kept_existing` |
| Заменить на шаблон | Перезаписать шаблоном фреймворка | `replaced` |
| Объединить | Добавить секции из шаблона к существующему | `merged` |
| Создать | Создать отсутствующий файл | `created` |
| Пропустить | Не создавать папку/файл | `skipped` |

### Алгоритм объединения Markdown

```python
def merge_markdown(project_content: str, template_content: str) -> str:
    """
    Слияние Markdown файлов по секциям.

    Алгоритм:
    1. Извлечь секции (## заголовки) из обоих файлов
    2. Сохранить все секции проекта
    3. Добавить секции из шаблона, которых нет в проекте
    """
    project_sections = extract_md_sections(project_content)
    template_sections = extract_md_sections(template_content)

    # Секции из шаблона, которых нет в проекте
    new_sections = [
        (title, content)
        for title, content in template_sections.items()
        if title not in project_sections
    ]

    if new_sections:
        result = project_content.rstrip() + "\n\n"
        result += "---\n\n<!-- Добавлено из шаблона AIDD -->\n\n"
        for title, content in new_sections:
            result += f"## {title}\n\n{content}\n\n"
        return result

    return project_content  # Нет новых секций
```

---

## Действия инициализации

После успешных проверок выполняются:

### 1. Создание структуры папок

> **VERIFY BEFORE ACT**: Перед созданием проверяем существование директорий.

```bash
# VERIFY: Проверить существующую структуру
if [ -d "ai-docs/docs" ]; then
    existing_count=$(ls -d ai-docs/docs/*/ 2>/dev/null | wc -l)
    echo "✓ Структура ai-docs/docs/ уже существует ($existing_count директорий)"
fi

# ACT: Создать только недостающие директории
# v2.4+: Поддержка новой структуры с префиксом _ (naming v3)
# Если naming_version=v3, создаём новую структуру, иначе старую
for dir in prd architecture plans reports research; do
    [ -d "ai-docs/docs/$dir" ] || mkdir -p "ai-docs/docs/$dir"
done

# v3 структура (опционально, создаётся при миграции)
# for dir in _analysis _research _plans/mvp _plans/features _validation; do
#     [ -d "ai-docs/docs/$dir" ] || mkdir -p "ai-docs/docs/$dir"
# done

[ -d "docs/api" ] || mkdir -p docs/api
[ -d ".claude" ] || mkdir -p .claude
```

**Результат** (v2 - backward compatible):
```
{project}/
├── ai-docs/
│   └── docs/
│       ├── prd/           # PRD документы (v2) или _analysis/ (v3)
│       ├── architecture/  # Архитектурные планы (v2) или _plans/mvp/ (v3)
│       ├── plans/         # Планы фич (v2) или _plans/features/ (v3)
│       ├── reports/       # Отчёты (v2) или _validation/ (v3)
│       └── research/      # Исследования (v2) или _research/ (v3)
├── .claude/               # Локальные настройки Claude Code
└── docs/
    └── api/               # API документация (openapi.yaml)
```

> **Примечание v2.4+**: Для миграции на v3 структуру используйте:
> ```bash
> python .aidd/scripts/migrate-naming-v3.py
> ```

### 2. Создание .pipeline-state.json

```json
{
  "version": "2.0",
  "project_name": "",
  "mode": "CREATE",
  "init_mode": "NEW_PROJECT",
  "init_decisions": {},
  "naming_version": "v2",
  "created_at": "2025-12-21T10:00:00Z",
  "updated_at": "2025-12-21T10:00:00Z",
  "gate_aliases": {
    "PRD_READY": "ANALYSIS_READY",
    "RESEARCH_DONE": "RESEARCH_READY",
    "IMPLEMENT_OK": "CODE_READY",
    "REVIEW_OK": "REVIEW_READY",
    "QA_PASSED": "TESTING_READY",
    "ALL_GATES_PASSED": "VALIDATION_READY"
  },
  "global_gates": {
    "BOOTSTRAP_READY": {
      "passed": true,
      "passed_at": "2025-12-21T10:00:00Z",
      "checks": {
        "git": true,
        "framework": true,
        "python": "3.11.5",
        "docker": true
      }
    }
  },
  "active_pipelines": {},
  "features_registry": {},
  "next_feature_id": 1,
  "services": []
}
```

> **Примечание v2.4+**:
> - `naming_version: "v2"` — использует старую структуру артефактов (backward compatible)
> - `naming_version: "v3"` — использует новую структуру (_analysis/, _plans/, etc.)
> - `gate_aliases` — позволяют использовать оба варианта названий ворот

#### Пример для EXISTING_PROJECT

```json
{
  "version": "2.0",
  "project_name": "my-existing-app",
  "mode": "FEATURE",
  "init_mode": "EXISTING_PROJECT",
  "init_decisions": {
    "CLAUDE.md": "kept_existing",
    "README.md": "kept_existing",
    ".gitignore": "kept_existing",
    ".pipeline-state.json": "created",
    "ai-docs/": "skipped",
    ".claude/": "created"
  },
  "naming_version": "v2",
  "created_at": "2025-12-23T10:00:00Z",
  "updated_at": "2025-12-23T10:00:00Z",
  "gate_aliases": {
    "PRD_READY": "ANALYSIS_READY",
    "RESEARCH_DONE": "RESEARCH_READY",
    "IMPLEMENT_OK": "CODE_READY",
    "REVIEW_OK": "REVIEW_READY",
    "QA_PASSED": "TESTING_READY",
    "ALL_GATES_PASSED": "VALIDATION_READY"
  },
  "global_gates": {
    "BOOTSTRAP_READY": {
      "passed": true,
      "passed_at": "2025-12-23T10:00:00Z",
      "checks": {
        "git": true,
        "framework": true,
        "python": "3.12.0",
        "docker": true
      }
    }
  },
  "active_pipelines": {},
  "features_registry": {},
  "next_feature_id": 1,
  "services": []
}
```

### 3. Копирование файлов из шаблонов

> **ВАЖНО**: Файлы проекта создаются из шаблонов в `.aidd/templates/project/`.
> Это гарантирует единообразие и правильную структуру.

#### Шаблоны проекта

| Шаблон | Создаёт в ЦП | Назначение |
|--------|--------------|------------|
| `CLAUDE.md.template` | `./CLAUDE.md` | Точка входа для AI (включает таблицы команд и агентов) |
| `changelog-template.md` | `./CHANGELOG.md` | Журнал изменений проекта |
| `README.md.template` | `./README.md` | Документация проекта |
| `.gitignore.template` | `./.gitignore` | Игнорируемые файлы |
| `.env.example.template` | `./.env.example` | Пример переменных окружения |
| `.claude/settings.local.json.example` | `./.claude/settings.local.json.example` | Образец локальных настроек Claude Code |

#### Алгоритм копирования

```python
def copy_project_templates(project_name: str, project_slug: str) -> None:
    """
    Копирует шаблоны проекта из фреймворка в ЦП.

    Args:
        project_name: Название проекта (для подстановки)
        project_slug: Slug проекта (для путей)
    """
    templates_dir = Path(".aidd/templates/project")

    # Плейсхолдеры для замены
    placeholders = {
        "{{PROJECT_NAME}}": project_name,
        "{{PROJECT_SLUG}}": project_slug,
        "{{PROJECT_DESCRIPTION}}": "",  # Заполняется позже в /idea
        "{{CREATED_DATE}}": datetime.now().strftime("%Y-%m-%d"),
        "{{MODE}}": "CREATE",
        "{{DATABASE}}": "PostgreSQL",
        "{{REPO_URL}}": "",
        "{{AUTHOR}}": "",
        "{{EMAIL}}": "",
        "{{SERVICE_NAME}}": project_slug,
    }

    # Копирование файлов
    for template_file in templates_dir.glob("*.template"):
        target_name = template_file.stem  # Убираем .template
        target_path = Path(target_name)

        # НЕ перезаписывать существующие файлы
        if target_path.exists():
            print(f"⏭️  {target_name} уже существует, пропускаем")
            continue

        # Читаем шаблон и заменяем плейсхолдеры
        content = template_file.read_text()
        for placeholder, value in placeholders.items():
            content = content.replace(placeholder, value)

        # Записываем файл
        target_path.write_text(content)
        print(f"✓ Создан {target_name}")
```

#### Плейсхолдеры в шаблонах

| Плейсхолдер | Описание | Пример значения |
|-------------|----------|-----------------|
| `{{PROJECT_NAME}}` | Название проекта | `Restaurant Booking` |
| `{{PROJECT_SLUG}}` | Slug для путей | `restaurant-booking` |
| `{{PROJECT_DESCRIPTION}}` | Описание проекта | `Сервис бронирования столиков` |
| `{{CREATED_DATE}}` | Дата создания | `2025-12-21` |
| `{{MODE}}` | Режим работы | `CREATE` или `FEATURE` |
| `{{DATABASE}}` | Тип БД | `PostgreSQL` |
| `{{SERVICE_NAME}}` | Имя сервиса | `booking` |
| `{{REPO_URL}}` | URL репозитория | `https://github.com/...` |
| `{{AUTHOR}}` | Автор | `John Doe` |
| `{{EMAIL}}` | Email | `john@example.com` |

#### Идемпотентность

Файлы НЕ перезаписываются, если уже существуют. Это позволяет:
- Безопасно запускать `/aidd-init` повторно
- Сохранять пользовательские изменения в файлах ЦП

#### Генерация CHANGELOG.md

**Для нового проекта**:
- Копируется шаблон `changelog-template.md` → `CHANGELOG.md`
- Содержит только секцию `[Unreleased]` с заглушками

**Для существующего проекта** (если есть `features_registry`):
- Автоматически генерируется из истории фич
- Для каждой DEPLOYED фичи создаётся секция на основе Completion Report
- Секции добавляются в обратной хронологии (новые сверху)

```python
def generate_changelog_if_needed(state: dict) -> None:
    """
    Генерирует CHANGELOG.md на основе features_registry.

    Вызывается при /aidd-init если:
    - CHANGELOG.md не существует
    - features_registry не пуст (есть DEPLOYED фичи)
    """
    changelog_path = Path("CHANGELOG.md")

    # Если CHANGELOG уже существует — не трогать
    if changelog_path.exists():
        print("⏭️ CHANGELOG.md уже существует, пропускаем")
        return

    # Если нет фич — использовать шаблон
    if not state.get("features_registry"):
        copy_template("changelog-template.md", "CHANGELOG.md")
        print("✓ Создан CHANGELOG.md (пустой шаблон)")
        return

    # Есть фичи — генерировать из истории
    changelog_content = build_changelog_from_registry(state["features_registry"])
    changelog_path.write_text(changelog_content)
    print(f"✓ Создан CHANGELOG.md ({len(state['features_registry'])} фич)")
```

### 4. Копирование slash-команд

> **Назначение**: Сделать команды AIDD видимыми в автодополнении Claude Code CLI.
>
> **Проблема**: Claude Code ищет slash-команды только в `{project}/.claude/commands/`.
> Когда фреймворк подключен как submodule (`.aidd/`), команды из `.aidd/.claude/commands/`
> не регистрируются автоматически.

#### Алгоритм копирования

```python
from pathlib import Path
import shutil


def copy_slash_commands() -> int:
    """
    Копирует slash-команды из фреймворка в проект.

    Returns:
        Количество скопированных/обновлённых команд
    """
    framework_commands = Path(".aidd/.claude/commands")
    project_commands = Path(".claude/commands")

    # VERIFY: Проверить существование фреймворка
    if not framework_commands.exists():
        print("⚠️ Директория .aidd/.claude/commands/ не найдена")
        return 0

    # ACT: Создать директорию если не существует
    project_commands.mkdir(parents=True, exist_ok=True)

    copied = 0
    updated = 0
    skipped = 0

    for cmd_file in framework_commands.glob("*.md"):
        target = project_commands / cmd_file.name

        if target.exists():
            # Сравнить содержимое
            if cmd_file.read_text() == target.read_text():
                skipped += 1
                continue
            # Файл изменился — обновить
            shutil.copy2(cmd_file, target)
            updated += 1
        else:
            # Файл не существует — скопировать
            shutil.copy2(cmd_file, target)
            copied += 1

    print(f"✓ Команды: {copied} скопировано, {updated} обновлено, {skipped} актуальны")
    return copied + updated
```

#### Bash-эквивалент

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

#### Результат

```
.claude/
└── commands/
    ├── init.md          ← Копия из .aidd/
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

#### Обновление при `git submodule update`

При обновлении submodule `.aidd/` команды могут измениться.
Повторный запуск `/aidd-init` обновит изменённые файлы.

### 5. Определение naming_version (v2.4+)

> **Назначение**: Определить какую структуру артефактов использовать (v2 или v3).

#### Алгоритм

```python
def determine_naming_version() -> str:
    """
    Определить naming_version для нового проекта.

    Returns:
        "v2" (старая структура, backward compatible) или
        "v3" (новая структура с префиксом _)

    Логика:
        - По умолчанию: "v2" (backward compatible)
        - v3 активируется только после явной миграции
    """
    # Проверить существование старой структуры
    old_structure = [
        Path("ai-docs/docs/prd"),
        Path("ai-docs/docs/architecture"),
        Path("ai-docs/docs/plans"),
        Path("ai-docs/docs/reports"),
    ]

    # Проверить существование новой структуры
    new_structure = [
        Path("ai-docs/docs/_analysis"),
        Path("ai-docs/docs/_research"),
        Path("ai-docs/docs/_plans/mvp"),
        Path("ai-docs/docs/_plans/features"),
        Path("ai-docs/docs/_validation"),
    ]

    old_exists = any(p.exists() for p in old_structure)
    new_exists = any(p.exists() for p in new_structure)

    if new_exists and not old_exists:
        # Уже мигрирован на v3
        return "v3"
    else:
        # По умолчанию v2 (backward compatible)
        return "v2"
```

#### Результат

В `.pipeline-state.json` устанавливается:

```json
{
  "naming_version": "v2",  // или "v3" после миграции
  ...
}
```

**Использование**:
- Команды `/aidd-analyze`, `/aidd-plan` проверяют `naming_version` и создают артефакты в соответствующих папках
- Миграция v2 → v3: `python .aidd/scripts/migrate-naming-v3.py`

---

## Качественные ворота

### BOOTSTRAP_READY

| Критерий | Описание |
|----------|----------|
| Git | Проект — git репозиторий |
| Фреймворк | `.aidd/CLAUDE.md` существует |
| Python | Версия >= 3.11 |
| Docker | Установлен |
| Структура | Папки `ai-docs/docs/` созданы |
| Claude | Папка `.claude/` создана |
| Состояние | `.pipeline-state.json` создан |

---

## Вывод команды

### Успешная инициализация

```
┌─────────────────────────────────────────────────────────────────┐
│                    BOOTSTRAP PIPELINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Проверка окружения:                                             │
│  ✓ Git репозиторий инициализирован                              │
│  ✓ Фреймворк .aidd/ подключен                                   │
│  ✓ Python 3.11.5 >= 3.11                                        │
│  ✓ Docker установлен                                            │
│                                                                  │
│  Инициализация:                                                  │
│  ✓ Создана структура ai-docs/docs/                              │
│  ✓ Создана папка .claude/                                       │
│  ✓ Скопировано 10 команд в .claude/commands/                    │
│  ✓ Создан .pipeline-state.json                                  │
│  ✓ Создан CLAUDE.md (с таблицами команд и агентов)              │
│                                                                  │
│  ────────────────────────────────────────────────────────────── │
│  ✓ BOOTSTRAP_READY                                               │
│                                                                  │
│  Доступные команды: /aidd-analyze /aidd-research /aidd-plan /aidd-code            │
│                     /aidd-validate /aidd-plan-feature                                │
│                                                                  │
│  Следующий шаг: /aidd-analyze "Описание вашего проекта"                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Ошибки проверок

```
┌─────────────────────────────────────────────────────────────────┐
│                    BOOTSTRAP PIPELINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Проверка окружения:                                             │
│  ✓ Git репозиторий инициализирован                              │
│  ✗ Фреймворк .aidd/ НЕ НАЙДЕН                                   │
│  ✓ Python 3.11.5 >= 3.11                                        │
│  ✗ Docker НЕ УСТАНОВЛЕН                                         │
│                                                                  │
│  ────────────────────────────────────────────────────────────── │
│  ✗ BOOTSTRAP_READY: 2 ошибки                                    │
│                                                                  │
│  Исправьте ошибки:                                               │
│                                                                  │
│  1. Подключите фреймворк:                                        │
│     git submodule add https://github.com/.../aidd-mvp-generator.git .aidd
│                                                                  │
│  2. Установите Docker:                                           │
│     https://docs.docker.com/get-docker/                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Успешная инициализация (EXISTING_PROJECT)

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
│  • CLAUDE.md — кастомная документация (3.2 KB)                   │
│                                                                  │
│  Решения пользователя:                                           │
│  ✓ CLAUDE.md — сохранена текущая версия                         │
│  ✓ README.md — сохранена текущая версия                         │
│  ✓ .gitignore — сохранена текущая версия                        │
│  ✓ .pipeline-state.json — создан                                │
│  ⏭️  ai-docs/docs/ — пропущено (проект использует services/)     │
│  ✓ .claude/ — создана                                           │
│  ✓ Скопировано 10 команд в .claude/commands/                    │
│                                                                  │
│  ────────────────────────────────────────────────────────────── │
│  ✓ BOOTSTRAP_READY                                               │
│                                                                  │
│  Доступные команды: /aidd-analyze /aidd-research /aidd-plan /aidd-code            │
│                     /aidd-validate /aidd-plan-feature                                │
│                                                                  │
│  Следующий шаг: /aidd-analyze "Описание новой фичи"                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Идемпотентность

Команда `/aidd-init` идемпотентна — повторный запуск безопасен:

| Состояние | Поведение |
|-----------|-----------|
| Папки существуют | Пропускает создание |
| `.pipeline-state.json` существует | Проверяет/обновляет `BOOTSTRAP_READY` |
| `CLAUDE.md` существует | Не перезаписывает |

---

## Примеры использования

### Новый проект с нуля

```bash
# 1. Создать директорию проекта
mkdir my-awesome-project && cd my-awesome-project

# 2. Инициализировать git
git init

# 3. Подключить фреймворк
git submodule add https://github.com/your-org/aidd-mvp-generator.git .aidd

# 4. Запустить Claude Code
claude

# 5. Инициализировать проект
/init

# 6. Начать работу
/idea "Описание проекта"
```

### Проверка окружения

```bash
# Проверить готовность без изменений
/init

# Если есть ошибки — исправить и повторить
/init
```

---

## Чеклист ворот BOOTSTRAP_READY

> ⚠️ AI ОБЯЗАН создать TodoWrite с этими пунктами.

- [ ] 🔴 Целевой проект определён (cwd = корень ЦП)
- [ ] 🔴 `.pipeline-state.json` создан
- [ ] 🔴 Структура `ai-docs/docs/` создана
- [ ] 🟡 `.claude/commands/` скопированы из `.aidd/`
- [ ] 🟡 `CLAUDE.md` целевого проекта существует
- [ ] 🟡 `CHANGELOG.md` создан (шаблон или из истории)
- [ ] 🔴 `.pipeline-state.json` обновлён (gate: BOOTSTRAP_READY)
- [ ] ⚪ `README.md` обновлён (если существует)

---

## Следующий шаг

После прохождения ворот `BOOTSTRAP_READY`:

```bash
/idea "Описание вашего проекта или фичи"
```

---

## См. также

- [docs/PIPELINE-TREE.md](../../docs/PIPELINE-TREE.md) — Дерево пайплайнов
- [docs/target-project-structure.md](../../docs/target-project-structure.md) — Структура ЦП
- [workflow.md](../../workflow.md) — Процесс разработки
