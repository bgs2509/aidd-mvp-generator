#!/usr/bin/env python3
"""
Скрипт миграции .pipeline-state.json с версии 1.0 на 2.0.

Использование:
    python scripts/migrate_pipeline_state.py [--dry-run] [--project-dir PATH]

Флаги:
    --dry-run       Показать что будет сделано, но не изменять файлы
    --project-dir   Путь к целевому проекту (по умолчанию: текущая директория)

Описание:
    1. Читает существующий .pipeline-state.json
    2. Определяет версию (v1 если version != "2.0")
    3. Мигрирует структуру:
       - gates → global_gates (только BOOTSTRAP_READY)
       - current_feature → active_pipelines[FID]
       - Локальные ворота переносятся в active_pipelines[FID].gates
    4. Создаёт резервную копию (.pipeline-state.json.v1.backup)
    5. Сохраняет новый файл

Автор: AIDD-MVP Generator
Версия: 1.0
"""

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


def get_current_git_branch() -> str | None:
    """Получить текущую git ветку."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def slugify(text: str) -> str:
    """Преобразовать текст в slug (kebab-case)."""
    slug = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ]+", "-", text.lower()).strip("-")
    # Транслитерация кириллицы
    translit_map = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
    result = ""
    for char in slug:
        result += translit_map.get(char, char)
    return result[:30]


def create_empty_feature_gates() -> dict[str, Any]:
    """Создать пустую структуру ворот для фичи."""
    return {
        "PRD_READY": {"passed": False, "passed_at": None, "artifact": None},
        "RESEARCH_DONE": {"passed": False, "passed_at": None},
        "PLAN_APPROVED": {"passed": False, "passed_at": None, "artifact": None, "approved_by": None},
        "IMPLEMENT_OK": {"passed": False, "passed_at": None},
        "REVIEW_OK": {"passed": False, "passed_at": None, "artifact": None},
        "QA_PASSED": {"passed": False, "passed_at": None, "artifact": None, "coverage": None},
        "ALL_GATES_PASSED": {"passed": False, "passed_at": None, "artifact": None},
        "DEPLOYED": {"passed": False, "passed_at": None},
    }


def migrate_v1_to_v2(state_v1: dict[str, Any]) -> dict[str, Any]:
    """
    Мигрирует .pipeline-state.json с версии 1.0 на 2.0.

    Args:
        state_v1: Состояние в формате v1

    Returns:
        Состояние в формате v2
    """
    now = datetime.now().isoformat()
    today = now[:10]

    # Базовая структура v2
    state_v2: dict[str, Any] = {
        "$schema": "pipeline-state-schema",
        "version": "2.0",
        "project_name": state_v1.get("project_name", ""),
        "mode": state_v1.get("mode", "CREATE"),
        "init_mode": state_v1.get("init_mode", "NEW_PROJECT"),
        "init_decisions": state_v1.get("init_decisions", {}),
        "parallel_mode": False,  # По умолчанию выключен для совместимости
        "created_at": state_v1.get("created_at", now),
        "updated_at": now,
        "global_gates": {
            "BOOTSTRAP_READY": state_v1.get("gates", {}).get("BOOTSTRAP_READY", {
                "passed": False,
                "passed_at": None,
                "checks": {"git": None, "framework": None, "python": None, "docker": None}
            })
        },
        "active_pipelines": {},
        "features_registry": state_v1.get("features_registry", {}),
        "next_feature_id": state_v1.get("next_feature_id", 1),
        "services": state_v1.get("services", []),
    }

    # Мигрируем current_feature в active_pipelines если есть
    current_feature = state_v1.get("current_feature")
    old_gates = state_v1.get("gates", {})

    # Проверяем есть ли активная фича (по воротам или current_feature)
    has_active_work = any(
        gate.get("passed", False)
        for name, gate in old_gates.items()
        if name != "BOOTSTRAP_READY" and isinstance(gate, dict)
    )

    if current_feature and isinstance(current_feature, dict) and current_feature.get("id"):
        # Есть явный current_feature
        fid = current_feature.get("id", "F001")
        name = current_feature.get("name", "migrated")
        title = current_feature.get("title", "Мигрированная фича")
        created = current_feature.get("created", today)
        stage = current_feature.get("stage", "IDEA")
        artifacts = current_feature.get("artifacts", {})

        # Определяем ветку
        current_branch = get_current_git_branch()
        branch = f"feature/{fid}-{slugify(name)}"
        if current_branch and current_branch.startswith("feature/"):
            branch = current_branch

        # Копируем ворота (кроме BOOTSTRAP_READY)
        feature_gates = create_empty_feature_gates()
        for gate_name, gate_data in old_gates.items():
            if gate_name != "BOOTSTRAP_READY" and gate_name in feature_gates:
                if isinstance(gate_data, dict):
                    feature_gates[gate_name] = gate_data

        state_v2["active_pipelines"][fid] = {
            "branch": branch,
            "name": name,
            "title": title,
            "stage": stage,
            "created": created,
            "gates": feature_gates,
            "artifacts": artifacts,
        }

        # Обновляем next_feature_id если нужно
        match = re.match(r"F(\d+)", fid)
        if match:
            fid_num = int(match.group(1))
            state_v2["next_feature_id"] = max(state_v2["next_feature_id"], fid_num + 1)

    elif has_active_work:
        # Нет current_feature, но есть прогресс по воротам — создаём фичу
        fid = f"F{state_v2['next_feature_id']:03d}"
        state_v2["next_feature_id"] += 1

        # Определяем stage по пройденным воротам
        stage = "IDEA"
        stage_map = [
            ("DEPLOYED", "DEPLOYED"),
            ("ALL_GATES_PASSED", "VALIDATED"),
            ("QA_PASSED", "QA"),
            ("REVIEW_OK", "REVIEW"),
            ("IMPLEMENT_OK", "IMPLEMENT"),
            ("PLAN_APPROVED", "GENERATE"),
            ("RESEARCH_DONE", "PLAN"),
            ("PRD_READY", "RESEARCH"),
        ]
        for gate_name, stage_name in stage_map:
            if old_gates.get(gate_name, {}).get("passed", False):
                stage = stage_name
                break

        # Получаем ветку
        current_branch = get_current_git_branch()
        branch = f"feature/{fid}-migrated"
        if current_branch and current_branch.startswith("feature/"):
            branch = current_branch

        # Копируем ворота
        feature_gates = create_empty_feature_gates()
        for gate_name, gate_data in old_gates.items():
            if gate_name != "BOOTSTRAP_READY" and gate_name in feature_gates:
                if isinstance(gate_data, dict):
                    feature_gates[gate_name] = gate_data

        # Собираем артефакты из старого формата
        old_artifacts = state_v1.get("artifacts", {})
        artifacts = {}
        for art_type in ["prd", "plan", "feature_plan", "review_report", "qa_report", "validation_report"]:
            if old_artifacts.get(art_type):
                # Нормализуем имя типа
                normalized = art_type.replace("_report", "").replace("feature_", "")
                artifacts[normalized] = old_artifacts[art_type]

        state_v2["active_pipelines"][fid] = {
            "branch": branch,
            "name": "migrated",
            "title": "Мигрированная фича (из v1)",
            "stage": stage,
            "created": today,
            "gates": feature_gates,
            "artifacts": artifacts,
        }

    return state_v2


def is_v1_state(state: dict[str, Any]) -> bool:
    """Проверить, является ли состояние версией 1.0."""
    version = state.get("version", "1.0")
    return version != "2.0"


def migrate(project_dir: Path, dry_run: bool = False) -> bool:
    """
    Выполнить миграцию .pipeline-state.json.

    Args:
        project_dir: Путь к проекту
        dry_run: Если True, только показать план

    Returns:
        True если миграция выполнена/нужна, False если уже v2
    """
    state_path = project_dir / ".pipeline-state.json"

    if not state_path.exists():
        print(f"Файл {state_path} не найден")
        return False

    # Читаем текущее состояние
    try:
        state_v1 = json.loads(state_path.read_text())
    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON: {e}")
        return False

    # Проверяем версию
    if not is_v1_state(state_v1):
        print(f"✓ Файл уже в формате v2.0, миграция не требуется")
        return False

    current_version = state_v1.get("version", "1.0")
    print(f"Обнаружена версия: {current_version}")
    print("Требуется миграция на v2.0")
    print()

    # Выполняем миграцию
    state_v2 = migrate_v1_to_v2(state_v1)

    # Выводим план изменений
    print("=" * 60)
    print("ПЛАН МИГРАЦИИ")
    print("=" * 60)
    print()

    print("Структурные изменения:")
    print("  • gates → global_gates (только BOOTSTRAP_READY)")
    print("  • Локальные ворота → active_pipelines[FID].gates")
    if state_v1.get("current_feature"):
        print("  • current_feature → active_pipelines")
    print("  • Добавлено: parallel_mode, version 2.0")
    print()

    if state_v2["active_pipelines"]:
        print("Активные пайплайны после миграции:")
        for fid, pipeline in state_v2["active_pipelines"].items():
            print(f"  {fid}: {pipeline['title']}")
            print(f"       Ветка: {pipeline['branch']}")
            print(f"       Этап: {pipeline['stage']}")
            passed_gates = [
                g for g, d in pipeline["gates"].items()
                if d.get("passed", False)
            ]
            if passed_gates:
                print(f"       Ворота: {', '.join(passed_gates)}")
        print()

    if state_v2["features_registry"]:
        print(f"Завершённых фич в реестре: {len(state_v2['features_registry'])}")
        print()

    print(f"next_feature_id: {state_v2['next_feature_id']}")
    print()

    if dry_run:
        print("[DRY RUN] Файлы не изменены")
        print()
        print("Предпросмотр нового состояния:")
        print("-" * 40)
        # Убираем $example для чистого вывода
        preview = {k: v for k, v in state_v2.items() if not k.startswith("$")}
        print(json.dumps(preview, indent=2, ensure_ascii=False))
        return True

    # Создаём резервную копию
    backup_path = state_path.with_suffix(".json.v1.backup")
    shutil.copy2(state_path, backup_path)
    print(f"✓ Создана резервная копия: {backup_path.name}")

    # Сохраняем новое состояние
    state_path.write_text(json.dumps(state_v2, indent=2, ensure_ascii=False))
    print(f"✓ Сохранено: {state_path.name}")

    print()
    print("=" * 60)
    print("МИГРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)

    return True


def ensure_v2(project_dir: Path | None = None) -> dict[str, Any] | None:
    """
    Проверить и автоматически мигрировать .pipeline-state.json на v2.

    Эта функция предназначена для вызова из slash-команд.

    Args:
        project_dir: Путь к проекту (по умолчанию: текущая директория)

    Returns:
        Состояние в формате v2 или None если файл не найден
    """
    if project_dir is None:
        project_dir = Path.cwd()

    state_path = project_dir / ".pipeline-state.json"

    if not state_path.exists():
        return None

    try:
        state = json.loads(state_path.read_text())
    except json.JSONDecodeError:
        return None

    if is_v1_state(state):
        print("⚠️  Обнаружен .pipeline-state.json v1.0")
        print("    Выполняется автоматическая миграция на v2.0...")

        state_v2 = migrate_v1_to_v2(state)

        # Резервная копия
        backup_path = state_path.with_suffix(".json.v1.backup")
        shutil.copy2(state_path, backup_path)

        # Сохранение
        state_path.write_text(json.dumps(state_v2, indent=2, ensure_ascii=False))
        print(f"    ✓ Миграция завершена. Резервная копия: {backup_path.name}")
        print()

        return state_v2

    return state


def main():
    parser = argparse.ArgumentParser(
        description="Миграция .pipeline-state.json с v1.0 на v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
    # Показать план миграции (без изменений)
    python scripts/migrate_pipeline_state.py --dry-run

    # Выполнить миграцию в текущей директории
    python scripts/migrate_pipeline_state.py

    # Выполнить миграцию в указанном проекте
    python scripts/migrate_pipeline_state.py --project-dir /path/to/project
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Показать план миграции без изменения файлов",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Путь к целевому проекту (по умолчанию: текущая директория)",
    )

    args = parser.parse_args()
    migrate(args.project_dir, args.dry_run)


if __name__ == "__main__":
    main()
