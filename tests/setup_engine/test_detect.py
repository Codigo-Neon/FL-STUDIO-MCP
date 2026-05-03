"""Tests for installer.setup_engine.detect."""
from pathlib import Path
import pytest

from installer.setup_engine.detect import (
    EnvironmentReport,
    detect_claude_desktop,
    detect_fl_studio,
    detect_loopmidi,
    detect_webview2,
    detect_environment,
)


class TestEnvironmentReport:
    def test_all_present_means_ready(self):
        report = EnvironmentReport(
            claude_desktop_path=Path("C:/Users/u/AppData/Local/Programs/Claude/Claude.exe"),
            fl_studio_settings_dir=Path("C:/Users/u/Documents/Image-Line/FL Studio/Settings"),
            loopmidi_path=Path("C:/Program Files/loopMIDI/loopMIDI.exe"),
            webview2_installed=True,
        )
        assert report.is_ready() is True

    def test_missing_claude_means_not_ready(self):
        report = EnvironmentReport(
            claude_desktop_path=None,
            fl_studio_settings_dir=Path("/somewhere"),
            loopmidi_path=Path("/somewhere"),
            webview2_installed=True,
        )
        assert report.is_ready() is False

    def test_missing_fl_studio_means_not_ready(self):
        report = EnvironmentReport(
            claude_desktop_path=Path("/somewhere"),
            fl_studio_settings_dir=None,
            loopmidi_path=Path("/somewhere"),
            webview2_installed=True,
        )
        assert report.is_ready() is False

    def test_missing_loopmidi_means_not_ready(self):
        report = EnvironmentReport(
            claude_desktop_path=Path("/somewhere"),
            fl_studio_settings_dir=Path("/somewhere"),
            loopmidi_path=None,
            webview2_installed=True,
        )
        assert report.is_ready() is False


class TestDetectClaudeDesktop:
    def test_returns_path_when_default_install_exists(self, fs):
        fake_path = Path("C:/Users/u/AppData/Local/Programs/Claude/Claude.exe")
        fs.create_file(str(fake_path))

        result = detect_claude_desktop(local_appdata=Path("C:/Users/u/AppData/Local"))

        assert result == fake_path

    def test_returns_none_when_not_installed(self, fs):
        result = detect_claude_desktop(local_appdata=Path("C:/Users/u/AppData/Local"))
        assert result is None


class TestDetectFlStudio:
    def test_returns_settings_dir_when_present(self, fs):
        fake_dir = Path("C:/Users/u/Documents/Image-Line/FL Studio/Settings")
        fs.create_dir(str(fake_dir))

        result = detect_fl_studio(documents=Path("C:/Users/u/Documents"))

        assert result == fake_dir

    def test_returns_none_when_settings_dir_missing(self, fs):
        result = detect_fl_studio(documents=Path("C:/Users/u/Documents"))
        assert result is None


class TestDetectLoopmidi:
    def test_finds_in_program_files(self, fs):
        fake_path = Path("C:/Program Files/loopMIDI/loopMIDI.exe")
        fs.create_file(str(fake_path))

        result = detect_loopmidi(program_files=Path("C:/Program Files"))

        assert result == fake_path

    def test_returns_none_when_missing(self, fs):
        result = detect_loopmidi(program_files=Path("C:/Program Files"))
        assert result is None


class TestDetectWebview2:
    def test_returns_true_when_runtime_dir_exists(self, fs):
        fake_dir = Path("C:/Program Files (x86)/Microsoft/EdgeWebView/Application")
        fs.create_dir(str(fake_dir))

        assert detect_webview2(program_files_x86=Path("C:/Program Files (x86)")) is True

    def test_returns_false_when_runtime_missing(self, fs):
        assert detect_webview2(program_files_x86=Path("C:/Program Files (x86)")) is False


class TestDetectEnvironment:
    def test_aggregates_all_detectors(self, fs):
        local_appdata = Path("C:/Users/u/AppData/Local")
        documents = Path("C:/Users/u/Documents")
        program_files = Path("C:/Program Files")
        program_files_x86 = Path("C:/Program Files (x86)")

        fs.create_file(str(local_appdata / "Programs/Claude/Claude.exe"))
        fs.create_dir(str(documents / "Image-Line/FL Studio/Settings"))
        fs.create_file(str(program_files / "loopMIDI/loopMIDI.exe"))
        fs.create_dir(str(program_files_x86 / "Microsoft/EdgeWebView/Application"))

        report = detect_environment(
            local_appdata=local_appdata,
            documents=documents,
            program_files=program_files,
            program_files_x86=program_files_x86,
        )

        assert report.is_ready() is True
        assert report.claude_desktop_path == local_appdata / "Programs/Claude/Claude.exe"
        assert report.fl_studio_settings_dir == documents / "Image-Line/FL Studio/Settings"
        assert report.loopmidi_path == program_files / "loopMIDI/loopMIDI.exe"
        assert report.webview2_installed is True
