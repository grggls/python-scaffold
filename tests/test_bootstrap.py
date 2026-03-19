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


class TestScaffoldTemplate:
    """Verify the scaffold pyproject.toml template has the correct uv/pytest config.

    These are regression tests: if the template is accidentally reverted, they fail.
    """

    def _read_pyproject(self) -> str:
        root = Path(__file__).resolve().parent.parent
        return (root / "pyproject.toml").read_text(encoding="utf-8")

    def test_uses_dependency_groups(self) -> None:
        """Dev deps must be in [dependency-groups] so uv sync includes them by default."""
        assert "[dependency-groups]" in self._read_pyproject()

    def test_no_optional_dependencies_section(self) -> None:
        """[project.optional-dependencies] requires --extra dev; dependency-groups does not."""
        assert "[project.optional-dependencies]" not in self._read_pyproject()

    def test_pytest_has_pythonpath_src(self) -> None:
        """pytest must add src/ to sys.path so the package is importable in any venv."""
        assert 'pythonpath = ["src"]' in self._read_pyproject()


def _make_pyproject_toml(tmp_path: Path) -> Path:
    """Write a pyproject.toml that mirrors the scaffold template structure."""
    content = (
        "[project]\n"
        'name = "myproject"\n'
        "\n"
        "[project.scripts]\n"
        'myproject = "myproject.main:main"\n'
        "\n"
        "[dependency-groups]\n"
        'dev = ["pytest>=8.2", "ruff>=0.15"]\n'
        "\n"
        "[tool.ruff.lint.isort]\n"
        'known-first-party = ["myproject"]\n'
        "\n"
        "[tool.pytest.ini_options]\n"
        'testpaths = ["tests"]\n'
        'pythonpath = ["src"]\n'
        "\n"
        "[tool.coverage.run]\n"
        'source = ["src/myproject"]\n'
    )
    p = tmp_path / "pyproject.toml"
    p.write_text(content, encoding="utf-8")
    return p


class TestBootstrapHyphenatedProject:
    """Bootstrap produces a correct pyproject.toml when the project name has a hyphen.

    Hyphenated names (e.g. url-shortener) split into a Python package name
    (url_shortener) and a CLI command name (url-shortener). The fix ensures
    that dev tools are always available and pytest can import the package.
    """

    def _apply_replacements(self, p: Path, name: str, cli_name: str) -> None:
        replacements = [
            ("python-scaffold", cli_name),
            ("myproject", name),
        ]
        bootstrap.rename_in_file(p, replacements)
        # Apply the same cli_name fix-up that bootstrap.main() does
        if cli_name != name:
            content = p.read_text(encoding="utf-8")
            old_script = f'{name} = "{name}.main:main"'
            new_script = f'{cli_name} = "{name}.main:main"'
            if old_script in content:
                p.write_text(content.replace(old_script, new_script), encoding="utf-8")

    def test_package_name_uses_underscores(self, tmp_path: Path) -> None:
        p = _make_pyproject_toml(tmp_path)
        self._apply_replacements(p, "url_shortener", "url-shortener")
        assert 'name = "url_shortener"' in p.read_text(encoding="utf-8")

    def test_cli_script_entry_uses_hyphens(self, tmp_path: Path) -> None:
        """[project.scripts] key should use the hyphenated CLI name, not the package name."""
        p = _make_pyproject_toml(tmp_path)
        self._apply_replacements(p, "url_shortener", "url-shortener")
        content = p.read_text(encoding="utf-8")
        assert 'url-shortener = "url_shortener.main:main"' in content
        assert 'url_shortener = "url_shortener.main:main"' not in content

    def test_dependency_groups_section_preserved(self, tmp_path: Path) -> None:
        """[dependency-groups] header must survive the rename so uv sync works."""
        p = _make_pyproject_toml(tmp_path)
        self._apply_replacements(p, "url_shortener", "url-shortener")
        content = p.read_text(encoding="utf-8")
        assert "[dependency-groups]" in content
        assert "[project.optional-dependencies]" not in content

    def test_pytest_pythonpath_preserved(self, tmp_path: Path) -> None:
        """pythonpath = ["src"] must survive the rename so pytest finds the package."""
        p = _make_pyproject_toml(tmp_path)
        self._apply_replacements(p, "url_shortener", "url-shortener")
        assert 'pythonpath = ["src"]' in p.read_text(encoding="utf-8")

    def test_coverage_source_renamed(self, tmp_path: Path) -> None:
        """Coverage source path must be updated to the new package name."""
        p = _make_pyproject_toml(tmp_path)
        self._apply_replacements(p, "url_shortener", "url-shortener")
        content = p.read_text(encoding="utf-8")
        assert 'source = ["src/url_shortener"]' in content
        assert "myproject" not in content

    @pytest.mark.parametrize(
        "name,cli_name",
        [
            ("my_app", "my_app"),  # no hyphen — cli_name equals name
            ("url_shortener", "url-shortener"),  # hyphen — cli_name differs from name
            ("data_pipeline", "data-pipeline"),
        ],
    )
    def test_no_placeholder_left_after_rename(
        self, tmp_path: Path, name: str, cli_name: str
    ) -> None:
        """No 'myproject' placeholder should remain after bootstrap runs."""
        p = _make_pyproject_toml(tmp_path)
        self._apply_replacements(p, name, cli_name)
        assert "myproject" not in p.read_text(encoding="utf-8")
