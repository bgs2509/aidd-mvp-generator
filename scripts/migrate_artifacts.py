#!/usr/bin/env python3
"""
Скрипт миграции существующих артефактов на новую систему именования.

Использование:
    python scripts/migrate_artifacts.py [--dry-run] [--project-dir PATH]

Флаги:
    --dry-run       Показать что будет сделано, но не изменять файлы
    --project-dir   Путь к целевому проекту (по умолчанию: текущая директория)

Описание:
    1. Анализирует существующие артефакты в ai-docs/docs/
    2. Группирует их по фичам (эвристика по именам)
    3. Присваивает уникальные FID
    4. Переименовывает файлы с добавлением даты и FID
    5. Добавляет YAML frontmatter
    6. Генерирует FEATURES.md
    7. Обновляет .pipeline-state.json

Автор: AIDD-MVP Generator
Версия: 1.0
"""

import argparse
import json
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Artifact:
    """Представление артефакта."""

    path: Path
    type: str  # prd, research, plan, review, qa, validation
    slug: str
    created_date: str | None = None
    feature_group: str | None = None
    new_filename: str | None = None
    frontmatter: dict = field(default_factory=dict)


@dataclass
class Feature:
    """Представление фичи."""

    fid: str
    name: str
    title: str
    created: str
    status: str = "DEPLOYED"
    services: list[str] = field(default_factory=list)
    artifacts: dict[str, str] = field(default_factory=dict)


def get_file_creation_date(filepath: Path) -> str:
    """Получить дату создания файла из git или filesystem."""
    try:
        # Попробовать git log
        result = subprocess.run(
            ["git", "log", "--follow", "--format=%aI", "--reverse", "--", str(filepath)],
            capture_output=True,
            text=True,
            cwd=filepath.parent,
        )
        if result.returncode == 0 and result.stdout.strip():
            first_commit_date = result.stdout.strip().split("\n")[0]
            return first_commit_date[:10]  # YYYY-MM-DD
    except Exception:
        pass

    # Fallback: mtime файла
    mtime = filepath.stat().st_mtime
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")


def extract_slug_from_filename(filename: str) -> str:
    """Извлечь slug из имени файла."""
    # Убрать расширение
    name = filename.rsplit(".", 1)[0]

    # Убрать известные суффиксы типов
    for suffix in ["-prd", "-research", "-plan", "-review", "-qa", "-validation"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break

    # Привести к kebab-case
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")

    # Ограничить длину
    if len(slug) > 30:
        slug = slug[:30].rsplit("-", 1)[0]

    return slug


def detect_artifact_type(filepath: Path) -> str | None:
    """Определить тип артефакта по пути и имени."""
    path_str = str(filepath)
    filename = filepath.name.lower()

    if "/prd/" in path_str or filename.endswith("-prd.md"):
        return "prd"
    elif "/research/" in path_str or filename.endswith("-research.md"):
        return "research"
    elif "/architecture/" in path_str or "/plans/" in path_str:
        if "feature" in filename:
            return "feature-plan"
        return "plan"
    elif "/reports/" in path_str:
        if "review" in filename:
            return "review"
        elif "qa" in filename:
            return "qa"
        elif "validation" in filename:
            return "validation"
    return None


def group_artifacts_by_feature(artifacts: list[Artifact]) -> dict[str, list[Artifact]]:
    """Группировать артефакты по предполагаемым фичам."""
    groups: dict[str, list[Artifact]] = defaultdict(list)

    for artifact in artifacts:
        # Используем slug как ключ группировки
        groups[artifact.slug].append(artifact)

    return dict(groups)


def generate_frontmatter(artifact: Artifact, feature: Feature) -> str:
    """Сгенерировать YAML frontmatter для артефакта."""
    type_to_status = {
        "prd": "PRD_READY",
        "research": "RESEARCH_DONE",
        "plan": "PLAN_APPROVED",
        "feature-plan": "PLAN_APPROVED",
        "review": "REVIEW_OK",
        "qa": "QA_PASSED",
        "validation": "ALL_GATES_PASSED",
    }

    type_to_author = {
        "prd": "AI (Analyst)",
        "research": "AI (Researcher)",
        "plan": "AI (Architect)",
        "feature-plan": "AI (Architect)",
        "review": "AI (Reviewer)",
        "qa": "AI (QA)",
        "validation": "AI (Validator)",
    }

    fm = {
        "feature_id": feature.fid,
        "feature_name": feature.name,
        "title": feature.title,
        "created": artifact.created_date or feature.created,
        "author": type_to_author.get(artifact.type, "AI"),
        "type": artifact.type,
        "status": type_to_status.get(artifact.type, "UNKNOWN"),
        "version": 1,
        "migrated_from": artifact.path.name,
        "migrated_at": datetime.now().strftime("%Y-%m-%d"),
    }

    lines = ["---"]
    for key, value in fm.items():
        if isinstance(value, str):
            lines.append(f'{key}: "{value}"')
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def add_frontmatter_to_content(content: str, frontmatter: str) -> str:
    """Добавить frontmatter к содержимому файла."""
    # Проверить, есть ли уже frontmatter
    if content.startswith("---"):
        # Уже есть frontmatter, заменить
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return frontmatter + parts[2]
    return frontmatter + content


def generate_features_md(features: dict[str, Feature]) -> str:
    """Сгенерировать содержимое FEATURES.md."""
    deployed = [f for f in features.values() if f.status == "DEPLOYED"]
    in_progress = [f for f in features.values() if f.status != "DEPLOYED" and f.status != "ARCHIVED"]
    archived = [f for f in features.values() if f.status == "ARCHIVED"]

    lines = [
        "# Реестр фич проекта",
        "",
        f"> Мигрировано: {datetime.now().strftime('%Y-%m-%d')}",
        "> Автоматически обновляется при создании/завершении фич.",
        "",
        "---",
        "",
        "## Статистика",
        "",
        "| Метрика | Значение |",
        "|---------|----------|",
        f"| Всего фич | {len(features)} |",
        f"| Deployed | {len(deployed)} |",
        f"| In Progress | {len(in_progress)} |",
        f"| Archived | {len(archived)} |",
        "",
        "---",
        "",
    ]

    # Активные фичи
    if in_progress:
        lines.extend(
            [
                "## Активные фичи",
                "",
                "| FID | Название | Статус | Дата | Сервисы | Артефакты |",
                "|-----|----------|--------|------|---------|-----------|",
            ]
        )
        for f in sorted(in_progress, key=lambda x: x.fid):
            services = ", ".join(f.services) if f.services else "—"
            artifacts_links = ", ".join([f"[{t.upper()}]({p})" for t, p in f.artifacts.items()])
            lines.append(f"| {f.fid} | {f.title} | {f.status} | {f.created} | {services} | {artifacts_links} |")
        lines.extend(["", "---", ""])

    # Завершённые фичи
    lines.extend(
        [
            "## Завершённые фичи",
            "",
            "| FID | Название | Deployed | Сервисы | Артефакты |",
            "|-----|----------|----------|---------|-----------|",
        ]
    )
    if deployed:
        for f in sorted(deployed, key=lambda x: x.fid):
            services = ", ".join(f.services) if f.services else "—"
            artifacts_links = ", ".join([f"[{t.upper()}]({p})" for t, p in f.artifacts.items()])
            lines.append(f"| {f.fid} | {f.title} | {f.created} | {services} | {artifacts_links} |")
    else:
        lines.append("| — | — | — | — | — |")

    lines.extend(["", "---", ""])

    # Архивные фичи
    lines.extend(
        [
            "## Архивные фичи",
            "",
            "| FID | Название | Причина архивации | Дата |",
            "|-----|----------|-------------------|------|",
        ]
    )
    if archived:
        for f in sorted(archived, key=lambda x: x.fid):
            lines.append(f"| {f.fid} | {f.title} | — | {f.created} |")
    else:
        lines.append("| — | — | — | — |")

    lines.extend(
        [
            "",
            "---",
            "",
            "**Формат именования**: `{YYYY-MM-DD}_{FID}_{slug}-{type}.md`",
            "**Спецификация**: См. `.aidd/docs/artifact-naming.md`",
        ]
    )

    return "\n".join(lines)


def update_pipeline_state(state_path: Path, features: dict[str, Feature]) -> dict[str, Any]:
    """Обновить .pipeline-state.json с реестром фич."""
    if state_path.exists():
        state = json.loads(state_path.read_text())
    else:
        state = {"project_name": "", "mode": "CREATE", "current_stage": 1, "gates": {}}

    # Добавить реестр фич
    state["features_registry"] = {}
    for fid, feature in features.items():
        state["features_registry"][fid] = {
            "name": feature.name,
            "title": feature.title,
            "created": feature.created,
            "status": feature.status,
            "services": feature.services,
        }

    # Установить next_feature_id
    max_id = 0
    for fid in features:
        match = re.match(r"F(\d+)", fid)
        if match:
            max_id = max(max_id, int(match.group(1)))
    state["next_feature_id"] = max_id + 1

    return state


def scan_artifacts(docs_dir: Path) -> list[Artifact]:
    """Просканировать директорию и найти все артефакты."""
    artifacts = []

    for md_file in docs_dir.rglob("*.md"):
        # Пропустить служебные файлы
        if md_file.name in ["FEATURES.md", "README.md", "rtm.md", "template-map.md"]:
            continue

        # Пропустить уже мигрированные (с FID в имени)
        if re.match(r"\d{4}-\d{2}-\d{2}_F\d{3}_", md_file.name):
            print(f"  Пропуск (уже мигрирован): {md_file.name}")
            continue

        artifact_type = detect_artifact_type(md_file)
        if artifact_type is None:
            print(f"  Пропуск (неизвестный тип): {md_file}")
            continue

        slug = extract_slug_from_filename(md_file.name)
        created_date = get_file_creation_date(md_file)

        artifact = Artifact(
            path=md_file,
            type=artifact_type,
            slug=slug,
            created_date=created_date,
        )
        artifacts.append(artifact)

    return artifacts


def migrate(project_dir: Path, dry_run: bool = False) -> None:
    """Выполнить миграцию артефактов."""
    docs_dir = project_dir / "ai-docs" / "docs"

    if not docs_dir.exists():
        print(f"Директория {docs_dir} не найдена")
        return

    print(f"Сканирование артефактов в {docs_dir}...")
    artifacts = scan_artifacts(docs_dir)

    if not artifacts:
        print("Артефакты для миграции не найдены")
        return

    print(f"Найдено артефактов: {len(artifacts)}")

    # Группировка по фичам
    groups = group_artifacts_by_feature(artifacts)
    print(f"Обнаружено фич: {len(groups)}")

    # Создание фич с FID
    features: dict[str, Feature] = {}
    fid_counter = 1

    for slug, group_artifacts in sorted(groups.items()):
        fid = f"F{fid_counter:03d}"
        fid_counter += 1

        # Найти самую раннюю дату
        dates = [a.created_date for a in group_artifacts if a.created_date]
        created = min(dates) if dates else datetime.now().strftime("%Y-%m-%d")

        # Извлечь title из PRD если есть
        title = slug.replace("-", " ").title()
        for artifact in group_artifacts:
            if artifact.type == "prd":
                content = artifact.path.read_text()
                match = re.search(r"^#\s+PRD:\s*(.+)$", content, re.MULTILINE)
                if match:
                    title = match.group(1).strip()
                break

        feature = Feature(fid=fid, name=slug, title=title, created=created)

        # Обработать каждый артефакт в группе
        for artifact in group_artifacts:
            artifact.feature_group = fid
            date = artifact.created_date or created
            new_filename = f"{date}_{fid}_{slug}-{artifact.type}.md"
            artifact.new_filename = new_filename

            # Определить новый путь
            type_to_dir = {
                "prd": "prd",
                "research": "research",
                "plan": "architecture",
                "feature-plan": "plans",
                "review": "reports/review",
                "qa": "reports/qa",
                "validation": "reports/validation",
            }
            subdir = type_to_dir.get(artifact.type, "")
            new_path = docs_dir / subdir / new_filename
            feature.artifacts[artifact.type] = f"{subdir}/{new_filename}"

        features[fid] = feature

    # Вывод плана миграции
    print("\n" + "=" * 60)
    print("ПЛАН МИГРАЦИИ")
    print("=" * 60)

    for fid, feature in sorted(features.items()):
        print(f"\n{fid}: {feature.title}")
        for artifact in artifacts:
            if artifact.feature_group == fid:
                print(f"  {artifact.path.name}")
                print(f"    → {artifact.new_filename}")

    if dry_run:
        print("\n[DRY RUN] Файлы не изменены")
        return

    # Выполнение миграции
    print("\n" + "=" * 60)
    print("ВЫПОЛНЕНИЕ МИГРАЦИИ")
    print("=" * 60)

    for artifact in artifacts:
        feature = features[artifact.feature_group]

        # Читаем содержимое
        content = artifact.path.read_text()

        # Генерируем frontmatter
        frontmatter = generate_frontmatter(artifact, feature)

        # Добавляем frontmatter
        new_content = add_frontmatter_to_content(content, frontmatter)

        # Определяем новый путь
        type_to_dir = {
            "prd": "prd",
            "research": "research",
            "plan": "architecture",
            "feature-plan": "plans",
            "review": "reports/review",
            "qa": "reports/qa",
            "validation": "reports/validation",
        }
        subdir = type_to_dir.get(artifact.type, "")
        new_path = docs_dir / subdir / artifact.new_filename

        # Создаём директорию если нужно
        new_path.parent.mkdir(parents=True, exist_ok=True)

        # Записываем новый файл
        new_path.write_text(new_content)
        print(f"  Создан: {new_path.relative_to(project_dir)}")

        # Удаляем старый файл если путь изменился
        if artifact.path != new_path:
            artifact.path.unlink()
            print(f"  Удалён: {artifact.path.relative_to(project_dir)}")

    # Генерируем FEATURES.md
    features_content = generate_features_md(features)
    features_path = docs_dir / "FEATURES.md"
    features_path.write_text(features_content)
    print(f"\nСоздан: {features_path.relative_to(project_dir)}")

    # Обновляем .pipeline-state.json
    state_path = project_dir / ".pipeline-state.json"
    state = update_pipeline_state(state_path, features)
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    print(f"Обновлён: {state_path.relative_to(project_dir)}")

    print("\n" + "=" * 60)
    print("МИГРАЦИЯ ЗАВЕРШЕНА")
    print(f"Мигрировано фич: {len(features)}")
    print(f"Мигрировано артефактов: {len(artifacts)}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Миграция артефактов на новую систему именования с FID",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
    # Показать план миграции (без изменений)
    python scripts/migrate_artifacts.py --dry-run

    # Выполнить миграцию в текущей директории
    python scripts/migrate_artifacts.py

    # Выполнить миграцию в указанном проекте
    python scripts/migrate_artifacts.py --project-dir /path/to/project
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
