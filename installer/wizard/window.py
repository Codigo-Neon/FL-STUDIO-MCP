"""WizardWindow — opens the pywebview window with the bundled HTML/JS/CSS.

The window owns one JsApi instance. When the user clicks "Cerrar e ir a la
bandeja" the JS calls pywebview.api.close_window() (registered as a method on
JsApi via a closure injected here), which calls window.destroy() to exit the
pywebview event loop.
"""
from pathlib import Path

import webview

from installer.wizard.api import JsApi


def launch_wizard(window_title: str = "FL MCP Studio — Configuración") -> None:
    """Open the wizard window. Blocks until the user closes it."""
    api = JsApi()

    ui_dir = Path(__file__).resolve().parent / "ui"
    index = ui_dir / "index.html"

    window = webview.create_window(
        title=window_title,
        url=str(index),
        js_api=api,
        width=720,
        height=540,
        resizable=False,
        background_color="#1e1e1e",
    )

    # Inject close_window so the JS finish handler can request a clean exit.
    def close_window() -> None:
        window.destroy()

    api.close_window = close_window  # type: ignore[attr-defined]

    webview.start(debug=False)
