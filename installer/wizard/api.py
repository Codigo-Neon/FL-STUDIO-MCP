"""JsApi — methods exposed to JavaScript via pywebview's `api` parameter.

Each method:
- Has no required arguments (or only JSON-serializable scalars)
- Returns a JSON-serializable dict
- Catches expected exceptions and returns `{"ok": False, "error": "..."}` so
  the JS layer can render user-friendly messages without seeing tracebacks
"""
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from installer.setup_engine.detect import detect_environment
from installer.setup_engine.claude_config import (
    backup_config,
    find_config_path,
    register_mcp_server,
    ConfigCorruptedError,
)
from installer.setup_engine.fl_studio import install_device_script
from installer.setup_engine.loopmidi import (
    create_port,
    download_loopmidi,
    extract_loopmidi,
    install_loopmidi,
    LoopMidiNotInstalledError,
)
from installer.tray.state import AppState, default_state_path
from installer.tray.supervisor import Supervisor


def _ok() -> Dict[str, Any]:
    return {"ok": True, "error": None}


def _err(msg: str) -> Dict[str, Any]:
    return {"ok": False, "error": msg}


def _path_or_none(p: Optional[Path]) -> Optional[str]:
    return str(p) if p is not None else None


class JsApi:
    """Methods callable from JS as `pywebview.api.<method>(...)`."""

    def detect(self) -> Dict[str, Any]:
        """Run environment detection and return a JSON-friendly snapshot."""
        report = detect_environment()
        return {
            "claude_desktop": _path_or_none(report.claude_desktop_path),
            "fl_studio_settings": _path_or_none(report.fl_studio_settings_dir),
            "loopmidi": _path_or_none(report.loopmidi_path),
            "webview2": report.webview2_installed,
            "is_ready": report.is_ready(),
        }

    def install_loopmidi(self) -> Dict[str, Any]:
        """Download → extract → install loopMIDI silently. Reports any error."""
        try:
            tmp = Path(tempfile.gettempdir()) / "fl_mcp_loopmidi"
            tmp.mkdir(parents=True, exist_ok=True)
            zip_path = download_loopmidi(dest=tmp / "loopmidi.zip")
            installer_exe = extract_loopmidi(zip_path=zip_path, extract_dir=tmp / "extracted")
            install_loopmidi(installer=installer_exe)
            return _ok()
        except Exception as exc:
            return _err(str(exc))

    def create_port(self) -> Dict[str, Any]:
        """Create the FL_MCP loopMIDI virtual port. Idempotent."""
        try:
            report = detect_environment()
            if report.loopmidi_path is None:
                return _err("loopMIDI no detectado. Instalalo primero (paso 3).")
            create_port(loopmidi_exe=report.loopmidi_path, port_name="FL_MCP")
            return _ok()
        except (LoopMidiNotInstalledError, RuntimeError) as exc:
            return _err(str(exc))

    def install_script(self) -> Dict[str, Any]:
        """Copy the bundled `device_test.py` into FL Studio's Hardware folder.

        The bundled script lives at `<install-root>/device_test.py` (placed there
        by Inno Setup). We resolve it relative to this module's parent.
        """
        try:
            report = detect_environment()
            if report.fl_studio_settings_dir is None:
                return _err("FL Studio no detectado. Abrí FL Studio al menos una vez antes.")
            bundled = Path(__file__).resolve().parents[2] / "device_test.py"
            install_device_script(
                source_script=bundled,
                fl_studio_settings_dir=report.fl_studio_settings_dir,
                device_name="FL_MCP",
            )
            return _ok()
        except FileNotFoundError as exc:
            return _err(str(exc))

    def register_mcp(self, python_exe: str, trigger_py: str) -> Dict[str, Any]:
        """Register the FL MCP server in Claude Desktop's config (with .bak)."""
        try:
            config = find_config_path()
            backup_config(config)
            register_mcp_server(
                config_path=config,
                name="flstudio",
                command=python_exe,
                args=[trigger_py],
            )
            return _ok()
        except ConfigCorruptedError as exc:
            return _err(f"Tu config de Claude Desktop está corrupta: {exc}")

    def test_connection(self) -> Dict[str, Any]:
        """Send a MIDI ping to FL Studio. Returns ok if the port accepted it."""
        ok = Supervisor().test_midi()
        if ok:
            return _ok()
        return _err(
            "FL Studio no respondió. Lo más común: olvidaste 'Enable' en MIDI Settings. "
            "Volvé al paso 7."
        )

    def mark_setup_completed(self) -> Dict[str, Any]:
        """Persist that setup finished — next launch goes straight to the tray."""
        state_path = default_state_path()
        state = AppState.load(state_path)
        state.setup_completed = True
        state.save(state_path)
        return _ok()
