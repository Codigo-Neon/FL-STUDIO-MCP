# Wizard GUI + Tray App Implementation Plan (Sub-project C)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the user-facing GUI of FL MCP Studio: a first-run wizard window (pywebview + HTML/CSS/JS) that walks the user through the 9-step install flow, plus a persistent tray app (pystray) that lives in the Windows notification area showing connection status and offering quick actions. Both wrap the Setup Engine (sub-project B) without duplicating its logic.

**Architecture:** Three Python packages. `installer/wizard/` hosts the pywebview window + a `JsApi` bridge class whose methods are callable from JS. `installer/tray/` hosts the pystray icon, menu, and a supervisor that monitors the MCP server process. `installer/main.py` is the single entry point — on first run it launches the wizard; after wizard completion it launches the tray. State is persisted in `%APPDATA%\FL MCP Studio\state.json` so subsequent launches know whether setup is done.

**Tech Stack:** Python 3.11+, `pywebview==5.3.2` (new dep), `pystray==0.19.5` (new dep), `Pillow==11.0.0` (pystray icon dep), HTML5/CSS3/vanilla JS for the wizard UI (no frontend frameworks — keeps the bundle small and the JS easy to debug), `psutil==6.1.0` (new dep, for process detection).

**Spec reference:** `docs/superpowers/specs/2026-05-03-windows-installer-design.md` sections 4 (wizard flow) + 5 (tray app) + 6 (auto-update).

**Test strategy:** Unit tests for the `JsApi` bridge (pure functions), the `Supervisor`, and the `State` manager. Manual visual QA for the wizard HTML (open in pywebview locally, capture screenshots) and for the tray icon (run pystray locally). End-to-end wizard execution requires Windows + loopMIDI + FL Studio; covered by `installer/QA_CHECKLIST.md`.

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `installer/wizard/__init__.py` | Create | Empty package marker |
| `installer/wizard/api.py` | Create | `JsApi` class — methods callable from JS that wrap setup_engine functions |
| `installer/wizard/window.py` | Create | `WizardWindow` — owns pywebview, opens HTML, exits to tray |
| `installer/wizard/ui/index.html` | Create | Wizard HTML structure: sidebar steps + main content area |
| `installer/wizard/ui/styles.css` | Create | Dark mode CSS, layout, status indicators |
| `installer/wizard/ui/wizard.js` | Create | Step state machine, sidebar updates, calls JsApi via `pywebview.api.*` |
| `installer/tray/__init__.py` | Create | Empty package marker |
| `installer/tray/supervisor.py` | Create | `Supervisor` — detects if MCP server is running, runs MIDI ping test |
| `installer/tray/state.py` | Create | `AppState` — load/save `%APPDATA%\FL MCP Studio\state.json` |
| `installer/tray/app.py` | Create | `TrayApp` — pystray icon, menu, integrates with Supervisor |
| `installer/main.py` | Create | Entry point: read state → launch wizard or tray |
| `installer/assets/icon_green.png` | Create (placeholder) | 64×64 green dot |
| `installer/assets/icon_yellow.png` | Create (placeholder) | 64×64 yellow dot |
| `installer/assets/icon_red.png` | Create (placeholder) | 64×64 red dot |
| `installer/assets/icon_gray.png` | Create (placeholder) | 64×64 gray dot |
| `installer/QA_CHECKLIST.md` | Create | Manual end-to-end QA steps for Windows |
| `tests/wizard/__init__.py` | Create | Empty package marker |
| `tests/wizard/test_api.py` | Create | Unit tests for JsApi |
| `tests/tray/__init__.py` | Create | Empty package marker |
| `tests/tray/test_state.py` | Create | Unit tests for AppState |
| `tests/tray/test_supervisor.py` | Create | Unit tests for Supervisor |
| `requirements.txt` | Modify | Add `pywebview==5.3.2`, `pystray==0.19.5`, `Pillow==11.0.0`, `psutil==6.1.0` |
| `CLAUDE.md` | Modify | Add Wizard + Tray section under "Sistema de Instalación (Windows)" |

---

## Task 1: Add deps + scaffold packages

**Files:**
- Modify: `requirements.txt`
- Create: `installer/wizard/__init__.py`
- Create: `installer/wizard/ui/.gitkeep`
- Create: `installer/tray/__init__.py`
- Create: `installer/assets/.gitkeep`
- Create: `tests/wizard/__init__.py`
- Create: `tests/tray/__init__.py`

- [ ] **Step 1: Add runtime dependencies**

Replace the contents of `requirements.txt` with:

```
mido==1.3.3
python-rtmidi==1.5.8
fl-studio-api-stubs==37.0.1
pywebview==5.3.2
pystray==0.19.5
Pillow==11.0.0
psutil==6.1.0
```

- [ ] **Step 2: Install the new deps**

```bash
cd "/home/roska/Documentos/FL MCP"
source .venv/bin/activate
pip install -r requirements.txt
```

Expected: 4 new packages installed (pywebview, pystray, Pillow, psutil).

- [ ] **Step 3: Create the package directories**

```bash
cd "/home/roska/Documentos/FL MCP"
mkdir -p installer/wizard/ui installer/tray installer/assets tests/wizard tests/tray
```

- [ ] **Step 4: Create empty `__init__.py` files (4 of them)**

Create as zero-byte files:
- `installer/wizard/__init__.py`
- `installer/tray/__init__.py`
- `tests/wizard/__init__.py`
- `tests/tray/__init__.py`

- [ ] **Step 5: Create `.gitkeep` markers for empty asset/UI dirs**

Create as zero-byte files:
- `installer/wizard/ui/.gitkeep`
- `installer/assets/.gitkeep`

- [ ] **Step 6: Verify pytest discovers the new test directories**

```bash
pytest --collect-only 2>&1 | tail -3
```

Expected: still says "62 tests collected". No errors about new dirs.

- [ ] **Step 7: Commit**

```bash
git add requirements.txt installer/wizard installer/tray installer/assets tests/wizard tests/tray
git commit -m "chore(wizard): scaffold wizard/tray packages + GUI deps"
```

---

## Task 2: `installer/tray/state.py` — Persistent app state

**Files:**
- Create: `installer/tray/state.py`
- Create: `tests/tray/test_state.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/tray/test_state.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/tray/test_state.py -v
```

Expected: ImportError on `installer.tray.state`.

- [ ] **Step 3: Implement `state.py`**

Create `installer/tray/state.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/tray/test_state.py -v
```

Expected: 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add installer/tray/state.py tests/tray/test_state.py
git commit -m "feat(tray): persistent AppState in %APPDATA%/FL MCP Studio/state.json"
```

---

## Task 3: `installer/tray/supervisor.py` — Process + MIDI status

**Files:**
- Create: `installer/tray/supervisor.py`
- Create: `tests/tray/test_supervisor.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/tray/test_supervisor.py`:

```python
"""Tests for installer.tray.supervisor."""
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from installer.tray.supervisor import (
    ServerStatus,
    Supervisor,
)


class TestServerStatus:
    def test_running_means_pid_present(self):
        status = ServerStatus(pid=4823, midi_port_present=True)
        assert status.is_running() is True

    def test_no_pid_means_not_running(self):
        status = ServerStatus(pid=None, midi_port_present=True)
        assert status.is_running() is False

    def test_color_green_when_all_ok(self):
        assert ServerStatus(pid=4823, midi_port_present=True).color() == "green"

    def test_color_yellow_when_running_but_midi_missing(self):
        assert ServerStatus(pid=4823, midi_port_present=False).color() == "yellow"

    def test_color_red_when_not_running(self):
        assert ServerStatus(pid=None, midi_port_present=False).color() == "red"


class TestSupervisorFindServerPid:
    def test_returns_pid_when_trigger_py_process_found(self, monkeypatch):
        fake_proc = MagicMock()
        fake_proc.info = {"pid": 4823, "name": "python.exe", "cmdline": ["python.exe", "trigger.py"]}
        monkeypatch.setattr(
            "installer.tray.supervisor.psutil.process_iter",
            MagicMock(return_value=[fake_proc]),
        )

        sup = Supervisor()
        assert sup.find_server_pid() == 4823

    def test_returns_none_when_no_trigger_py_running(self, monkeypatch):
        fake_proc = MagicMock()
        fake_proc.info = {"pid": 100, "name": "explorer.exe", "cmdline": ["explorer.exe"]}
        monkeypatch.setattr(
            "installer.tray.supervisor.psutil.process_iter",
            MagicMock(return_value=[fake_proc]),
        )

        sup = Supervisor()
        assert sup.find_server_pid() is None

    def test_handles_missing_cmdline_gracefully(self, monkeypatch):
        fake_proc = MagicMock()
        fake_proc.info = {"pid": 100, "name": "kernel", "cmdline": None}
        monkeypatch.setattr(
            "installer.tray.supervisor.psutil.process_iter",
            MagicMock(return_value=[fake_proc]),
        )

        sup = Supervisor()
        assert sup.find_server_pid() is None


class TestSupervisorCheckStatus:
    def test_combines_pid_and_port_check(self, monkeypatch, mock_rtmidi):
        fake_proc = MagicMock()
        fake_proc.info = {"pid": 4823, "name": "python.exe", "cmdline": ["python", "trigger.py"]}
        monkeypatch.setattr(
            "installer.tray.supervisor.psutil.process_iter",
            MagicMock(return_value=[fake_proc]),
        )
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = ["FL_MCP 0"]

        status = Supervisor().check_status()

        assert status.pid == 4823
        assert status.midi_port_present is True
        assert status.color() == "green"


class TestSupervisorTestMidi:
    def test_sends_c5_note_via_transport(self, monkeypatch, mock_rtmidi):
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = ["FL_MCP 0"]
        sent_messages = []
        mock_rtmidi.MidiOut.return_value.send_message.side_effect = lambda msg: sent_messages.append(msg)

        result = Supervisor().test_midi()

        assert result is True
        assert [0x90, 0x3C, 0x64] in sent_messages  # note on
        assert [0x80, 0x3C, 0x00] in sent_messages  # note off

    def test_returns_false_when_port_missing(self, mock_rtmidi):
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = []

        result = Supervisor().test_midi()

        assert result is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/tray/test_supervisor.py -v
```

Expected: ImportError on `installer.tray.supervisor`.

- [ ] **Step 3: Implement `supervisor.py`**

Create `installer/tray/supervisor.py`:

```python
"""Supervise the FL MCP server: check whether it's running + ping MIDI.

Claude Desktop launches the MCP server (`trigger.py`) over stdio when the user
opens Claude. The supervisor doesn't start or stop the server — it just observes
whether it's alive, so the tray can show an accurate status icon.

The MIDI port test uses python-rtmidi directly (not through the running server)
because loopMIDI ports are multi-writer-friendly: two processes can write to the
same virtual port without conflict.
"""
import time
from dataclasses import dataclass
from typing import Optional

import psutil


@dataclass
class ServerStatus:
    """Snapshot of the MCP server's observable state."""
    pid: Optional[int]
    midi_port_present: bool

    def is_running(self) -> bool:
        return self.pid is not None

    def color(self) -> str:
        """Tray icon color: green = OK, yellow = degraded, red = down."""
        if not self.is_running():
            return "red"
        if not self.midi_port_present:
            return "yellow"
        return "green"


class Supervisor:
    """Stateless inspector of the MCP server's runtime state."""

    SERVER_SCRIPT_NAME = "trigger.py"
    MIDI_PORT_NAME = "FL_MCP"

    def find_server_pid(self) -> Optional[int]:
        """Return the PID of any process whose cmdline contains `trigger.py`."""
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            cmdline = proc.info.get("cmdline") or []
            if any(self.SERVER_SCRIPT_NAME in arg for arg in cmdline):
                return proc.info["pid"]
        return None

    def check_status(self) -> ServerStatus:
        """Combine process detection + MIDI port presence into a single status."""
        return ServerStatus(
            pid=self.find_server_pid(),
            midi_port_present=self._port_present(),
        )

    def test_midi(self) -> bool:
        """Send a C5 note ON/OFF to the FL_MCP port. Return True if delivered.

        Returns False if the port is not visible (loopMIDI not running, FL Studio
        not configured, etc.).
        """
        if not self._port_present():
            return False
        import rtmidi
        out = rtmidi.MidiOut()
        for index, name in enumerate(out.get_ports()):
            if self.MIDI_PORT_NAME in name:
                out.open_port(index)
                out.send_message([0x90, 0x3C, 0x64])  # C5 note on, vel 100
                time.sleep(0.3)
                out.send_message([0x80, 0x3C, 0x00])  # C5 note off
                out.close_port()
                return True
        return False

    def _port_present(self) -> bool:
        import rtmidi
        out = rtmidi.MidiOut()
        return any(self.MIDI_PORT_NAME in name for name in out.get_ports())
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/tray/test_supervisor.py -v
```

Expected: 10 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add installer/tray/supervisor.py tests/tray/test_supervisor.py
git commit -m "feat(tray): Supervisor for MCP process + MIDI port status"
```

---

## Task 4: `installer/wizard/api.py` — JsApi bridge

**Files:**
- Create: `installer/wizard/api.py`
- Create: `tests/wizard/test_api.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/wizard/test_api.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/wizard/test_api.py -v
```

Expected: ImportError on `installer.wizard.api`.

- [ ] **Step 3: Implement `api.py`**

Create `installer/wizard/api.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/wizard/test_api.py -v
```

Expected: 13 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add installer/wizard/api.py tests/wizard/test_api.py
git commit -m "feat(wizard): JsApi bridge — JS-callable methods wrapping setup_engine"
```

---

## Task 5: HTML structure + base CSS

**Files:**
- Create: `installer/wizard/ui/index.html`
- Create: `installer/wizard/ui/styles.css`

- [ ] **Step 1: Create `index.html`**

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>FL MCP Studio — Configuración</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <h1 class="brand">FL MCP Studio</h1>
      <ol class="steps" id="steps">
        <li data-step="1" class="step current"><span class="dot"></span>Bienvenida</li>
        <li data-step="2" class="step"><span class="dot"></span>Diagnóstico</li>
        <li data-step="3" class="step"><span class="dot"></span>Instalar loopMIDI</li>
        <li data-step="4" class="step"><span class="dot"></span>Crear puerto MIDI</li>
        <li data-step="5" class="step"><span class="dot"></span>Instalar script</li>
        <li data-step="6" class="step"><span class="dot"></span>Registrar Claude</li>
        <li data-step="7" class="step"><span class="dot"></span>Configurar FL Studio</li>
        <li data-step="8" class="step"><span class="dot"></span>Probar conexión</li>
        <li data-step="9" class="step"><span class="dot"></span>Listo</li>
      </ol>
    </aside>

    <main class="content">
      <section class="step-panel" data-step="1">
        <h2>Bienvenida</h2>
        <p>Esto va a configurar Claude para que controle tu FL Studio. Tarda unos 3 minutos.</p>
        <p>Asegurate de tener <strong>FL Studio cerrado</strong> antes de empezar.</p>
        <div class="actions">
          <button class="primary" data-action="next">Comenzar</button>
        </div>
      </section>

      <section class="step-panel hidden" data-step="2">
        <h2>Diagnóstico del sistema</h2>
        <p>Chequeando qué está instalado…</p>
        <ul class="checklist" id="diag-list"></ul>
        <div class="actions">
          <button class="secondary" data-action="back">Atrás</button>
          <button class="primary" data-action="next" id="diag-next" disabled>Siguiente</button>
        </div>
      </section>

      <section class="step-panel hidden" data-step="3">
        <h2>Instalar loopMIDI</h2>
        <p>Vamos a descargar e instalar loopMIDI desde el sitio oficial.</p>
        <div class="status-box" id="lm-status">Esperando…</div>
        <div class="actions">
          <button class="secondary" data-action="back">Atrás</button>
          <button class="primary" data-action="install-loopmidi">Instalar</button>
          <button class="secondary" data-action="next" id="lm-next" disabled>Siguiente</button>
        </div>
      </section>

      <section class="step-panel hidden" data-step="4">
        <h2>Crear puerto MIDI virtual</h2>
        <p>Creando un puerto llamado <code>FL_MCP</code> que FL Studio va a usar para recibir MIDI.</p>
        <div class="status-box" id="port-status">Esperando…</div>
        <div class="actions">
          <button class="secondary" data-action="back">Atrás</button>
          <button class="primary" data-action="create-port">Crear puerto</button>
          <button class="secondary" data-action="next" id="port-next" disabled>Siguiente</button>
        </div>
      </section>

      <section class="step-panel hidden" data-step="5">
        <h2>Instalar script en FL Studio</h2>
        <p>Copiando <code>device_test.py</code> a la carpeta <code>Hardware</code> de FL Studio.</p>
        <div class="status-box" id="script-status">Esperando…</div>
        <div class="actions">
          <button class="secondary" data-action="back">Atrás</button>
          <button class="primary" data-action="install-script">Instalar script</button>
          <button class="secondary" data-action="next" id="script-next" disabled>Siguiente</button>
        </div>
      </section>

      <section class="step-panel hidden" data-step="6">
        <h2>Registrar en Claude Desktop</h2>
        <p>Editando <code>claude_desktop_config.json</code> (con backup automático).</p>
        <div class="status-box" id="mcp-status">Esperando…</div>
        <div class="actions">
          <button class="secondary" data-action="back">Atrás</button>
          <button class="primary" data-action="register-mcp">Registrar</button>
          <button class="secondary" data-action="next" id="mcp-next" disabled>Siguiente</button>
        </div>
      </section>

      <section class="step-panel hidden" data-step="7">
        <h2>Activar el script en FL Studio</h2>
        <p>Este paso lo tenés que hacer vos en FL Studio. Seguí estas instrucciones:</p>
        <ol class="manual-steps">
          <li>Abrí FL Studio</li>
          <li>Menú <strong>Options → MIDI Settings</strong></li>
          <li>En la lista de <em>Input</em>, encontrá <code>FL_MCP</code></li>
          <li>Hacé click en <strong>Enable</strong> y elegí <code>FL_MCP</code> en <em>Controller type</em></li>
          <li>Click en <strong>Refresh</strong> y cerrá la ventana de Settings</li>
        </ol>
        <div class="actions">
          <button class="secondary" data-action="back">Atrás</button>
          <button class="primary" data-action="next">Ya lo hice, continuar</button>
        </div>
      </section>

      <section class="step-panel hidden" data-step="8">
        <h2>Probar la conexión</h2>
        <p>Vamos a mandar una nota MIDI a FL Studio. Si todo está bien, vas a verla aparecer.</p>
        <div class="status-box" id="test-status">Click "Probar" cuando estés listo.</div>
        <div class="actions">
          <button class="secondary" data-action="back">Atrás</button>
          <button class="primary" data-action="test-connection">Probar</button>
          <button class="secondary" data-action="next" id="test-next" disabled>Siguiente</button>
        </div>
      </section>

      <section class="step-panel hidden" data-step="9">
        <h2>¡Listo!</h2>
        <p>Tu FL MCP Studio está configurado.</p>
        <p>De ahora en adelante vas a ver el ícono <span class="icon-pill green"></span> en la bandeja del sistema. Desde ahí podés ver el estado, reabrir este wizard o probar la conexión.</p>
        <div class="actions">
          <button class="primary" data-action="finish">Cerrar e ir a la bandeja</button>
        </div>
      </section>
    </main>
  </div>
  <script src="wizard.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create `styles.css`**

```css
/* FL MCP Studio — Wizard styles. Dark mode, VS Code / Linear inspired. */

:root {
  --bg: #1e1e1e;
  --bg-panel: #252526;
  --bg-elev: #2d2d30;
  --text: #d4d4d4;
  --text-muted: #858585;
  --accent: #0e639c;
  --accent-hover: #1177bb;
  --ok: #16825d;
  --warn: #cc6633;
  --error: #b03a3a;
  --border: #3c3c3c;
  --radius: 6px;
  font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
  font-size: 14px;
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
  height: 100vh;
  background: var(--bg);
  color: var(--text);
  overflow: hidden;
}

.app {
  display: grid;
  grid-template-columns: 220px 1fr;
  height: 100vh;
}

.sidebar {
  background: var(--bg-panel);
  border-right: 1px solid var(--border);
  padding: 24px 16px;
  overflow-y: auto;
}

.brand {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 24px 0;
  color: var(--text);
}

.steps {
  list-style: none;
  margin: 0;
  padding: 0;
}

.step {
  display: flex;
  align-items: center;
  padding: 8px 4px;
  font-size: 13px;
  color: var(--text-muted);
  position: relative;
}

.step .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--bg-elev);
  border: 1px solid var(--border);
  margin-right: 10px;
  flex-shrink: 0;
}

.step.current { color: var(--text); font-weight: 500; }
.step.current .dot { background: var(--accent); border-color: var(--accent); }
.step.done .dot { background: var(--ok); border-color: var(--ok); }
.step.error .dot { background: var(--error); border-color: var(--error); }

.content {
  padding: 32px 40px;
  overflow-y: auto;
}

.step-panel { display: block; }
.step-panel.hidden { display: none; }

.step-panel h2 {
  font-size: 22px;
  font-weight: 600;
  margin: 0 0 16px 0;
}

.step-panel p {
  line-height: 1.6;
  margin: 0 0 12px 0;
}

code {
  background: var(--bg-elev);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: "Consolas", "Menlo", monospace;
  font-size: 12.5px;
}

.actions {
  margin-top: 24px;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

button {
  padding: 8px 18px;
  border: none;
  border-radius: var(--radius);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 120ms ease;
}

button.primary {
  background: var(--accent);
  color: white;
}
button.primary:hover { background: var(--accent-hover); }
button.primary:disabled { background: var(--bg-elev); color: var(--text-muted); cursor: not-allowed; }

button.secondary {
  background: var(--bg-elev);
  color: var(--text);
  border: 1px solid var(--border);
}
button.secondary:hover { background: var(--border); }
button.secondary:disabled { opacity: 0.5; cursor: not-allowed; }

.checklist {
  list-style: none;
  padding: 0;
  margin: 16px 0;
}

.checklist li {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  margin-bottom: 6px;
}

.checklist li::before {
  content: "";
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  margin-right: 12px;
  background: var(--bg-elev);
  border: 1px solid var(--border);
  flex-shrink: 0;
}

.checklist li.ok::before { background: var(--ok); border-color: var(--ok); }
.checklist li.missing::before { background: var(--error); border-color: var(--error); }

.status-box {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  margin: 16px 0;
  min-height: 48px;
  font-family: "Consolas", monospace;
  font-size: 12.5px;
  white-space: pre-wrap;
}

.status-box.ok { border-color: var(--ok); }
.status-box.error { border-color: var(--error); color: #ff9b9b; }

.manual-steps {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 16px 16px 36px;
  margin: 16px 0;
  line-height: 1.9;
}

.icon-pill {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  vertical-align: middle;
  margin: 0 4px;
}
.icon-pill.green { background: var(--ok); }
```

- [ ] **Step 3: Verify HTML/CSS load standalone (basic syntax check)**

```bash
python -c "from pathlib import Path; html = Path('installer/wizard/ui/index.html').read_text(); assert html.startswith('<!DOCTYPE html>'); print('HTML OK,', len(html), 'bytes')"
```

Expected: `HTML OK, NNNN bytes`.

- [ ] **Step 4: Commit**

```bash
git add installer/wizard/ui/index.html installer/wizard/ui/styles.css
git commit -m "feat(wizard): HTML structure + dark-mode CSS for the wizard window"
```

---

## Task 6: `wizard.js` — Step state machine + API calls

**Files:**
- Create: `installer/wizard/ui/wizard.js`

- [ ] **Step 1: Create `wizard.js`**

Note on DOM safety: this file uses `replaceChildren()` and `textContent` only — never `innerHTML`. All dynamic content comes from `pywebview.api.*` Python responses (which we control), but we still avoid `innerHTML` as defense in depth.

```javascript
/* FL MCP Studio — Wizard JS. Drives step navigation and calls Python via pywebview.api. */

(function () {
  "use strict";

  const TOTAL_STEPS = 9;
  let currentStep = 1;

  // ----- DOM helpers -----

  function showStep(n) {
    document.querySelectorAll(".step-panel").forEach((el) => {
      el.classList.toggle("hidden", Number(el.dataset.step) !== n);
    });
    document.querySelectorAll(".sidebar .step").forEach((el) => {
      const step = Number(el.dataset.step);
      el.classList.toggle("current", step === n);
    });
    currentStep = n;
  }

  function markStepDone(n) {
    const li = document.querySelector(`.sidebar .step[data-step="${n}"]`);
    if (li) li.classList.add("done");
  }

  function markStepError(n) {
    const li = document.querySelector(`.sidebar .step[data-step="${n}"]`);
    if (li) li.classList.add("error");
  }

  function setStatus(boxId, message, kind) {
    const box = document.getElementById(boxId);
    if (!box) return;
    box.textContent = message;
    box.classList.remove("ok", "error");
    if (kind) box.classList.add(kind);
  }

  function enableNext(buttonId) {
    const btn = document.getElementById(buttonId);
    if (btn) btn.disabled = false;
  }

  function makeChecklistItem(label, value) {
    const li = document.createElement("li");
    li.classList.add(value ? "ok" : "missing");
    li.textContent = `${label}: ${value || "no detectado"}`;
    return li;
  }

  // ----- Action handlers -----

  async function runDetect() {
    const list = document.getElementById("diag-list");
    list.replaceChildren();
    const placeholder = document.createElement("li");
    placeholder.textContent = "Chequeando…";
    list.appendChild(placeholder);

    const r = await pywebview.api.detect();

    list.replaceChildren(
      makeChecklistItem("Claude Desktop", r.claude_desktop),
      makeChecklistItem("FL Studio", r.fl_studio_settings),
      makeChecklistItem("loopMIDI", r.loopmidi),
      makeChecklistItem("WebView2 Runtime", r.webview2 ? "instalado" : null),
    );
    enableNext("diag-next");
    if (r.is_ready) markStepDone(2);
  }

  async function runInstallLoopmidi() {
    setStatus("lm-status", "Descargando e instalando loopMIDI… (puede tardar un minuto)", null);
    const r = await pywebview.api.install_loopmidi();
    if (r.ok) {
      setStatus("lm-status", "✅ loopMIDI instalado", "ok");
      enableNext("lm-next");
      markStepDone(3);
    } else {
      setStatus("lm-status", `❌ Error: ${r.error}`, "error");
      markStepError(3);
    }
  }

  async function runCreatePort() {
    setStatus("port-status", "Creando puerto FL_MCP…", null);
    const r = await pywebview.api.create_port();
    if (r.ok) {
      setStatus("port-status", "✅ Puerto FL_MCP listo", "ok");
      enableNext("port-next");
      markStepDone(4);
    } else {
      setStatus("port-status", `❌ Error: ${r.error}`, "error");
      markStepError(4);
    }
  }

  async function runInstallScript() {
    setStatus("script-status", "Copiando device_test.py…", null);
    const r = await pywebview.api.install_script();
    if (r.ok) {
      setStatus("script-status", "✅ Script instalado en FL Studio", "ok");
      enableNext("script-next");
      markStepDone(5);
    } else {
      setStatus("script-status", `❌ Error: ${r.error}`, "error");
      markStepError(5);
    }
  }

  async function runRegisterMcp() {
    setStatus("mcp-status", "Editando claude_desktop_config.json…", null);
    // The wizard knows where it was installed; pass those paths to Python.
    // Defaults assume the install dir layout from sub-project D's Inno Setup script.
    const pythonExe = "C:/Program Files/FL MCP Studio/python-embed/python.exe";
    const triggerPy = "C:/Program Files/FL MCP Studio/trigger.py";
    const r = await pywebview.api.register_mcp(pythonExe, triggerPy);
    if (r.ok) {
      setStatus("mcp-status", "✅ Claude Desktop configurado", "ok");
      enableNext("mcp-next");
      markStepDone(6);
    } else {
      setStatus("mcp-status", `❌ Error: ${r.error}`, "error");
      markStepError(6);
    }
  }

  async function runTestConnection() {
    setStatus("test-status", "Mandando nota MIDI a FL Studio…", null);
    const r = await pywebview.api.test_connection();
    if (r.ok) {
      setStatus("test-status", "✅ FL Studio recibió la nota. Todo listo.", "ok");
      enableNext("test-next");
      markStepDone(8);
    } else {
      setStatus("test-status", `❌ ${r.error}`, "error");
      markStepError(8);
    }
  }

  async function runFinish() {
    await pywebview.api.mark_setup_completed();
    if (window.pywebview && pywebview.api.close_window) {
      pywebview.api.close_window();
    } else {
      window.close();
    }
  }

  // ----- Wire up -----

  function onActionClick(event) {
    const action = event.target.dataset.action;
    if (!action) return;

    switch (action) {
      case "next":
        if (currentStep === 1) {
          showStep(2);
          markStepDone(1);
          runDetect();
        } else if (currentStep === 7) {
          showStep(8);
          markStepDone(7);
        } else if (currentStep === 9) {
          // no-op; finish button handles 9
        } else {
          showStep(currentStep + 1);
        }
        break;
      case "back":
        if (currentStep > 1) showStep(currentStep - 1);
        break;
      case "install-loopmidi":
        runInstallLoopmidi();
        break;
      case "create-port":
        runCreatePort();
        break;
      case "install-script":
        runInstallScript();
        break;
      case "register-mcp":
        runRegisterMcp();
        break;
      case "test-connection":
        runTestConnection();
        break;
      case "finish":
        runFinish();
        break;
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.body.addEventListener("click", onActionClick);
  });
})();
```

- [ ] **Step 2: Sanity check (file parses, no innerHTML)**

```bash
python -c "
content = open('installer/wizard/ui/wizard.js').read()
assert 'innerHTML' not in content, 'innerHTML found — use replaceChildren/textContent'
assert 'replaceChildren' in content
print('JS OK,', len(content), 'bytes')
"
```

Expected: `JS OK, NNNN bytes`.

- [ ] **Step 3: Commit**

```bash
git add installer/wizard/ui/wizard.js
git commit -m "feat(wizard): step state machine + API calls in vanilla JS"
```

---

## Task 7: `installer/wizard/window.py` — Pywebview lifecycle

**Files:**
- Create: `installer/wizard/window.py`

- [ ] **Step 1: Implement `window.py`**

Create `installer/wizard/window.py`:

```python
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
```

- [ ] **Step 2: Verify the module imports cleanly**

```bash
python -c "from installer.wizard.window import launch_wizard; print('OK')"
```

Expected: `OK`. Note: do NOT call `launch_wizard()` from this verification — it would open a real window and block. The import alone is enough.

- [ ] **Step 3: Commit**

```bash
git add installer/wizard/window.py
git commit -m "feat(wizard): pywebview window lifecycle + JsApi binding"
```

---

## Task 8: `installer/tray/app.py` — Tray icon + menu

**Files:**
- Create: `installer/tray/app.py`

- [ ] **Step 1: Implement `app.py`**

Create `installer/tray/app.py`:

```python
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
        # Lazy import to avoid pulling pywebview into every tray-only run
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
```

- [ ] **Step 2: Verify the module imports cleanly**

```bash
python -c "from installer.tray.app import TrayApp; print('OK')"
```

Expected: `OK`. The icon files don't exist yet — we create them in Task 9 — so don't call `TrayApp().run()` here.

- [ ] **Step 3: Commit**

```bash
git add installer/tray/app.py
git commit -m "feat(tray): pystray icon + menu with status polling"
```

---

## Task 9: Icon assets + entry point

**Files:**
- Create: `installer/assets/icon_green.png`
- Create: `installer/assets/icon_yellow.png`
- Create: `installer/assets/icon_red.png`
- Create: `installer/assets/icon_gray.png`
- Create: `installer/main.py`
- Delete: `installer/assets/.gitkeep` (no longer needed)

- [ ] **Step 1: Generate placeholder icons via a one-off Python script**

```bash
cd "/home/roska/Documentos/FL MCP"
source .venv/bin/activate
python <<'PY'
from PIL import Image, ImageDraw
from pathlib import Path

ASSETS = Path("installer/assets")
ASSETS.mkdir(parents=True, exist_ok=True)

colors = {
    "green": (22, 130, 93),
    "yellow": (204, 153, 51),
    "red": (176, 58, 58),
    "gray": (90, 90, 90),
}

for name, rgb in colors.items():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((8, 8, 56, 56), fill=rgb + (255,))
    img.save(ASSETS / f"icon_{name}.png")
    print(f"Created {name}")
PY
```

Expected output:
```
Created green
Created yellow
Created red
Created gray
```

- [ ] **Step 2: Verify icons exist + are valid PNGs**

```bash
file installer/assets/icon_*.png
```

Expected: each line ends with `PNG image data, 64 x 64`.

- [ ] **Step 3: Remove the .gitkeep marker (no longer needed)**

```bash
rm -f installer/assets/.gitkeep
```

- [ ] **Step 4: Implement `installer/main.py`**

Create `installer/main.py`:

```python
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
```

- [ ] **Step 5: Verify the entry point imports cleanly**

```bash
python -c "from installer.main import main; print('OK')"
```

Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add installer/assets/icon_green.png installer/assets/icon_yellow.png installer/assets/icon_red.png installer/assets/icon_gray.png installer/main.py
git rm -f installer/assets/.gitkeep 2>/dev/null || true
git commit -m "feat(installer): icon assets + main.py entry point routing"
```

---

## Task 10: Manual QA checklist + CLAUDE.md update

**Files:**
- Create: `installer/QA_CHECKLIST.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Create `installer/QA_CHECKLIST.md`**

```markdown
# FL MCP Studio — QA Checklist

Manual end-to-end tests that require a real Windows 10/11 machine with FL Studio
21+ and Claude Desktop installed. These cannot be automated because they
exercise loopMIDI installation, FL Studio MIDI integration, and Claude Desktop's
config file mutation against real apps.

## Pre-flight

- [ ] Windows 10 22H2 or Windows 11
- [ ] FL Studio 21+ installed AND opened at least once (creates Settings dir)
- [ ] Claude Desktop installed
- [ ] No prior `FL_MCP` loopMIDI port (test fresh-install flow)

## First run

- [ ] Run `python -m installer.main`
- [ ] Wizard window opens (720×540, dark theme)
- [ ] Step 1 "Bienvenida" shown by default
- [ ] Sidebar shows all 9 steps with the first marked current
- [ ] Click "Comenzar" → moves to step 2

## Step 2 — Diagnóstico

- [ ] Auto-runs detection
- [ ] Each item shows ✅ or ❌ correctly
- [ ] Missing items show "no detectado"
- [ ] "Siguiente" enabled after detection

## Step 3 — Instalar loopMIDI

- [ ] Click "Instalar"
- [ ] Status box shows progress
- [ ] Network failure (disable Wi-Fi briefly) shows readable error
- [ ] Success → green border + checkmark + Siguiente enabled
- [ ] Verify loopMIDI now in Program Files

## Step 4 — Crear puerto MIDI

- [ ] Click "Crear puerto"
- [ ] Verify port `FL_MCP` appears in loopMIDI's window
- [ ] Re-run is no-op (port already exists, returns OK)

## Step 5 — Instalar script

- [ ] Click "Instalar script"
- [ ] Verify `device_test.py` exists at `%USERPROFILE%\Documents\Image-Line\FL Studio\Settings\Hardware\FL_MCP\`
- [ ] Verify `device_FL_MCP.nfo` companion exists

## Step 6 — Registrar Claude

- [ ] Click "Registrar"
- [ ] Verify `%APPDATA%\Claude\claude_desktop_config.json` has `flstudio` entry under `mcpServers`
- [ ] Verify `claude_desktop_config.json.bak` was created
- [ ] If a corrupted config exists, error message is friendly (not a stack trace)

## Step 7 — Manual FL Studio activation

- [ ] Open FL Studio → Options → MIDI Settings
- [ ] Find `FL_MCP` in Input list, Enable, set Controller type to `FL_MCP`
- [ ] Click Refresh, close Settings
- [ ] Return to wizard, click "Ya lo hice, continuar"

## Step 8 — Probar conexión

- [ ] Click "Probar"
- [ ] FL Studio should briefly show MIDI activity (either piano roll lights up or sounds play)
- [ ] Wizard shows ✅
- [ ] If FL Studio doesn't respond, error suggests revisiting step 7

## Step 9 — Listo

- [ ] Click "Cerrar e ir a la bandeja"
- [ ] Wizard window closes
- [ ] Tray icon appears in notification area (green)

## Tray app

- [ ] Right-click → menu shows all entries
- [ ] "Probar conexión MIDI" → toast notification with result
- [ ] "Reabrir wizard de setup" → wizard window reopens
- [ ] "Ver logs en vivo" → opens `%APPDATA%\FL MCP Studio\logs\` in Explorer
- [ ] Icon color changes when MCP server starts/stops in Claude Desktop

## Re-launch

- [ ] Close tray (Salir), re-run `python -m installer.main`
- [ ] Skips wizard (setup_completed=True), goes straight to tray

## Re-run wizard

- [ ] From tray menu → "Reabrir wizard de setup"
- [ ] Wizard opens at step 1
- [ ] Step 4 (create-port) reports "ya existía, OK"
- [ ] Step 6 (register-mcp) preserves any other MCP servers in the config

## Negative tests

- [ ] Run with FL Studio closed during step 8 → error explains the situation
- [ ] Manually corrupt `claude_desktop_config.json` then re-run step 6 → wizard offers backup-restore flow
```

- [ ] **Step 2: Update `CLAUDE.md`**

Use the Edit tool. Find the existing "## Sistema de Instalación (Windows)" section and replace it with:

```markdown
## Sistema de Instalación (Windows)

`installer/` empaqueta el setup automático del MCP en Windows en 3 sub-paquetes:

### `installer/setup_engine/` — Lógica pura

| Módulo | Responsabilidad |
|---|---|
| `detect.py` | Devuelve `EnvironmentReport` con qué hay instalado (Claude Desktop, FL Studio, loopMIDI, WebView2) |
| `claude_config.py` | Edita `claude_desktop_config.json` con backup `.bak`. Tira `ConfigCorruptedError` si el JSON está roto |
| `fl_studio.py` | Copia `device_test.py` a `Documents/Image-Line/FL Studio/Settings/Hardware/FL_MCP/` + crea `.nfo` companion |
| `loopmidi.py` | Descarga loopMIDI del sitio oficial, descomprime ZIP, instalación silenciosa, crea/detecta puerto virtual `FL_MCP` |
| `cli.py` | Wrapper argparse: `python -m installer.setup_engine.cli <subcommand>` para QA manual |

### `installer/wizard/` — GUI primera vez

| Archivo | Responsabilidad |
|---|---|
| `api.py` | `JsApi` — métodos callable desde JS via `pywebview.api.*`. Wraps cada función del setup_engine y la traduce a `{ok, error}` |
| `window.py` | `launch_wizard()` — abre la ventana pywebview, inyecta JsApi, bloquea hasta cierre |
| `ui/index.html` | 9 pasos como `<section>` apilados, ocultos via clase `.hidden` |
| `ui/styles.css` | Dark mode estilo VS Code, sidebar 220px + main 32px padding |
| `ui/wizard.js` | Vanilla JS — state machine de pasos, llama a `pywebview.api.*`. Usa `replaceChildren()`/`textContent` solamente (no `innerHTML`) |

### `installer/tray/` — App persistente

| Archivo | Responsabilidad |
|---|---|
| `state.py` | `AppState` — persiste `setup_completed` en `%APPDATA%\FL MCP Studio\state.json` |
| `supervisor.py` | `Supervisor.check_status()` — detecta proceso del MCP server + verifica puerto MIDI |
| `app.py` | `TrayApp` — pystray + menú + thread polling cada 5s |

### `installer/main.py` — Entry point

Lee `state.json` → si setup no completo lanza wizard; después (siempre) lanza tray.

Tests: `pytest tests/wizard tests/tray tests/setup_engine` (Linux con pyfakefs + mocks de subprocess/urllib/rtmidi/psutil). QA end-to-end manual via `installer/QA_CHECKLIST.md` en VM Windows.
```

- [ ] **Step 3: Run the full test suite to confirm nothing regressed**

```bash
pytest
```

Expected: 62 (Plan A + B) + 6 (state) + 10 (supervisor) + 13 (api) = **91 tests PASS**.

- [ ] **Step 4: Commit**

```bash
git add installer/QA_CHECKLIST.md CLAUDE.md
git commit -m "docs(installer): manual QA checklist + update CLAUDE.md with wizard/tray"
```

---

## Done — what you should have at the end

- 3 new packages: `installer/wizard/`, `installer/tray/`, `installer/assets/`
- 1 entry point: `installer/main.py`
- 4 PNG icons (placeholder dots — sub-project D can replace with branded versions)
- 91 unit tests total (62 from A+B + 29 new)
- HTML wizard renderable in pywebview
- Tray app runnable on Windows
- Manual QA checklist
- 10 atomic commits

## Verification checklist before declaring done

- [ ] `pytest` reports 91 PASS, 0 FAIL
- [ ] `python -c "from installer.main import main; print('OK')"` succeeds
- [ ] `python -c "from installer.wizard.window import launch_wizard; print('OK')"` succeeds
- [ ] `python -c "from installer.tray.app import TrayApp; print('OK')"` succeeds
- [ ] `installer/assets/` has 4 PNGs of size 64×64
- [ ] `installer/QA_CHECKLIST.md` has all 9 wizard steps + tray sections + negative tests
- [ ] `git log --oneline | head -10` shows 10 commits with conventional-commit format

## Out of scope (sub-project D will handle)

- Inno Setup `.iss` script that bundles Python embedded + this code into a single `.exe` installer
- GitHub Actions release pipeline
- Code signing
- Branded icon designs (placeholders are fine for v1)
- Auto-update implementation (the menu item exists but is a stub)
- Logging configuration (rotating file handler) — falls under polish

These pieces will package the working GUI + tray we deliver here.
