#!/usr/bin/env python3
"""
Git-хелперы для параллельных пайплайнов AIDD.

Функции:
- create_feature_branch: Создание ветки для новой фичи
- get_current_branch: Получение текущей ветки
- get_current_feature_context: Определение FID по git ветке
- merge_pipeline_states: Объединение состояний при merge
- check_file_conflicts: Детекция конфликтов файлов между ветками
- complete_feature_merge: Завершение фичи и перенос в registry

Использование:
    python3 scripts/git_helpers.py <command> [args]

Команды:
    branch <fid> <slug>     Создать ветку feature/{fid}-{slug}
    context                  Показать текущий контекст фичи
    conflicts <fid1> <fid2>  Проверить конфликты между фичами
    merge <fid>              Завершить фичу и подготовить к merge
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_current_branch() -> str:
    """Получить имя текущей git ветки."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Ошибка git: {result.stderr}")
    return result.stdout.strip()


def create_feature_branch(fid: str, slug: str) -> str:
    """
    Создать git ветку для новой фичи.

    Args:
        fid: Feature ID (F001, F002, ...)
        slug: Slug фичи в kebab-case (table-booking)

    Returns:
        Имя созданной ветки

    Raises:
        RuntimeError: Если ветка уже существует или ошибка git
    """
    branch = f"feature/{fid}-{slug}"

    # Проверить, что ветка не существует
    result = subprocess.run(
        ["git", "show-ref", "--verify", f"refs/heads/{branch}"],
        capture_output=True
    )
    if result.returncode == 0:
        raise RuntimeError(f"Ветка {branch} уже существует")

    # Создать и переключиться на ветку
    result = subprocess.run(
        ["git", "checkout", "-b", branch],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Ошибка создания ветки: {result.stderr}")

    print(f"✓ Создана ветка: {branch}")
    return branch


def get_current_feature_context(state: dict) -> Optional[tuple[str, dict]]:
    """
    Определить текущую фичу по git ветке.

    Args:
        state: Содержимое .pipeline-state.json (v2)

    Returns:
        (fid, pipeline) или None если не в ветке фичи

    Алгоритм:
        1. Получить текущую git ветку
        2. Найти FID в active_pipelines по branch
        3. Если ветка не найдена, но есть только одна активная фича — использовать её
    """
    try:
        current_branch = get_current_branch()
    except RuntimeError:
        return None

    active_pipelines = state.get("active_pipelines", {})

    # Поиск по ветке
    for fid, pipeline in active_pipelines.items():
        if pipeline.get("branch") == current_branch:
            return (fid, pipeline)

    # Извлечь FID из имени ветки (feature/F001-slug → F001)
    if current_branch.startswith("feature/"):
        parts = current_branch.replace("feature/", "").split("-")
        if parts and parts[0].startswith("F"):
            potential_fid = parts[0]
            if potential_fid in active_pipelines:
                return (potential_fid, active_pipelines[potential_fid])

    # Если только одна активная фича — использовать её
    if len(active_pipelines) == 1:
        fid = list(active_pipelines.keys())[0]
        print(f"⚠️  Используется единственная активная фича: {fid}")
        return (fid, active_pipelines[fid])

    # Не в контексте фичи
    return None


def get_modified_files(branch: str, base_branch: str = "main") -> list[str]:
    """
    Получить список файлов, изменённых в ветке относительно base.

    Args:
        branch: Ветка фичи
        base_branch: Базовая ветка для сравнения

    Returns:
        Список путей к изменённым файлам
    """
    # Найти общего предка
    result = subprocess.run(
        ["git", "merge-base", base_branch, branch],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        # Попробовать с master если main не существует
        result = subprocess.run(
            ["git", "merge-base", "master", branch],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return []

    merge_base = result.stdout.strip()

    # Получить список изменённых файлов
    result = subprocess.run(
        ["git", "diff", "--name-only", merge_base, branch],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return []

    return [f for f in result.stdout.strip().split("\n") if f]


def check_file_conflicts(state: dict, fid_a: str, fid_b: str) -> list[str]:
    """
    Проверить, редактируют ли две фичи одни и те же файлы.

    Args:
        state: Содержимое .pipeline-state.json (v2)
        fid_a: Feature ID первой фичи
        fid_b: Feature ID второй фичи

    Returns:
        Список конфликтующих файлов
    """
    active = state.get("active_pipelines", {})

    if fid_a not in active or fid_b not in active:
        raise ValueError(f"Фичи {fid_a} или {fid_b} не найдены в active_pipelines")

    branch_a = active[fid_a].get("branch")
    branch_b = active[fid_b].get("branch")

    if not branch_a or not branch_b:
        return []

    files_a = set(get_modified_files(branch_a))
    files_b = set(get_modified_files(branch_b))

    conflicts = files_a & files_b

    # Исключить .pipeline-state.json — он всегда конфликтует
    conflicts.discard(".pipeline-state.json")

    return list(conflicts)


def merge_pipeline_states(
    main_state: dict,
    feature_state: dict,
    fid: str
) -> dict:
    """
    Объединить состояния после merge feature ветки в main.

    Args:
        main_state: Состояние из main
        feature_state: Состояние из feature ветки
        fid: Feature ID завершённой фичи

    Returns:
        Объединённое состояние
    """
    result = json.loads(json.dumps(main_state))  # Deep copy
    now = datetime.now()

    # 1. Перенести фичу в registry
    if fid in feature_state.get("active_pipelines", {}):
        pipeline = feature_state["active_pipelines"][fid]

        result.setdefault("features_registry", {})
        result["features_registry"][fid] = {
            "name": pipeline.get("name"),
            "title": pipeline.get("title"),
            "status": "DEPLOYED",
            "created": pipeline.get("created"),
            "deployed": now.strftime("%Y-%m-%d"),
            "artifacts": pipeline.get("artifacts", {}),
            "services": pipeline.get("services", [])
        }

    # 2. Удалить из active_pipelines
    if fid in result.get("active_pipelines", {}):
        del result["active_pipelines"][fid]

    # 3. Синхронизировать next_feature_id (взять максимум)
    result["next_feature_id"] = max(
        main_state.get("next_feature_id", 1),
        feature_state.get("next_feature_id", 1)
    )

    # 4. Обновить timestamp
    result["updated_at"] = now.isoformat()

    return result


def complete_feature_merge(state: dict, fid: str) -> dict:
    """
    Завершить фичу и подготовить к merge.

    Перемещает фичу из active_pipelines в features_registry
    со статусом DEPLOYED.

    Args:
        state: Содержимое .pipeline-state.json (v2)
        fid: Feature ID завершённой фичи

    Returns:
        Обновлённое состояние
    """
    if fid not in state.get("active_pipelines", {}):
        raise ValueError(f"Фича {fid} не найдена в active_pipelines")

    pipeline = state["active_pipelines"][fid]
    now = datetime.now()

    # Проверить, что все ворота пройдены
    gates = pipeline.get("gates", {})
    required_gates = [
        "PRD_READY", "RESEARCH_DONE", "PLAN_APPROVED",
        "IMPLEMENT_OK", "REVIEW_OK", "QA_PASSED", "ALL_GATES_PASSED"
    ]

    missing = [g for g in required_gates if not gates.get(g, {}).get("passed")]
    if missing:
        raise ValueError(f"Не все ворота пройдены: {missing}")

    # Отметить DEPLOYED
    pipeline["gates"]["DEPLOYED"] = {
        "passed": True,
        "passed_at": now.isoformat()
    }

    # Перенести в registry
    state.setdefault("features_registry", {})
    state["features_registry"][fid] = {
        "name": pipeline.get("name"),
        "title": pipeline.get("title"),
        "status": "DEPLOYED",
        "created": pipeline.get("created"),
        "deployed": now.strftime("%Y-%m-%d"),
        "artifacts": pipeline.get("artifacts", {}),
        "services": pipeline.get("services", [])
    }

    # Удалить из active_pipelines
    del state["active_pipelines"][fid]

    # Обновить timestamp
    state["updated_at"] = now.isoformat()

    return state


def print_conflict_warning(conflicts: list[str], fid_a: str, fid_b: str) -> None:
    """Вывести предупреждение о конфликтах."""
    if not conflicts:
        print(f"✓ Нет конфликтов между {fid_a} и {fid_b}")
        return

    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│  ⚠️ ПРЕДУПРЕЖДЕНИЕ: Обнаружены потенциальные конфликты          │")
    print("├─────────────────────────────────────────────────────────────────┤")
    print(f"│  Фичи {fid_a} и {fid_b} редактируют одни файлы:{'':>25}│")
    for f in conflicts[:5]:
        line = f"  • {f}"
        print(f"│{line:<63}│")
    if len(conflicts) > 5:
        print(f"│  ... и ещё {len(conflicts) - 5} файлов{'':>42}│")
    print("│" + " " * 65 + "│")
    print("│  Рекомендации:                                                  │")
    print("│  1. Завершить и смержить одну фичу перед продолжением другой    │")
    print("│  2. Разделить изменения на разные модули                        │")
    print("│  3. Координировать merge с командой                             │")
    print("└─────────────────────────────────────────────────────────────────┘")


def cmd_branch(args: list[str]) -> int:
    """Команда: создать ветку для фичи."""
    if len(args) < 2:
        print("Использование: git_helpers.py branch <fid> <slug>")
        return 1

    fid, slug = args[0], args[1]

    try:
        branch = create_feature_branch(fid, slug)
        print(f"Ветка создана: {branch}")
        return 0
    except RuntimeError as e:
        print(f"❌ {e}")
        return 1


def cmd_context(args: list[str]) -> int:
    """Команда: показать текущий контекст фичи."""
    state_path = Path(".pipeline-state.json")

    if not state_path.exists():
        print("❌ .pipeline-state.json не найден")
        return 1

    state = json.loads(state_path.read_text())

    context = get_current_feature_context(state)
    if context:
        fid, pipeline = context
        print(f"✓ Текущая фича: {fid}")
        print(f"  Название: {pipeline.get('title')}")
        print(f"  Ветка: {pipeline.get('branch')}")
        print(f"  Этап: {pipeline.get('stage')}")

        gates = pipeline.get("gates", {})
        passed = [g for g, v in gates.items() if v.get("passed")]
        print(f"  Ворота пройдены: {', '.join(passed) or 'нет'}")
    else:
        print("⚠️  Не в контексте фичи")
        branch = get_current_branch()
        print(f"  Текущая ветка: {branch}")

        active = state.get("active_pipelines", {})
        if active:
            print(f"  Активные фичи: {', '.join(active.keys())}")
        else:
            print("  Нет активных фич")

    return 0


def cmd_conflicts(args: list[str]) -> int:
    """Команда: проверить конфликты между фичами."""
    if len(args) < 2:
        print("Использование: git_helpers.py conflicts <fid1> <fid2>")
        return 1

    fid_a, fid_b = args[0], args[1]
    state_path = Path(".pipeline-state.json")

    if not state_path.exists():
        print("❌ .pipeline-state.json не найден")
        return 1

    state = json.loads(state_path.read_text())

    try:
        conflicts = check_file_conflicts(state, fid_a, fid_b)
        print_conflict_warning(conflicts, fid_a, fid_b)
        return 1 if conflicts else 0
    except ValueError as e:
        print(f"❌ {e}")
        return 1


def cmd_merge(args: list[str]) -> int:
    """Команда: завершить фичу и подготовить к merge."""
    if len(args) < 1:
        print("Использование: git_helpers.py merge <fid>")
        return 1

    fid = args[0]
    state_path = Path(".pipeline-state.json")

    if not state_path.exists():
        print("❌ .pipeline-state.json не найден")
        return 1

    state = json.loads(state_path.read_text())

    try:
        updated_state = complete_feature_merge(state, fid)
        state_path.write_text(json.dumps(updated_state, indent=2, ensure_ascii=False))
        print(f"✓ Фича {fid} завершена и перемещена в features_registry")
        print(f"  Теперь можно выполнить: git merge {state['active_pipelines'].get(fid, {}).get('branch', '')}")
        return 0
    except ValueError as e:
        print(f"❌ {e}")
        return 1


def main():
    """Точка входа."""
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "branch": cmd_branch,
        "context": cmd_context,
        "conflicts": cmd_conflicts,
        "merge": cmd_merge,
    }

    if command not in commands:
        print(f"❌ Неизвестная команда: {command}")
        print(f"Доступные команды: {', '.join(commands.keys())}")
        return 1

    return commands[command](args)


if __name__ == "__main__":
    sys.exit(main())
