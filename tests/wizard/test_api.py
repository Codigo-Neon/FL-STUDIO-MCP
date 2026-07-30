"""Tests for installer.wizard.api."""
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from installer.wizard.api import JsApi


class TestJsApiDetect:
    def test_returns_serializable_environment_report(self, monkeypatch):
        fake_report = MagicMock()
        fake_report.claude_desktop_path = Path("C:/Claude.exe")
        fake_report.fl_studio_settings_dir = Path("C:/FL/Settings")
        fake_report.loopmidi_path = Path("C:/loopMIDI/loopMIDI.exe")
        fake_report.webview2_installed = True
        fake_report.is_ready.return_value = True

        monkeypatch.setattr(
            "installer.wizard.api.detect_environment",
            MagicMock(return_value=fake_report),
        )

        result = JsApi().detect()

        assert result == {
            "claude_desktop": "C:/Claude.exe",
            "fl_studio_settings": "C:/FL/Settings",
            "loopmidi": "C:/loopMIDI/loopMIDI.exe",
            "webview2": True,
            "is_ready": True,
        }

    def test_renders_none_paths_as_null(self, monkeypatch):
        fake_report = MagicMock()
        fake_report.claude_desktop_path = None
        fake_report.fl_studio_settings_dir = None
        fake_report.loopmidi_path = None
        fake_report.webview2_installed = False
        fake_report.is_ready.return_value = False

        monkeypatch.setattr(
            "installer.wizard.api.detect_environment",
            MagicMock(return_value=fake_report),
        )

        result = JsApi().detect()

        assert result["claude_desktop"] is None
        assert result["fl_studio_settings"] is None
        assert result["loopmidi"] is None
        assert result["webview2"] is False
        assert result["is_ready"] is False


class TestJsApiInstallLoopmidi:
    def test_runs_full_pipeline(self, monkeypatch, tmp_path):
        fake_dl = MagicMock(return_value=tmp_path / "loopmidi.zip")
        fake_extract = MagicMock(return_value=tmp_path / "loopMIDISetup.exe")
        fake_install = MagicMock()
        monkeypatch.setattr("installer.wizard.api.download_loopmidi", fake_dl)
        monkeypatch.setattr("installer.wizard.api.extract_loopmidi", fake_extract)
        monkeypatch.setattr("installer.wizard.api.install_loopmidi", fake_install)

        result = JsApi().install_loopmidi()

        assert result == {"ok": True, "error": None}
        fake_dl.assert_called_once()
        fake_extract.assert_called_once()
        fake_install.assert_called_once()

    def test_returns_error_on_network_failure(self, monkeypatch):
        from urllib.error import URLError
        monkeypatch.setattr(
            "installer.wizard.api.download_loopmidi",
            MagicMock(side_effect=URLError("no internet")),
        )

        result = JsApi().install_loopmidi()

        assert result["ok"] is False
        assert "no internet" in result["error"]


class TestJsApiCreatePort:
    def test_returns_ok_when_port_created(self, monkeypatch):
        fake_report = MagicMock()
        fake_report.loopmidi_path = Path("C:/loopMIDI/loopMIDI.exe")
        monkeypatch.setattr(
            "installer.wizard.api.detect_environment",
            MagicMock(return_value=fake_report),
        )
        monkeypatch.setattr("installer.wizard.api.create_port", MagicMock())

        result = JsApi().create_port()

        assert result == {"ok": True, "error": None}

    def test_returns_error_when_loopmidi_not_detected(self, monkeypatch):
        fake_report = MagicMock()
        fake_report.loopmidi_path = None
        monkeypatch.setattr(
            "installer.wizard.api.detect_environment",
            MagicMock(return_value=fake_report),
        )

        result = JsApi().create_port()

        assert result["ok"] is False
        assert "loopMIDI" in result["error"]


class TestJsApiInstallScript:
    def test_calls_install_device_script_with_bundled_source(self, monkeypatch, tmp_path):
        fake_install = MagicMock()
        monkeypatch.setattr("installer.wizard.api.install_device_script", fake_install)
        monkeypatch.setattr("installer.wizard.api.install_bridge_package", MagicMock())
        monkeypatch.setattr(
            "installer.wizard.api.detect_environment",
            MagicMock(return_value=MagicMock(fl_studio_settings_dir=tmp_path)),
        )

        result = JsApi().install_script()

        assert result["ok"] is True
        fake_install.assert_called_once()
        kwargs = fake_install.call_args.kwargs
        assert kwargs["fl_studio_settings_dir"] == tmp_path
        assert kwargs["device_name"] == "FL_MCP"

    def test_also_installs_bridge_package_next_to_script(self, monkeypatch, tmp_path):
        """device_test.py does `from bridge import ...` at import time, so the
        wizard must copy bridge/ into the same Hardware dir as the script."""
        fake_script = MagicMock()
        fake_bridge = MagicMock()
        monkeypatch.setattr("installer.wizard.api.install_device_script", fake_script)
        monkeypatch.setattr("installer.wizard.api.install_bridge_package", fake_bridge)
        monkeypatch.setattr(
            "installer.wizard.api.detect_environment",
            MagicMock(return_value=MagicMock(fl_studio_settings_dir=tmp_path)),
        )

        result = JsApi().install_script()

        assert result["ok"] is True
        fake_bridge.assert_called_once()
        kwargs = fake_bridge.call_args.kwargs
        assert kwargs["fl_studio_settings_dir"] == tmp_path
        assert kwargs["device_name"] == "FL_MCP"
        # Same install root the script came from, so both land together.
        assert kwargs["source_root"] == fake_script.call_args.kwargs["source_script"].parent

    def test_reports_error_when_bridge_package_missing(self, monkeypatch, tmp_path):
        monkeypatch.setattr("installer.wizard.api.install_device_script", MagicMock())
        monkeypatch.setattr(
            "installer.wizard.api.install_bridge_package",
            MagicMock(side_effect=FileNotFoundError("bridge package not found at source: X")),
        )
        monkeypatch.setattr(
            "installer.wizard.api.detect_environment",
            MagicMock(return_value=MagicMock(fl_studio_settings_dir=tmp_path)),
        )

        result = JsApi().install_script()

        assert result["ok"] is False
        assert "bridge" in result["error"]

    def test_returns_error_when_fl_studio_not_detected(self, monkeypatch):
        monkeypatch.setattr(
            "installer.wizard.api.detect_environment",
            MagicMock(return_value=MagicMock(fl_studio_settings_dir=None)),
        )

        result = JsApi().install_script()

        assert result["ok"] is False
        assert "FL Studio" in result["error"]


class TestJsApiRegisterMcp:
    def test_backs_up_then_registers(self, monkeypatch):
        fake_backup = MagicMock()
        fake_register = MagicMock()
        monkeypatch.setattr("installer.wizard.api.backup_config", fake_backup)
        monkeypatch.setattr("installer.wizard.api.register_mcp_server", fake_register)
        monkeypatch.setattr(
            "installer.wizard.api.find_config_path",
            MagicMock(return_value=Path("C:/AppData/Roaming/Claude/cfg.json")),
        )

        result = JsApi().register_mcp(python_exe="C:/python.exe", trigger_py="C:/trigger.py")

        assert result["ok"] is True
        fake_backup.assert_called_once()
        fake_register.assert_called_once()
        assert fake_register.call_args.kwargs["command"] == "C:/python.exe"
        assert fake_register.call_args.kwargs["args"] == ["C:/trigger.py"]


class TestJsApiTestConnection:
    def test_delegates_to_supervisor(self, monkeypatch):
        fake_sup = MagicMock()
        fake_sup.test_midi.return_value = True
        monkeypatch.setattr(
            "installer.wizard.api.Supervisor",
            MagicMock(return_value=fake_sup),
        )

        result = JsApi().test_connection()

        assert result == {"ok": True, "error": None}

    def test_returns_friendly_error_when_port_missing(self, monkeypatch):
        fake_sup = MagicMock()
        fake_sup.test_midi.return_value = False
        monkeypatch.setattr(
            "installer.wizard.api.Supervisor",
            MagicMock(return_value=fake_sup),
        )

        result = JsApi().test_connection()

        assert result["ok"] is False
        assert "FL Studio" in result["error"] or "puerto" in result["error"]


class TestJsApiMarkSetupCompleted:
    def test_persists_state(self, monkeypatch, fs):
        from installer.tray.state import AppState
        state_path = Path("C:/Users/u/AppData/Roaming/FL MCP Studio/state.json")
        monkeypatch.setattr(
            "installer.wizard.api.default_state_path",
            MagicMock(return_value=state_path),
        )

        JsApi().mark_setup_completed()

        loaded = AppState.load(state_path)
        assert loaded.setup_completed is True
