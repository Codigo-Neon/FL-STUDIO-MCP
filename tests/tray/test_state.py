"""Tests for installer.tray.state."""
import json
from pathlib import Path
import pytest

from installer.tray.state import AppState, default_state_path


class TestDefaultStatePath:
    def test_uses_appdata_env_var(self, monkeypatch):
        monkeypatch.setenv("APPDATA", "C:/Users/u/AppData/Roaming")
        result = default_state_path()
        assert result == Path("C:/Users/u/AppData/Roaming/FL MCP Studio/state.json")


class TestAppStateLoad:
    def test_returns_default_when_file_missing(self, fs):
        state_path = Path("C:/Users/u/AppData/Roaming/FL MCP Studio/state.json")
        state = AppState.load(state_path)
        assert state.setup_completed is False
        assert state.last_known_version is None

    def test_loads_existing_state(self, fs):
        state_path = Path("C:/Users/u/AppData/Roaming/FL MCP Studio/state.json")
        fs.create_file(
            str(state_path),
            contents=json.dumps({"setup_completed": True, "last_known_version": "1.0.0"}),
        )

        state = AppState.load(state_path)

        assert state.setup_completed is True
        assert state.last_known_version == "1.0.0"

    def test_corrupted_json_returns_default(self, fs):
        state_path = Path("C:/Users/u/AppData/Roaming/FL MCP Studio/state.json")
        fs.create_file(str(state_path), contents="not json {")

        state = AppState.load(state_path)

        assert state.setup_completed is False


class TestAppStateSave:
    def test_creates_parent_dir(self, fs):
        state_path = Path("C:/Users/u/AppData/Roaming/FL MCP Studio/state.json")
        state = AppState(setup_completed=True, last_known_version="1.0.0")

        state.save(state_path)

        assert state_path.exists()
        data = json.loads(state_path.read_text())
        assert data == {"setup_completed": True, "last_known_version": "1.0.0"}

    def test_overwrites_existing_state(self, fs):
        state_path = Path("C:/Users/u/AppData/Roaming/FL MCP Studio/state.json")
        fs.create_file(str(state_path), contents='{"setup_completed": false, "last_known_version": null}')

        AppState(setup_completed=True, last_known_version="2.0.0").save(state_path)

        data = json.loads(state_path.read_text())
        assert data["setup_completed"] is True
        assert data["last_known_version"] == "2.0.0"
