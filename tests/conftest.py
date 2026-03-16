"""Shared test fixtures."""

from __future__ import annotations

import pytest

from myproject.config import Settings


@pytest.fixture
def settings() -> Settings:
    """Return a Settings instance with test defaults."""
    return Settings(
        app_name="myproject-test",
        debug=True,
        log_level="DEBUG",
    )
