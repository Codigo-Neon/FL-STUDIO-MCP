"""FL MCP Studio entry point.

On first run (state.json says setup not completed): launch the wizard.
When the wizard finishes: it sets setup_completed=True and the next launch goes
straight to the tray.

The tray can re-open the wizard via its menu.
"""
import sys

from installer.tray.state import AppState, default_state_path


def main() -> int:
    state = AppState.load(default_state_path())

    if not state.setup_completed:
        from installer.wizard.window import launch_wizard
        launch_wizard()
        # After wizard returns, fall through to tray (the user just finished setup).

    from installer.tray.app import TrayApp
    TrayApp().run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
