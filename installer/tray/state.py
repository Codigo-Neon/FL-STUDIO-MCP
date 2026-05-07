"""Persistent app state stored in %APPDATA%\\FL MCP Studio\\state.json.

Used by the entry point to decide whether to show the wizard (first run) or
go straight to the tray (returning user). Also tracks the last seen version
for the auto-update notification.
"""
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


def default_state_path() -> Path:
    """Return the default location of state.json under %APPDATA%."""
    appdata = Path(os.environ.get("APPDATA", ""))
    return appdata / "FL MCP Studio" / "state.json"


@dataclass
class AppState:
    """Persistable app state. Add fields here as new features need them."""
    setup_completed: bool = False
    last_known_version: Optional[str] = None

    @classmethod
    def load(cls, state_path: Path) -> "AppState":
        """Read state.json. If missing or corrupt, return defaults silently —
        the user shouldn't see startup errors over a recoverable state file.
        """
        if not state_path.exists():
            return cls()
        try:
            data = json.loads(state_path.read_text())
        except json.JSONDecodeError:
            return cls()
        return cls(
            setup_completed=data.get("setup_completed", False),
            last_known_version=data.get("last_known_version"),
        )

    def save(self, state_path: Path) -> None:
        """Persist to disk, creating parent dirs as needed."""
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(asdict(self), indent=2))
