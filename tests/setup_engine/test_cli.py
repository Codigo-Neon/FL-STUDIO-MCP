"""Smoke tests for the setup_engine CLI."""
import sys
from unittest.mock import MagicMock
import pytest

from installer.setup_engine import cli


class TestCli:
    def test_help_lists_all_subcommands(self, capsys):
        with pytest.raises(SystemExit):
            cli.main(["--help"])
        out = capsys.readouterr().out
        assert "detect" in out
        assert "install-loopmidi" in out
        assert "create-port" in out
        assert "install-script" in out
        assert "register-mcp" in out

    def test_detect_subcommand_calls_detect_environment(self, monkeypatch, capsys):
        fake_report = MagicMock()
        fake_report.is_ready.return_value = True
        fake_report.claude_desktop_path = "C:/.../Claude.exe"
        fake_report.fl_studio_settings_dir = "C:/.../Settings"
        fake_report.loopmidi_path = "C:/.../loopMIDI.exe"
        fake_report.webview2_installed = True

        monkeypatch.setattr(
            "installer.setup_engine.cli.detect_environment",
            MagicMock(return_value=fake_report),
        )

        cli.main(["detect"])
        out = capsys.readouterr().out
        assert "Claude Desktop" in out
        assert "FL Studio" in out
        assert "loopMIDI" in out
        assert "WebView2" in out

    def test_create_port_subcommand_calls_create_port(self, monkeypatch):
        fake_create = MagicMock()
        monkeypatch.setattr(
            "installer.setup_engine.cli.create_port", fake_create
        )

        cli.main([
            "create-port",
            "--loopmidi-exe", "C:/Program Files/loopMIDI/loopMIDI.exe",
            "--port-name", "FL_MCP",
        ])

        fake_create.assert_called_once()
        kwargs = fake_create.call_args.kwargs
        assert str(kwargs["loopmidi_exe"]).endswith("loopMIDI.exe")
        assert kwargs["port_name"] == "FL_MCP"
