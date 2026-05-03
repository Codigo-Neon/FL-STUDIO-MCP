"""Detect which dependencies of FL MCP Studio are installed on the host.

All paths are passed as parameters with sensible defaults pulled from environment
variables — this lets the test suite (and Linux dev runs) override them via
pyfakefs without monkeypatching environment variables globally.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class EnvironmentReport:
    """Snapshot of which Windows dependencies are present on the host."""
    claude_desktop_path: Optional[Path]
    fl_studio_settings_dir: Optional[Path]
    loopmidi_path: Optional[Path]
    webview2_installed: bool

    def is_ready(self) -> bool:
        """True iff every required component was detected."""
        return (
            self.claude_desktop_path is not None
            and self.fl_studio_settings_dir is not None
            and self.loopmidi_path is not None
            and self.webview2_installed
        )


def _default_local_appdata() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", ""))


def _default_documents() -> Path:
    return Path(os.environ.get("USERPROFILE", "")) / "Documents"


def _default_program_files() -> Path:
    return Path(os.environ.get("ProgramFiles", "C:/Program Files"))


def _default_program_files_x86() -> Path:
    return Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)"))


def detect_claude_desktop(local_appdata: Optional[Path] = None) -> Optional[Path]:
    """Return the path to Claude.exe if installed in the default per-user location."""
    base = local_appdata if local_appdata is not None else _default_local_appdata()
    candidate = base / "Programs" / "Claude" / "Claude.exe"
    return candidate if candidate.exists() else None


def detect_fl_studio(documents: Optional[Path] = None) -> Optional[Path]:
    """Return the FL Studio Settings directory if it exists.

    FL Studio creates this directory on first launch. Its presence is a reliable
    indicator that FL Studio is installed AND has been opened at least once
    (which we need, because we will write Hardware/ scripts into it).
    """
    base = documents if documents is not None else _default_documents()
    candidate = base / "Image-Line" / "FL Studio" / "Settings"
    return candidate if candidate.is_dir() else None


def detect_loopmidi(program_files: Optional[Path] = None) -> Optional[Path]:
    """Return the path to loopMIDI.exe if installed in the default location."""
    base = program_files if program_files is not None else _default_program_files()
    candidate = base / "loopMIDI" / "loopMIDI.exe"
    return candidate if candidate.exists() else None


def detect_webview2(program_files_x86: Optional[Path] = None) -> bool:
    """True if Microsoft Edge WebView2 Runtime is installed (preinstalled on Win10/11)."""
    base = program_files_x86 if program_files_x86 is not None else _default_program_files_x86()
    return (base / "Microsoft" / "EdgeWebView" / "Application").is_dir()


def detect_environment(
    local_appdata: Optional[Path] = None,
    documents: Optional[Path] = None,
    program_files: Optional[Path] = None,
    program_files_x86: Optional[Path] = None,
) -> EnvironmentReport:
    """Run all detectors and assemble the report."""
    return EnvironmentReport(
        claude_desktop_path=detect_claude_desktop(local_appdata),
        fl_studio_settings_dir=detect_fl_studio(documents),
        loopmidi_path=detect_loopmidi(program_files),
        webview2_installed=detect_webview2(program_files_x86),
    )
