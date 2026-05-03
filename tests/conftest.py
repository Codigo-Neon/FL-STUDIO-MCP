"""Shared pytest fixtures for the FL MCP test suite."""
import sys
from unittest.mock import MagicMock
import pytest


@pytest.fixture
def mock_rtmidi(monkeypatch):
    """Inject a fake `rtmidi` module so tests can run on platforms where rtmidi
    is not installed or where we want to control its behavior."""
    fake_rtmidi = MagicMock()
    monkeypatch.setitem(sys.modules, "rtmidi", fake_rtmidi)
    return fake_rtmidi


@pytest.fixture
def force_platform(monkeypatch):
    """Return a callable that overrides sys.platform for the duration of a test."""
    def _set(value: str) -> None:
        monkeypatch.setattr(sys, "platform", value)
    return _set
