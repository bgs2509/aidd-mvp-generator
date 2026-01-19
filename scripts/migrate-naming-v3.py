#!/usr/bin/env python3
"""
Migration Script: Naming Convention v3

Migrates existing project to new naming conventions based on 5 core words:
analyst, researcher, planner, coder, validator

Changes:
- Artifacts: prd/ → _analysis/, architecture/ → _plans/mvp/, etc.
- Files: Remove duplication ({name}-prd.md → {name}.md)
- Gates: PRD_READY → ANALYSIS_READY, IMPLEMENT_OK → CODE_READY
- References: Update all internal links

Usage:
    python scripts/migrate-naming-v3.py --dry-run  # Show plan
    python scripts/migrate-naming-v3.py            # Execute migration
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Gate mappings (old → new)
GATE_MAPPINGS = {
    "PRD_READY": "ANALYSIS_READY",
    "RESEARCH_DONE": "RESEARCH_READY",
    "IMPLEMENT_OK": "CODE_READY",
    "REVIEW_OK": "REVIEW_READY",
    "QA_PASSED": "TESTING_READY",
    "ALL_GATES_PASSED": "VALIDATION_READY",
}

# Artifact folder mappings (old → new)
ARTIFACT_FOLDER_MAPPINGS = {
    "prd": "_analysis",
    "research": "_research",
    "architecture": "_plans/mvp",
    "plans": "_plans/features",
    "reports": "_validation",
}

# File name patterns to remove duplication
FILE_RENAME_PATTERNS = [
    (r"(.+)-prd\.md$", r"\1.md"),
    (r"(.+)-research\.md$", r"\1.md"),
    (r"(.+)-plan\.md$", r"\1.md"),
    (r"(.+)-completion\.md$", r"\1.md"),
]


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def print_step(step: int, total: int, text: str):
    """Print step marker"""
    print(f"\n[{step}/{total}] {text}")
    print("-" * 70)


def backup_file(file_path: Path) -> Path:
    """Create backup of file"""
    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
    if file_path.exists():
        import shutil
        shutil.copy2(file_path, backup_path)
        print(f"  ✓ Backup: {backup_path.relative_to(Path.cwd())}")
    return backup_path


def migrate_folders(docs_path: Path, dry_run: bool = False) -> List[Tuple[Path, Path]]:
    """
    Migrate artifact folders to new structure

    Returns list of (old_path, new_path) tuples
    """
    migrations = []

    for old_name, new_name in ARTIFACT_FOLDER_MAPPINGS.items():
        old_path = docs_path / old_name
        new_path = docs_path / new_name

        if not old_path.exists():
            print(f"  ⊘ Skip: {old_path.relative_to(Path.cwd())} (не существует)")
            continue

        if new_path.exists():
            print(f"  ⚠ Skip: {new_path.relative_to(Path.cwd())} (уже существует)")
            continue

        migrations.append((old_path, new_path))

        if dry_run:
            print(f"  → {old_path.relative_to(Path.cwd())}")
            print(f"     → {new_path.relative_to(Path.cwd())}")
        else:
            # Create parent directory if needed
            new_path.parent.mkdir(parents=True, exist_ok=True)
            old_path.rename(new_path)
            print(f"  ✓ {old_path.name} → {new_path.relative_to(docs_path)}")

    return migrations


def migrate_files(docs_path: Path, dry_run: bool = False) -> List[Tuple[Path, Path]]:
    """
    Remove duplication in file names

    Returns list of (old_path, new_path) tuples
    """
    migrations = []

    # Scan all markdown files in new folders
    for folder in ["_analysis", "_research", "_plans/mvp", "_plans/features", "_validation"]:
        folder_path = docs_path / folder
        if not folder_path.exists():
            continue

        for md_file in folder_path.rglob("*.md"):
            old_name = md_file.name
            new_name = old_name

            # Apply rename patterns
            for pattern, replacement in FILE_RENAME_PATTERNS:
                new_name = re.sub(pattern, replacement, new_name)

            if new_name != old_name and new_name != ".md":
                new_path = md_file.parent / new_name

                if new_path.exists():
                    print(f"  ⚠ Skip: {new_path.relative_to(Path.cwd())} (уже существует)")
                    continue

                migrations.append((md_file, new_path))

                if dry_run:
                    print(f"  → {md_file.relative_to(docs_path)}")
                    print(f"     → {new_path.relative_to(docs_path)}")
                else:
                    md_file.rename(new_path)
                    print(f"  ✓ {old_name} → {new_name}")

    return migrations


def migrate_pipeline_state(state_path: Path, dry_run: bool = False) -> bool:
    """
    Update .pipeline-state.json:
    - Add naming_version: "v3"
    - Keep old gate names (backward compatibility via gate_aliases)

    Returns True if changes were made
    """
    if not state_path.exists():
        print(f"  ⊘ Skip: {state_path} (не существует)")
        return False

    # Backup before modifying
    if not dry_run:
        backup_file(state_path)

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    changes = []

    # Add naming_version flag
    if "naming_version" not in state:
        state["naming_version"] = "v3"
        changes.append("naming_version: v3")

    # Ensure gate_aliases exist (backward compatibility)
    if "gate_aliases" not in state:
        state["gate_aliases"] = GATE_MAPPINGS
        changes.append("gate_aliases: added")

    if changes:
        if dry_run:
            print(f"  → Обновить {state_path.name}:")
            for change in changes:
                print(f"     + {change}")
        else:
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            print(f"  ✓ {state_path.name} обновлён:")
            for change in changes:
                print(f"     + {change}")
        return True
    else:
        print(f"  ⊘ Skip: {state_path.name} (уже актуален)")
        return False


def update_references(docs_path: Path, folder_migrations: List[Tuple[Path, Path]],
                      file_migrations: List[Tuple[Path, Path]], dry_run: bool = False) -> int:
    """
    Update internal links in all markdown files

    Returns number of files updated
    """
    # Build replacement map
    replacements = {}

    # Folder references
    for old_path, new_path in folder_migrations:
        old_rel = old_path.relative_to(docs_path)
        new_rel = new_path.relative_to(docs_path)
        replacements[str(old_rel)] = str(new_rel)

    # File references
    for old_path, new_path in file_migrations:
        old_rel = old_path.relative_to(docs_path)
        new_rel = new_path.relative_to(docs_path)
        replacements[str(old_rel)] = str(new_rel)

    if not replacements:
        print("  ⊘ Нет замен для выполнения")
        return 0

    updated_count = 0

    # Scan all markdown files
    for md_file in docs_path.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        original_content = content

        # Apply replacements
        for old_ref, new_ref in replacements.items():
            # Match markdown links: [text](path) or [text](path#anchor)
            content = re.sub(
                rf"\[([^\]]+)\]\({re.escape(str(old_ref))}([#)])",
                rf"[\1]({new_ref}\2",
                content
            )
            # Match plain paths
            content = content.replace(str(old_ref), str(new_ref))

        if content != original_content:
            if dry_run:
                print(f"  → Обновить ссылки в {md_file.relative_to(docs_path)}")
            else:
                md_file.write_text(content, encoding="utf-8")
                print(f"  ✓ {md_file.relative_to(docs_path)}")
            updated_count += 1

    return updated_count


def main():
    """Main migration flow"""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate project to naming v3")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show migration plan without making changes")
    args = parser.parse_args()

    # Paths
    project_root = Path.cwd()
    docs_path = project_root / "ai-docs" / "docs"
    state_path = project_root / ".pipeline-state.json"

    # Header
    print_header("NAMING CONVENTION MIGRATION: v2 → v3")

    if args.dry_run:
        print("🔍 DRY RUN MODE: Показываю план без изменений\n")
    else:
        print("⚠️  ВЫПОЛНЕНИЕ: Изменения будут применены\n")
        print("💾 Рекомендация: Создайте git commit перед миграцией")
        print("   git add -A && git commit -m 'chore: before naming v3 migration'\n")

        response = input("Продолжить? [y/N]: ")
        if response.lower() != 'y':
            print("\n❌ Отменено пользователем")
            return 1

    # Check prerequisites
    if not docs_path.exists():
        print(f"\n❌ Ошибка: {docs_path} не существует")
        print("   Эта команда должна запускаться из корня целевого проекта")
        return 1

    # Step 1: Migrate folders
    print_step(1, 4, "Миграция папок артефактов")
    folder_migrations = migrate_folders(docs_path, args.dry_run)

    # Step 2: Migrate files
    print_step(2, 4, "Переименование файлов (убрать дублирование)")
    file_migrations = migrate_files(docs_path, args.dry_run)

    # Step 3: Update pipeline state
    print_step(3, 4, "Обновление .pipeline-state.json")
    migrate_pipeline_state(state_path, args.dry_run)

    # Step 4: Update references
    print_step(4, 4, "Обновление ссылок в документах")
    updated_count = update_references(docs_path, folder_migrations, file_migrations, args.dry_run)

    # Summary
    print_header("ИТОГИ")
    print(f"  Папок перемещено:     {len(folder_migrations)}")
    print(f"  Файлов переименовано: {len(file_migrations)}")
    print(f"  Ссылок обновлено:     {updated_count}")

    if args.dry_run:
        print("\n✓ Dry run завершён. Запустите без --dry-run для применения.")
    else:
        print("\n✓ Миграция завершена успешно!")
        print("\n📋 Следующие шаги:")
        print("   1. Проверьте изменения: git status")
        print("   2. Создайте коммит: git commit -m 'feat: migrate to naming v3'")
        print("   3. Используйте новые команды: /aidd-analyze, /aidd-code, etc.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
