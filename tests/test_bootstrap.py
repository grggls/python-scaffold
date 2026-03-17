"""Tests for the bootstrap script."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add scripts/ to path so we can import bootstrap
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from bootstrap import rename_in_file, should_skip, to_pascal_case, validate_name


class TestToPascalCase:
    """PascalCase conversion tests."""

    def test_single_word(self) -> None:
        assert to_pascal_case("hello") == "Hello"

    def test_snake_case(self) -> None:
        assert to_pascal_case("my_app") == "MyApp"

    def test_multiple_underscores(self) -> None:
        assert to_pascal_case("my_cool_app") == "MyCoolApp"


class TestValidateName:
    """Project name validation tests."""

    def test_valid_name(self) -> None:
        assert validate_name("my_app") == "my_app"

    def test_rejects_hyphenated_name(self) -> None:
        with pytest.raises(SystemExit):
            validate_name("my-app")

    def test_rejects_myproject(self) -> None:
        with pytest.raises(SystemExit):
            validate_name("myproject")

    def test_rejects_invalid_identifier(self) -> None:
        with pytest.raises(SystemExit):
            validate_name("123invalid")


class TestShouldSkip:
    """Path skip logic tests."""

    def test_skips_git_dir(self) -> None:
        assert should_skip(Path(".git/config")) is True

    def test_skips_pycache(self) -> None:
        assert should_skip(Path("src/__pycache__/module.pyc")) is True

    def test_skips_bootstrap_file(self) -> None:
        assert should_skip(Path("scripts/bootstrap.py")) is True

    def test_allows_normal_file(self) -> None:
        assert should_skip(Path("src/myproject/main.py")) is False

    def test_skips_venv(self) -> None:
        assert should_skip(Path(".venv/lib/python3.12/site.py")) is True


class TestRenameInFile:
    """File content replacement tests."""

    def test_replaces_content(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello myproject world", encoding="utf-8")
        result = rename_in_file(f, [("myproject", "newapp")])
        assert result is True
        assert f.read_text(encoding="utf-8") == "hello newapp world"

    def test_no_change_returns_false(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("nothing to replace", encoding="utf-8")
        result = rename_in_file(f, [("myproject", "newapp")])
        assert result is False

    def test_skips_binary_file(self, tmp_path: Path) -> None:
        f = tmp_path / "test.bin"
        f.write_bytes(b"\x00\x01\x02\xff\xfe")
        result = rename_in_file(f, [("myproject", "newapp")])
        assert result is False
