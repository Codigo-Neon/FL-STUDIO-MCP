"""TrayApp — pystray icon + menu, polls Supervisor for status.

The tray app runs the pystray event loop on the main thread (required on most
platforms). A background thread polls `Supervisor.check_status()` every 5
seconds and updates the icon color when the state changes.
"""
import threading
from pathlib import Path
from typing import Optional

import pystray
from PIL import Image

from installer.tray.supervisor import ServerStatus, Supervisor

POLL_INTERVAL_SECONDS = 5
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def _load_icon(color: str) -> Image.Image:
    """Load the PNG icon for `color` ('green'|'yellow'|'red'|'gray')."""
    return Image.open(ASSETS_DIR / f"icon_{color}.png")


class TrayApp:
    """Lifecycle wrapper around pystray.Icon."""

    def __init__(self, supervisor: Optional[Supervisor] = None) -> None:
        self._supervisor = supervisor or Supervisor()
        self._icon: Optional[pystray.Icon] = None
        self._poll_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("Abrir panel completo", self._open_wizard),
            pystray.MenuItem("Probar conexión MIDI", self._test_midi),
            pystray.MenuItem("Reabrir wizard de setup", self._open_wizard),
            pystray.MenuItem("Ver logs en vivo", self._open_logs),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Buscar actualizaciones", self._check_updates),
            pystray.MenuItem("Acerca de", self._show_about),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Salir", self._quit),
        )

    def _poll_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                status = self._supervisor.check_status()
                if self._icon is not None:
                    self._icon.icon = _load_icon(status.color())
                    self._icon.title = self._format_title(status)
            except Exception:
                pass  # never let a polling error kill the tray
            self._stop_event.wait(POLL_INTERVAL_SECONDS)

    def _format_title(self, status: ServerStatus) -> str:
        running = "Corriendo" if status.is_running() else "Apagado"
        port = "OK" if status.midi_port_present else "MISSING"
        return f"FL MCP Studio — Server: {running} | MIDI: {port}"

    def _open_wizard(self, icon, item) -> None:
        # KNOWN LIMITATION: webview.start() requires the main thread on Windows
        # (mswebview2 backend uses STA COM init). Launching from this menu
        # callback runs on a pystray background thread, which on real Windows
        # will fail with RuntimeError or render nothing. Fixing requires
        # signaling the main thread to take over. Tracked for v2.
        # On first install the wizard is launched directly from main.py on the
        # main thread, so the happy path works.
        from installer.wizard.window import launch_wizard
        threading.Thread(target=launch_wizard, daemon=True).start()

    def _test_midi(self, icon, item) -> None:
        ok = self._supervisor.test_midi()
        icon.notify(
            "FL Studio recibió la nota ✅" if ok else "Sin respuesta. ¿Olvidaste 'Enable' en MIDI Settings?",
            "FL MCP Studio",
        )

    def _open_logs(self, icon, item) -> None:
        import os
        import subprocess
        log_dir = Path(os.environ.get("APPDATA", "")) / "FL MCP Studio" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(["explorer.exe", str(log_dir)])

    def _check_updates(self, icon, item) -> None:
        icon.notify("Chequeo de actualizaciones aún no implementado.", "FL MCP Studio")

    def _show_about(self, icon, item) -> None:
        icon.notify("FL MCP Studio v0.1 — control de FL Studio desde Claude.", "FL MCP Studio")

    def _quit(self, icon, item) -> None:
        self._stop_event.set()
        icon.stop()

    def run(self) -> None:
        """Start the tray. Blocks until the user clicks Salir."""
        self._icon = pystray.Icon(
            "fl_mcp_studio",
            icon=_load_icon("gray"),
            title="FL MCP Studio — iniciando…",
            menu=self._build_menu(),
        )
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()
        self._icon.run()
