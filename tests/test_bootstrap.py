"""Tests for the bootstrap script.

These tests are skipped automatically after bootstrap.py deletes itself
during project setup.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

_scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
_bootstrap_exists = (_scripts_dir / "bootstrap.py").exists()

if _bootstrap_exists:
    sys.path.insert(0, str(_scripts_dir))
    bootstrap = importlib.import_module("bootstrap")

pytestmark = pytest.mark.skipif(
    not _bootstrap_exists,
    reason="bootstrap.py was removed after project setup",
)


class TestToPascalCase:
    """PascalCase conversion tests."""

    def test_single_word(self) -> None:
        assert bootstrap.to_pascal_case("hello") == "Hello"

    def test_snake_case(self) -> None:
        assert bootstrap.to_pascal_case("my_app") == "MyApp"

    def test_multiple_underscores(self) -> None:
        assert bootstrap.to_pascal_case("my_cool_app") == "MyCoolApp"


class TestValidateName:
    """Project name validation tests."""

    def test_valid_name(self) -> None:
        assert bootstrap.validate_name("my_app") == "my_app"

    def test_rejects_hyphenated_name(self) -> None:
        with pytest.raises(SystemExit):
            bootstrap.validate_name("my-app")

    def test_rejects_myproject(self) -> None:
        with pytest.raises(SystemExit):
            bootstrap.validate_name("myproject")

    def test_rejects_invalid_identifier(self) -> None:
        with pytest.raises(SystemExit):
            bootstrap.validate_name("123invalid")


class TestShouldSkip:
    """Path skip logic tests."""

    def test_skips_git_dir(self) -> None:
        assert bootstrap.should_skip(Path(".git/config")) is True

    def test_skips_pycache(self) -> None:
        assert bootstrap.should_skip(Path("src/__pycache__/module.pyc")) is True

    def test_skips_bootstrap_file(self) -> None:
        assert bootstrap.should_skip(Path("scripts/bootstrap.py")) is True

    def test_allows_normal_file(self) -> None:
        assert bootstrap.should_skip(Path("src/myproject/main.py")) is False

    def test_skips_venv(self) -> None:
        assert bootstrap.should_skip(Path(".venv/lib/python3.12/site.py")) is True


class TestRenameInFile:
    """File content replacement tests."""

    def test_replaces_content(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello myproject world", encoding="utf-8")
        result = bootstrap.rename_in_file(f, [("myproject", "newapp")])
        assert result is True
        assert f.read_text(encoding="utf-8") == "hello newapp world"

    def test_no_change_returns_false(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("nothing to replace", encoding="utf-8")
        result = bootstrap.rename_in_file(f, [("myproject", "newapp")])
        assert result is False

    def test_skips_binary_file(self, tmp_path: Path) -> None:
        f = tmp_path / "test.bin"
        f.write_bytes(b"\x00\x01\x02\xff\xfe")
        result = bootstrap.rename_in_file(f, [("myproject", "newapp")])
        assert result is False


def _make_scaffold_tree(root: Path) -> None:
    """Create a minimal scaffold directory tree for cleanup tests."""
    (root / "pyproject.toml").write_text("[project]\nname = 'myproject'\n", encoding="utf-8")
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_bootstrap.py").write_text("# scaffold test\n", encoding="utf-8")
    commands = root / ".claude" / "commands"
    commands.mkdir(parents=True)
    (commands / "bootstrap.md").write_text("# bootstrap\n", encoding="utf-8")
    (root / "Makefile").write_text(
        ".PHONY: help install bootstrap new\n\n"
        "help:\n\techo help\n\n"
        "install:\n\tuv sync\n\n"
        "bootstrap: ## Rename project\n\tpython scripts/bootstrap.py\n\n"
        "new: ## Create new project\n\techo new\n",
        encoding="utf-8",
    )
    (root / "CLAUDE.md").write_text(
        "# myproject\n\n"
        "- `scripts/` — utility scripts (bootstrap.py is one-time setup, delete after use)\n"
        "- Other config\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "# myproject\n\n"
        "## Quick Start\n\nmake new PROJECT=my_app\n\n"
        "## Manual Setup\n\npython scripts/bootstrap.py\n\n"
        "## Usage\n\nuv run myproject\n",
        encoding="utf-8",
    )
    docs = root / "docs"
    docs.mkdir()
    (docs / "getting-started.md").write_text(
        "## Quick Start\n\n### One-Command Setup\n\nmake new PROJECT=my_app\n\n"
        "### Manual Setup\n\npython scripts/bootstrap.py\n\n"
        "---\n\n## Project Structure\n\n"
        "### `scripts/bootstrap.py` — One-Time Rename Tool\n\nSome text.\n\n"
        "### `.claude/` — Claude Code Configuration\n\nSome text.\n\n"
        "| `make bootstrap` | python scripts/bootstrap.py | one-time |\n"
        "| `make new` | clone + bootstrap | scaffold |\n"
        "| `/bootstrap` | Guides you | scaffold |\n",
        encoding="utf-8",
    )


class TestCleanupScaffold:
    """Tests for cleanup_scaffold — removes scaffold-specific files and references."""

    def test_deletes_test_bootstrap(self, tmp_path: Path) -> None:
        _make_scaffold_tree(tmp_path)
        bootstrap.cleanup_scaffold(tmp_path)
        assert not (tmp_path / "tests" / "test_bootstrap.py").exists()

    def test_deletes_bootstrap_command(self, tmp_path: Path) -> None:
        _make_scaffold_tree(tmp_path)
        bootstrap.cleanup_scaffold(tmp_path)
        assert not (tmp_path / ".claude" / "commands" / "bootstrap.md").exists()

    def test_removes_bootstrap_target_from_makefile(self, tmp_path: Path) -> None:
        _make_scaffold_tree(tmp_path)
        bootstrap.cleanup_scaffold(tmp_path)
        content = (tmp_path / "Makefile").read_text(encoding="utf-8")
        assert "bootstrap" not in content

    def test_removes_new_target_from_makefile(self, tmp_path: Path) -> None:
        _make_scaffold_tree(tmp_path)
        bootstrap.cleanup_scaffold(tmp_path)
        content = (tmp_path / "Makefile").read_text(encoding="utf-8")
        assert "new:" not in content

    def test_preserves_other_makefile_targets(self, tmp_path: Path) -> None:
        _make_scaffold_tree(tmp_path)
        bootstrap.cleanup_scaffold(tmp_path)
        content = (tmp_path / "Makefile").read_text(encoding="utf-8")
        assert "help" in content
        assert "install" in content

    def test_removes_bootstrap_from_claude_md(self, tmp_path: Path) -> None:
        _make_scaffold_tree(tmp_path)
        bootstrap.cleanup_scaffold(tmp_path)
        content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
        assert "bootstrap" not in content
        assert "Other config" in content  # non-bootstrap content preserved

    def test_replaces_readme_quick_start(self, tmp_path: Path) -> None:
        _make_scaffold_tree(tmp_path)
        bootstrap.cleanup_scaffold(tmp_path)
        content = (tmp_path / "README.md").read_text(encoding="utf-8")
        assert "make new" not in content
        assert "bootstrap" not in content
        assert "make dev" in content
        assert "make check" in content
        assert "## Usage" in content  # section after Quick Start preserved

    def test_cleans_getting_started(self, tmp_path: Path) -> None:
        _make_scaffold_tree(tmp_path)
        bootstrap.cleanup_scaffold(tmp_path)
        content = (tmp_path / "docs" / "getting-started.md").read_text(encoding="utf-8")
        assert "bootstrap" not in content
        assert "make new" not in content
        assert "## Project Structure" in content  # structure section preserved
        assert ".claude/" in content  # .claude section preserved

    def test_tolerates_missing_optional_files(self, tmp_path: Path) -> None:
        """cleanup_scaffold should not raise when scaffold files are already absent."""
        (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
        bootstrap.cleanup_scaffold(tmp_path)  # must not raise
