"""Tests for myproject."""

from __future__ import annotations

import re
from dataclasses import FrozenInstanceError

import pytest
from hypothesis import given
from hypothesis import strategies as st

from myproject import __version__
from myproject.config import Settings, get_settings
from myproject.main import main


class TestVersion:
    """Version string tests."""

    def test_version_exists(self) -> None:
        assert isinstance(__version__, str)

    def test_version_is_semver(self) -> None:
        assert re.match(r"^\d+\.\d+\.\d+", __version__)


class TestMain:
    """CLI entry point tests."""

    def test_main_returns_zero(self) -> None:
        assert main([]) == 0

    def test_version_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0
        assert __version__ in capsys.readouterr().out

    def test_verbose_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert main(["--verbose"]) == 0
        assert "myproject" in capsys.readouterr().out

    def test_invalid_flag(self) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main(["--unknown"])
        assert exc_info.value.code == 2


class TestConfig:
    """Configuration tests."""

    def test_settings_defaults(self) -> None:
        settings = Settings()
        assert settings.app_name == "myproject"
        assert settings.debug is False
        assert settings.log_level == "INFO"

    def test_settings_immutable(self) -> None:
        settings = Settings()
        with pytest.raises(FrozenInstanceError):
            settings.app_name = "changed"  # type: ignore[misc]

    def test_get_settings_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("APP_NAME", "testapp")
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("LOG_LEVEL", "debug")
        settings = get_settings()
        assert settings.app_name == "testapp"
        assert settings.debug is True
        assert settings.log_level == "DEBUG"

    def test_fixture_settings(self, settings: Settings) -> None:
        assert settings.app_name == "myproject-test"
        assert settings.debug is True
        assert settings.log_level == "DEBUG"

    def test_invalid_log_level(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOG_LEVEL", "INVALID")
        with pytest.raises(ValueError, match="Invalid LOG_LEVEL"):
            get_settings()

    @given(st.text())
    def test_settings_app_name_accepts_any_string(self, name: str) -> None:
        """Property-based test: Settings should accept any string as app_name."""
        settings = Settings(app_name=name)
        assert settings.app_name == name
