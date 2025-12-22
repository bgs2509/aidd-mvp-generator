---
allowed-tools: Read(*), Glob(*), Grep(*), Bash(git :*), Bash(python3 :*), Bash(docker :*), Bash(mkdir :*), Write(**/*.md), Write(**/*.json)
description: Инициализация целевого проекта (Bootstrap Pipeline)
---

# Команда: /init

> Запускает Bootstrap Pipeline для инициализации целевого проекта.

---

## Синтаксис

```bash
/init
```

---

## Описание

Команда `/init` выполняет проверку окружения и инициализацию структуры
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
| Новый проект, первый запуск | `/init` (рекомендуется) или сразу `/idea` |
| Проверить готовность окружения | `/init` |
| Исправить проблемы инициализации | `/init` |

**Примечание**: Команда `/idea` автоматически выполняет проверки bootstrap,
но `/init` позволяет выполнить их явно и получить детальную диагностику.

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
for dir in prd architecture plans reports research; do
    [ -d "ai-docs/docs/$dir" ] || mkdir -p "ai-docs/docs/$dir"
done

[ -d "docs/api" ] || mkdir -p docs/api
[ -d ".claude" ] || mkdir -p .claude
```

**Результат**:
```
{project}/
├── ai-docs/
│   └── docs/
│       ├── prd/           # PRD документы
│       ├── architecture/  # Архитектурные планы
│       ├── plans/         # Планы фич
│       └── reports/       # Отчёты (review, qa, validation)
├── .claude/               # Локальные настройки Claude Code
└── docs/
    └── api/               # API документация (openapi.yaml)
```

### 2. Создание .pipeline-state.json

```json
{
  "project_name": "",
  "mode": "CREATE",
  "current_stage": 0,
  "created_at": "2025-12-21T10:00:00Z",
  "gates": {
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
  "artifacts": {}
}
```

### 3. Копирование файлов из шаблонов

> **ВАЖНО**: Файлы проекта создаются из шаблонов в `.aidd/templates/project/`.
> Это гарантирует единообразие и правильную структуру.

#### Шаблоны проекта

| Шаблон | Создаёт в ЦП | Назначение |
|--------|--------------|------------|
| `CLAUDE.md.template` | `./CLAUDE.md` | Точка входа для AI в ЦП |
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
- Безопасно запускать `/init` повторно
- Сохранять пользовательские изменения в файлах ЦП

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
│  ✓ Создан .pipeline-state.json                                  │
│  ✓ Создан CLAUDE.md                                             │
│                                                                  │
│  ────────────────────────────────────────────────────────────── │
│  ✓ BOOTSTRAP_READY                                               │
│                                                                  │
│  Следующий шаг: /idea "Описание вашего проекта"                 │
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

---

## Идемпотентность

Команда `/init` идемпотентна — повторный запуск безопасен:

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
