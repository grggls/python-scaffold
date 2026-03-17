#!/usr/bin/env python3
"""Bootstrap script to rename the scaffold project.

Replaces all occurrences of 'myproject' with a user-chosen name across
all files and directories. Run once after cloning the scaffold.

Usage:
    python scripts/bootstrap.py <project_name>

Example:
    python scripts/bootstrap.py my_awesome_app
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".mypy_cache", ".ruff_cache"}
SKIP_FILES = {"bootstrap.py"}

REPLACEMENTS = [
    ("myproject", None),  # snake_case — replacement computed from input
    ("MyProject", None),  # PascalCase
    ("MYPROJECT", None),  # UPPER_CASE
]


def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(word.capitalize() for word in name.split("_"))


def is_text_file(path: Path) -> bool:
    """Check if a file is a text file by attempting UTF-8 decode."""
    try:
        path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return False
    return True


def validate_name(name: str) -> str:
    """Validate that the project name is a valid Python identifier."""
    if not name.isidentifier():
        print(f"Error: '{name}' is not a valid Python identifier.")
        if "-" in name:
            suggestion = name.replace("-", "_")
            print(f"Hint: Try '{suggestion}' (use underscores, not hyphens).")
        sys.exit(1)

    if name == "myproject":
        print("Error: Project name cannot be 'myproject' (that's the placeholder).")
        sys.exit(1)

    return name


def find_project_root() -> Path:
    """Find the project root by looking for pyproject.toml."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent

    print("Error: Could not find pyproject.toml. Run from within the project.")
    sys.exit(1)


def should_skip(path: Path) -> bool:
    """Check if a path should be skipped."""
    parts = path.parts
    for skip_dir in SKIP_DIRS:
        if skip_dir in parts:
            return True
    if path.name in SKIP_FILES:
        return True
    return False


def rename_in_file(path: Path, replacements: list[tuple[str, str]]) -> bool:
    """Replace text in a file. Returns True if changes were made."""
    if not is_text_file(path):
        return False

    content = path.read_text(encoding="utf-8")
    original = content

    for old, new in replacements:
        content = content.replace(old, new)

    if content != original:
        path.write_text(content, encoding="utf-8")
        return True
    return False


def main() -> int:
    """Run the bootstrap process."""
    parser = argparse.ArgumentParser(
        description="Rename the scaffold project to your chosen name.",
        epilog="Example: python scripts/bootstrap.py my_awesome_app",
    )
    parser.add_argument(
        "name",
        nargs="?",
        help="New project name (must be a valid Python identifier, e.g., my_app)",
    )
    args = parser.parse_args()

    if args.name is None:
        name = input("Enter project name (snake_case, e.g., my_app): ").strip()
    else:
        name = args.name

    name = validate_name(name)
    pascal_name = to_pascal_case(name)
    upper_name = name.upper()

    author_name = input("Author name [Gregory Damiani]: ").strip() or "Gregory Damiani"
    author_email = (
        input("Author email [gregory.damiani@gmail.com]: ").strip() or "gregory.damiani@gmail.com"
    )
    github_username = input("GitHub username [grggls]: ").strip() or "grggls"

    replacements: list[tuple[str, str]] = [
        ("myproject", name),
        ("MyProject", pascal_name),
        ("MYPROJECT", upper_name),
        ("Gregory Damiani", author_name),
        ("gregory.damiani@gmail.com", author_email),
        ("grggls", github_username),
    ]

    root = find_project_root()
    print(f"\nRenaming project: myproject -> {name}")
    print(f"  PascalCase: MyProject -> {pascal_name}")
    print(f"  UPPER_CASE: MYPROJECT -> {upper_name}")
    print(f"  Author:     {author_name} <{author_email}>")
    print(f"  GitHub:     grggls -> {github_username}")
    print(f"  Root: {root}\n")

    # Rename directory first
    src_dir = root / "src" / "myproject"
    new_src_dir = root / "src" / name
    dirs_renamed: list[str] = []

    if src_dir.exists():
        shutil.move(str(src_dir), str(new_src_dir))
        dirs_renamed.append(f"  src/myproject/ -> src/{name}/")
        print(f"Renamed directory: src/myproject/ -> src/{name}/")

    # Replace in all text files
    files_modified: list[str] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if should_skip(path):
            continue

        relative = path.relative_to(root)
        if rename_in_file(path, replacements):
            files_modified.append(f"  {relative}")

    # Fix CLI command name in pyproject.toml if a separate CLI name was provided
    # (e.g., make new PROJECT=my-app sets SCAFFOLD_CLI_NAME=my-app while name=my_app)
    cli_name = os.environ.get("SCAFFOLD_CLI_NAME", "")
    if cli_name and cli_name != name:
        pyproject = root / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text(encoding="utf-8")
            # Replace the script entry key to use the hyphenated CLI name
            old_script = f'{name} = "{name}.main:main"'
            new_script = f'{cli_name} = "{name}.main:main"'
            if old_script in content:
                content = content.replace(old_script, new_script)
                pyproject.write_text(content, encoding="utf-8")
                print(f"CLI command: {cli_name} (from SCAFFOLD_CLI_NAME)")

    # Summary
    print(f"\nDirectories renamed: {len(dirs_renamed)}")
    for d in dirs_renamed:
        print(d)

    print(f"\nFiles modified: {len(files_modified)}")
    for f in files_modified:
        print(f)

    # Offer to self-delete
    print()
    response = input("Remove bootstrap script? [Y/n] ").strip().lower()
    if response in ("", "y", "yes"):
        script_path = Path(__file__).resolve()
        script_dir = script_path.parent

        script_path.unlink()
        print(f"Deleted: {script_path.relative_to(root)}")

        # Remove scripts/ if empty
        remaining = list(script_dir.iterdir())
        if not remaining:
            script_dir.rmdir()
            print(f"Deleted empty directory: {script_dir.relative_to(root)}/")

    print(
        "\nNext steps:\n"
        "  1. git init\n"
        "  2. make dev\n"
        "  3. make check\n"
        '  4. git add . && git commit -m "Initial commit"\n'
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
