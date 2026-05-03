# Setup Engine Implementation Plan (Sub-project B)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the pure-Python Setup Engine that the Windows installer's GUI wizard (sub-project C) will call to detect dependencies, install loopMIDI, create the FL_MCP virtual MIDI port, copy `device_test.py` into FL Studio's Hardware folder, and register the MCP server in Claude Desktop's config — all with safe rollback (backups + idempotent operations) and full unit-test coverage that runs from Linux.

**Architecture:** Five focused modules under a new `installer/setup_engine/` package, each with a single responsibility (detection, loopMIDI, FL Studio script, Claude config, CLI orchestration). Functions accept paths as parameters with environment-variable defaults — this makes everything trivially testable from Linux while real Windows runs use the env-var defaults. No GUI logic; the GUI (sub-project C) imports these and renders the UX.

**Tech Stack:** Python 3.11+, `pyfakefs` for filesystem mocking in tests (new dev dep), `unittest.mock` for subprocess/HTTP mocking, stdlib `urllib.request` for the loopMIDI download (avoids new runtime deps), `argparse` for the CLI, `dataclasses` for the detection report.

**Spec reference:** `docs/superpowers/specs/2026-05-03-windows-installer-design.md` sections 4 (steps 2-6 of wizard) and 7 (error handling).

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `installer/__init__.py` | Create | Empty package marker |
| `installer/setup_engine/__init__.py` | Create | Re-exports the public API of all 4 modules |
| `installer/setup_engine/detect.py` | Create | `EnvironmentReport` dataclass + `detect_environment()` |
| `installer/setup_engine/claude_config.py` | Create | Find/back-up/edit `claude_desktop_config.json` to register the MCP server |
| `installer/setup_engine/fl_studio.py` | Create | Locate FL Studio Hardware dir + copy `device_test.py` + metadata file |
| `installer/setup_engine/loopmidi.py` | Create | Download loopMIDI installer + silent install + create/check `FL_MCP` virtual port |
| `installer/setup_engine/cli.py` | Create | argparse wrapper exposing each step as a subcommand for manual debugging |
| `tests/setup_engine/__init__.py` | Create | Empty package marker |
| `tests/setup_engine/test_detect.py` | Create | Unit tests for environment detection |
| `tests/setup_engine/test_claude_config.py` | Create | Unit tests for Claude Desktop config editing |
| `tests/setup_engine/test_fl_studio.py` | Create | Unit tests for FL Studio script installation |
| `tests/setup_engine/test_loopmidi.py` | Create | Unit tests for loopMIDI download/install/port creation |
| `tests/setup_engine/test_cli.py` | Create | Smoke test that the CLI imports and lists subcommands |
| `requirements-dev.txt` | Modify | Add `pyfakefs==5.7.1` |

**Cross-platform strategy (per user decision, option C):** Functions accept paths as parameters; defaults read from `os.environ.get("APPDATA")` / `os.environ.get("USERPROFILE")` etc. Linux dev runs pass explicit paths or use pyfakefs. Functions that genuinely cannot work on Linux (calling `loopMIDI.exe`) raise `NotImplementedError("Windows only")` only at the point of subprocess invocation — pure-logic helpers stay portable.

---

## Task 1: Add pyfakefs + create package skeleton

**Files:**
- Modify: `requirements-dev.txt`
- Create: `installer/__init__.py`
- Create: `installer/setup_engine/__init__.py`
- Create: `tests/setup_engine/__init__.py`

- [ ] **Step 1: Add `pyfakefs` to dev deps**

Replace `requirements-dev.txt` content with:

```
pytest==8.3.4
pytest-mock==3.14.0
pyfakefs==5.7.1
```

- [ ] **Step 2: Install the new dep**

```bash
cd "/home/roska/Documentos/FL MCP"
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Expected: `pyfakefs` installs without errors.

- [ ] **Step 3: Create the package directories**

```bash
mkdir -p installer/setup_engine tests/setup_engine
```

- [ ] **Step 4: Create empty `__init__.py` files**

Create three zero-byte files:
- `installer/__init__.py`
- `installer/setup_engine/__init__.py`
- `tests/setup_engine/__init__.py`

- [ ] **Step 5: Verify pytest discovers the new test directory**

Run:
```bash
pytest --collect-only 2>&1 | tail -5
```

Expected: still says "15 tests collected" (the existing midi_transport tests). No errors about the new directory.

- [ ] **Step 6: Commit**

```bash
git add requirements-dev.txt installer/__init__.py installer/setup_engine/__init__.py tests/setup_engine/__init__.py
git commit -m "chore(setup-engine): scaffold package + add pyfakefs dev dep"
```

---

## Task 2: `detect.py` — Environment detection

**Files:**
- Create: `installer/setup_engine/detect.py`
- Create: `tests/setup_engine/test_detect.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/setup_engine/test_detect.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/setup_engine/test_detect.py -v
```

Expected: ImportError because `installer.setup_engine.detect` does not exist yet.

- [ ] **Step 3: Implement `detect.py`**

Create `installer/setup_engine/detect.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/setup_engine/test_detect.py -v
```

Expected: 14 tests PASS (4 EnvironmentReport + 2 ClaudeDesktop + 2 FlStudio + 2 Loopmidi + 2 WebView2 + 1 aggregator + 1 already counted = 14).

- [ ] **Step 5: Commit**

```bash
git add installer/setup_engine/detect.py tests/setup_engine/test_detect.py
git commit -m "feat(setup-engine): add environment detection with EnvironmentReport"
```

---

## Task 3: `claude_config.py` — Edit Claude Desktop config

**Files:**
- Create: `installer/setup_engine/claude_config.py`
- Create: `tests/setup_engine/test_claude_config.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/setup_engine/test_claude_config.py`:

```python
"""Tests for installer.setup_engine.claude_config."""
import json
from pathlib import Path
import pytest

from installer.setup_engine.claude_config import (
    find_config_path,
    backup_config,
    register_mcp_server,
    ConfigCorruptedError,
)


class TestFindConfigPath:
    def test_returns_default_path(self):
        appdata = Path("C:/Users/u/AppData/Roaming")
        result = find_config_path(appdata=appdata)
        assert result == appdata / "Claude" / "claude_desktop_config.json"


class TestBackupConfig:
    def test_creates_bak_with_same_contents(self, fs):
        config = Path("C:/Users/u/AppData/Roaming/Claude/claude_desktop_config.json")
        fs.create_file(str(config), contents='{"foo": "bar"}')

        backup_path = backup_config(config)

        assert backup_path == config.with_suffix(".json.bak")
        assert backup_path.read_text() == '{"foo": "bar"}'

    def test_no_op_when_config_missing(self, fs):
        config = Path("C:/Users/u/AppData/Roaming/Claude/claude_desktop_config.json")
        result = backup_config(config)
        assert result is None


class TestRegisterMcpServer:
    def test_creates_config_when_missing(self, fs):
        config = Path("C:/Users/u/AppData/Roaming/Claude/claude_desktop_config.json")
        fs.create_dir(str(config.parent))

        register_mcp_server(
            config_path=config,
            name="flstudio",
            command="C:/Program Files/FL MCP Studio/python-embed/python.exe",
            args=["C:/Program Files/FL MCP Studio/trigger.py"],
        )

        data = json.loads(config.read_text())
        assert data == {
            "mcpServers": {
                "flstudio": {
                    "command": "C:/Program Files/FL MCP Studio/python-embed/python.exe",
                    "args": ["C:/Program Files/FL MCP Studio/trigger.py"],
                }
            }
        }

    def test_preserves_existing_servers(self, fs):
        config = Path("C:/Users/u/AppData/Roaming/Claude/claude_desktop_config.json")
        existing = {
            "mcpServers": {
                "other-server": {"command": "node", "args": ["other.js"]}
            }
        }
        fs.create_file(str(config), contents=json.dumps(existing))

        register_mcp_server(
            config_path=config,
            name="flstudio",
            command="python",
            args=["trigger.py"],
        )

        data = json.loads(config.read_text())
        assert "other-server" in data["mcpServers"]
        assert data["mcpServers"]["flstudio"] == {
            "command": "python",
            "args": ["trigger.py"],
        }

    def test_overwrites_same_named_server(self, fs):
        config = Path("C:/Users/u/AppData/Roaming/Claude/claude_desktop_config.json")
        existing = {
            "mcpServers": {
                "flstudio": {"command": "old", "args": ["old.py"]}
            }
        }
        fs.create_file(str(config), contents=json.dumps(existing))

        register_mcp_server(
            config_path=config,
            name="flstudio",
            command="new",
            args=["new.py"],
        )

        data = json.loads(config.read_text())
        assert data["mcpServers"]["flstudio"] == {
            "command": "new",
            "args": ["new.py"],
        }

    def test_raises_on_corrupted_json(self, fs):
        config = Path("C:/Users/u/AppData/Roaming/Claude/claude_desktop_config.json")
        fs.create_file(str(config), contents="this is not json {")

        with pytest.raises(ConfigCorruptedError, match="claude_desktop_config.json"):
            register_mcp_server(
                config_path=config,
                name="flstudio",
                command="python",
                args=["trigger.py"],
            )

    def test_writes_with_2_space_indent(self, fs):
        config = Path("C:/Users/u/AppData/Roaming/Claude/claude_desktop_config.json")
        fs.create_dir(str(config.parent))

        register_mcp_server(
            config_path=config,
            name="flstudio",
            command="python",
            args=["trigger.py"],
        )

        text = config.read_text()
        assert "  \"mcpServers\"" in text  # 2-space indent on top-level key
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/setup_engine/test_claude_config.py -v
```

Expected: ImportError on `installer.setup_engine.claude_config`.

- [ ] **Step 3: Implement `claude_config.py`**

Create `installer/setup_engine/claude_config.py`:

```python
"""Edit Claude Desktop's MCP server configuration safely.

We always create a `.bak` of the existing config before mutating it. JSON parse
errors raise `ConfigCorruptedError` so the caller can offer the user a recovery
path (restore from .bak or write a fresh config).
"""
import json
import os
import shutil
from pathlib import Path
from typing import Optional


class ConfigCorruptedError(Exception):
    """Raised when the existing claude_desktop_config.json is not valid JSON."""


def _default_appdata() -> Path:
    return Path(os.environ.get("APPDATA", ""))


def find_config_path(appdata: Optional[Path] = None) -> Path:
    """Return the canonical location of Claude Desktop's config file."""
    base = appdata if appdata is not None else _default_appdata()
    return base / "Claude" / "claude_desktop_config.json"


def backup_config(config_path: Path) -> Optional[Path]:
    """Copy the config to `<name>.json.bak`. Returns the backup path, or None
    if the source did not exist (no backup needed).
    """
    if not config_path.exists():
        return None
    backup_path = config_path.with_suffix(".json.bak")
    shutil.copy2(config_path, backup_path)
    return backup_path


def register_mcp_server(
    config_path: Path,
    name: str,
    command: str,
    args: list[str],
) -> None:
    """Idempotently add (or overwrite) an MCP server entry in the config.

    Existing servers under different names are preserved. If the file does not
    exist, it is created with just this one server. The file is always written
    back with 2-space indentation for human readability.

    Raises ConfigCorruptedError if the existing file is not valid JSON.
    """
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text())
        except json.JSONDecodeError as exc:
            raise ConfigCorruptedError(
                f"{config_path.name} is not valid JSON: {exc.msg}"
            ) from exc
    else:
        data = {}

    servers = data.setdefault("mcpServers", {})
    servers[name] = {"command": command, "args": args}

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(data, indent=2))
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/setup_engine/test_claude_config.py -v
```

Expected: 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add installer/setup_engine/claude_config.py tests/setup_engine/test_claude_config.py
git commit -m "feat(setup-engine): edit Claude Desktop config with backup + idempotency"
```

---

## Task 4: `fl_studio.py` — Install device script

**Files:**
- Create: `installer/setup_engine/fl_studio.py`
- Create: `tests/setup_engine/test_fl_studio.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/setup_engine/test_fl_studio.py`:

```python
"""Tests for installer.setup_engine.fl_studio."""
from pathlib import Path
import pytest

from installer.setup_engine.fl_studio import (
    find_hardware_dir,
    install_device_script,
    HARDWARE_SUBDIR,
)


class TestFindHardwareDir:
    def test_returns_hardware_subdir_under_settings(self, fs):
        settings_dir = Path("C:/Users/u/Documents/Image-Line/FL Studio/Settings")
        fs.create_dir(str(settings_dir))

        result = find_hardware_dir(fl_studio_settings_dir=settings_dir)

        assert result == settings_dir / "Hardware"

    def test_creates_hardware_dir_if_missing(self, fs):
        settings_dir = Path("C:/Users/u/Documents/Image-Line/FL Studio/Settings")
        fs.create_dir(str(settings_dir))

        result = find_hardware_dir(fl_studio_settings_dir=settings_dir)

        assert result.is_dir()


class TestInstallDeviceScript:
    def test_copies_script_under_named_subdir(self, fs):
        settings_dir = Path("C:/Users/u/Documents/Image-Line/FL Studio/Settings")
        fs.create_dir(str(settings_dir))
        source_script = Path("/install/device_test.py")
        fs.create_file(str(source_script), contents="# device script body\n")

        result = install_device_script(
            source_script=source_script,
            fl_studio_settings_dir=settings_dir,
            device_name="FL_MCP",
        )

        target = settings_dir / "Hardware" / "FL_MCP" / "device_test.py"
        assert target.exists()
        assert target.read_text() == "# device script body\n"
        assert result == target

    def test_writes_companion_metadata_file(self, fs):
        settings_dir = Path("C:/Users/u/Documents/Image-Line/FL Studio/Settings")
        fs.create_dir(str(settings_dir))
        source_script = Path("/install/device_test.py")
        fs.create_file(str(source_script), contents="x")

        install_device_script(
            source_script=source_script,
            fl_studio_settings_dir=settings_dir,
            device_name="FL_MCP",
        )

        meta = settings_dir / "Hardware" / "FL_MCP" / "device_FL_MCP.nfo"
        assert meta.exists()
        text = meta.read_text()
        assert "FL_MCP" in text
        assert "device_test.py" in text

    def test_overwrites_existing_install(self, fs):
        settings_dir = Path("C:/Users/u/Documents/Image-Line/FL Studio/Settings")
        target_dir = settings_dir / "Hardware" / "FL_MCP"
        fs.create_file(str(target_dir / "device_test.py"), contents="OLD")
        source_script = Path("/install/device_test.py")
        fs.create_file(str(source_script), contents="NEW")

        install_device_script(
            source_script=source_script,
            fl_studio_settings_dir=settings_dir,
            device_name="FL_MCP",
        )

        assert (target_dir / "device_test.py").read_text() == "NEW"

    def test_raises_when_source_missing(self, fs):
        settings_dir = Path("C:/Users/u/Documents/Image-Line/FL Studio/Settings")
        fs.create_dir(str(settings_dir))
        source_script = Path("/install/missing.py")

        with pytest.raises(FileNotFoundError):
            install_device_script(
                source_script=source_script,
                fl_studio_settings_dir=settings_dir,
                device_name="FL_MCP",
            )


def test_hardware_subdir_constant_value():
    assert HARDWARE_SUBDIR == "Hardware"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/setup_engine/test_fl_studio.py -v
```

Expected: ImportError on `installer.setup_engine.fl_studio`.

- [ ] **Step 3: Implement `fl_studio.py`**

Create `installer/setup_engine/fl_studio.py`:

```python
"""Install the FL MCP `device_test.py` script into FL Studio's Hardware folder.

FL Studio reads MIDI controller scripts from
`<Settings>/Hardware/<DeviceName>/device_*.py`. We create that directory if
needed and write both the script and a small `.nfo` companion that FL Studio
uses to display the device's friendly name in its MIDI Settings panel.
"""
import shutil
from pathlib import Path

HARDWARE_SUBDIR = "Hardware"


def find_hardware_dir(fl_studio_settings_dir: Path) -> Path:
    """Return the Hardware/ directory under FL Studio's Settings, creating it
    if it does not yet exist (FL Studio creates it on first scripted-controller
    install, so missing-on-fresh-install is normal)."""
    hardware = fl_studio_settings_dir / HARDWARE_SUBDIR
    hardware.mkdir(parents=True, exist_ok=True)
    return hardware


def install_device_script(
    source_script: Path,
    fl_studio_settings_dir: Path,
    device_name: str,
) -> Path:
    """Copy `source_script` to `<Settings>/Hardware/<device_name>/device_test.py`
    and write a companion `device_<name>.nfo` metadata file. Returns the path to
    the installed script.

    Overwrites any existing files at the target location (the GUI presents this
    as "reinstall" rather than "fresh install" when re-run).
    """
    if not source_script.exists():
        raise FileNotFoundError(f"Source script not found: {source_script}")

    hardware = find_hardware_dir(fl_studio_settings_dir)
    device_dir = hardware / device_name
    device_dir.mkdir(parents=True, exist_ok=True)

    target_script = device_dir / "device_test.py"
    shutil.copyfile(source_script, target_script)

    nfo = device_dir / f"device_{device_name}.nfo"
    nfo.write_text(
        f"name={device_name}\n"
        f"script=device_test.py\n"
        "vendor=FL MCP Studio\n"
    )

    return target_script
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/setup_engine/test_fl_studio.py -v
```

Expected: 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add installer/setup_engine/fl_studio.py tests/setup_engine/test_fl_studio.py
git commit -m "feat(setup-engine): install device_test.py into FL Studio Hardware dir"
```

---

## Task 5: `loopmidi.py` — Port creation + detection

**Files:**
- Create: `installer/setup_engine/loopmidi.py` (partial — port operations only; download in Task 6)
- Create: `tests/setup_engine/test_loopmidi.py` (port test class only)

- [ ] **Step 1: Write the failing tests**

Create `tests/setup_engine/test_loopmidi.py`:

```python
"""Tests for installer.setup_engine.loopmidi."""
from pathlib import Path
from unittest.mock import MagicMock, call
import pytest

from installer.setup_engine.loopmidi import (
    port_exists,
    create_port,
    LoopMidiNotInstalledError,
)


class TestPortExists:
    def test_returns_true_when_rtmidi_lists_port(self, mock_rtmidi):
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = [
            "Microsoft GS Wavetable Synth 0",
            "FL_MCP 1",
        ]

        assert port_exists("FL_MCP") is True

    def test_returns_false_when_no_match(self, mock_rtmidi):
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = ["Other 0"]

        assert port_exists("FL_MCP") is False

    def test_substring_match_is_used(self, mock_rtmidi):
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = ["FL_MCP Suffix 2"]

        assert port_exists("FL_MCP") is True


class TestCreatePort:
    def test_invokes_loopmidi_with_addport_flag(self, monkeypatch, mock_rtmidi):
        loopmidi_exe = Path("C:/Program Files/loopMIDI/loopMIDI.exe")
        # First poll: port absent. After "running" loopMIDI, port present.
        mock_rtmidi.MidiOut.return_value.get_ports.side_effect = [
            [],            # before
            ["FL_MCP 0"],  # after
        ]
        fake_run = MagicMock(return_value=MagicMock(returncode=0))
        monkeypatch.setattr("subprocess.run", fake_run)

        create_port(loopmidi_exe=loopmidi_exe, port_name="FL_MCP")

        fake_run.assert_called_once_with(
            [str(loopmidi_exe), "/AddPort:FL_MCP"],
            capture_output=True,
            text=True,
            timeout=15,
        )

    def test_no_op_when_port_already_exists(self, monkeypatch, mock_rtmidi):
        loopmidi_exe = Path("C:/Program Files/loopMIDI/loopMIDI.exe")
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = ["FL_MCP 0"]
        fake_run = MagicMock()
        monkeypatch.setattr("subprocess.run", fake_run)

        create_port(loopmidi_exe=loopmidi_exe, port_name="FL_MCP")

        fake_run.assert_not_called()

    def test_raises_when_loopmidi_exe_missing(self, monkeypatch, mock_rtmidi):
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = []
        loopmidi_exe = Path("C:/missing/loopMIDI.exe")

        with pytest.raises(LoopMidiNotInstalledError):
            create_port(loopmidi_exe=loopmidi_exe, port_name="FL_MCP")

    def test_raises_when_loopmidi_call_fails(self, monkeypatch, fs, mock_rtmidi):
        loopmidi_exe = Path("C:/Program Files/loopMIDI/loopMIDI.exe")
        fs.create_file(str(loopmidi_exe))
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = []
        fake_run = MagicMock(return_value=MagicMock(returncode=1, stderr="busy"))
        monkeypatch.setattr("subprocess.run", fake_run)

        with pytest.raises(RuntimeError, match="loopMIDI exited with code 1"):
            create_port(loopmidi_exe=loopmidi_exe, port_name="FL_MCP")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/setup_engine/test_loopmidi.py -v
```

Expected: ImportError on `installer.setup_engine.loopmidi`.

- [ ] **Step 3: Implement port operations in `loopmidi.py`**

Create `installer/setup_engine/loopmidi.py`:

```python
"""Manage loopMIDI virtual MIDI ports on Windows.

We use python-rtmidi to enumerate existing ports (works cross-platform for tests
via the mock_rtmidi fixture) and shell out to loopMIDI.exe with /AddPort: flags
to create new ones (Windows only, mocked in tests).

Download/install of loopMIDI itself is in this same module (added in Task 6) but
kept as separate functions for clarity.
"""
import subprocess
from pathlib import Path


class LoopMidiNotInstalledError(Exception):
    """Raised when loopMIDI.exe is not present at the expected path."""


def port_exists(port_name: str) -> bool:
    """Return True if any rtmidi-visible output port name contains `port_name`."""
    import rtmidi
    out = rtmidi.MidiOut()
    return any(port_name in name for name in out.get_ports())


def create_port(loopmidi_exe: Path, port_name: str) -> None:
    """Create a virtual loopMIDI port named `port_name`. No-op if it already exists.

    Raises LoopMidiNotInstalledError if `loopmidi_exe` is missing on disk.
    Raises RuntimeError if the loopMIDI invocation returns a non-zero exit code.
    """
    if port_exists(port_name):
        return

    if not loopmidi_exe.exists():
        raise LoopMidiNotInstalledError(f"loopMIDI not found at {loopmidi_exe}")

    result = subprocess.run(
        [str(loopmidi_exe), f"/AddPort:{port_name}"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"loopMIDI exited with code {result.returncode}: {result.stderr.strip()}"
        )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/setup_engine/test_loopmidi.py -v
```

Expected: 7 tests PASS (3 port_exists + 4 create_port).

- [ ] **Step 5: Commit**

```bash
git add installer/setup_engine/loopmidi.py tests/setup_engine/test_loopmidi.py
git commit -m "feat(setup-engine): create + detect FL_MCP virtual MIDI port via loopMIDI"
```

---

## Task 6: `loopmidi.py` — Download + silent install

**Files:**
- Modify: `installer/setup_engine/loopmidi.py` (APPEND functions)
- Modify: `tests/setup_engine/test_loopmidi.py` (APPEND test class)

- [ ] **Step 1: Write the failing tests**

APPEND to `tests/setup_engine/test_loopmidi.py`:

```python
from installer.setup_engine.loopmidi import (
    download_loopmidi,
    install_loopmidi,
    LOOPMIDI_DOWNLOAD_URL,
)


class TestDownloadLoopmidi:
    def test_writes_installer_to_dest(self, monkeypatch, fs):
        fs.create_dir("/tmp")
        dest = Path("/tmp/loopmidi_setup.exe")
        fake_response = MagicMock()
        fake_response.read.return_value = b"FAKE INSTALLER BYTES"
        fake_response.__enter__ = MagicMock(return_value=fake_response)
        fake_response.__exit__ = MagicMock(return_value=False)

        fake_urlopen = MagicMock(return_value=fake_response)
        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

        result = download_loopmidi(dest=dest)

        assert result == dest
        assert dest.read_bytes() == b"FAKE INSTALLER BYTES"
        fake_urlopen.assert_called_once_with(LOOPMIDI_DOWNLOAD_URL, timeout=60)

    def test_raises_on_network_error(self, monkeypatch, fs):
        from urllib.error import URLError
        fs.create_dir("/tmp")
        dest = Path("/tmp/loopmidi_setup.exe")
        monkeypatch.setattr(
            "urllib.request.urlopen",
            MagicMock(side_effect=URLError("no internet")),
        )

        with pytest.raises(URLError):
            download_loopmidi(dest=dest)


class TestInstallLoopmidi:
    def test_runs_installer_silently(self, monkeypatch, fs):
        installer = Path("C:/tmp/loopmidi_setup.exe")
        fs.create_file(str(installer))
        fake_run = MagicMock(return_value=MagicMock(returncode=0))
        monkeypatch.setattr("subprocess.run", fake_run)

        install_loopmidi(installer=installer)

        fake_run.assert_called_once_with(
            [str(installer), "/SILENT", "/NORESTART"],
            capture_output=True,
            text=True,
            timeout=120,
        )

    def test_raises_on_installer_failure(self, monkeypatch, fs):
        installer = Path("C:/tmp/loopmidi_setup.exe")
        fs.create_file(str(installer))
        monkeypatch.setattr(
            "subprocess.run",
            MagicMock(return_value=MagicMock(returncode=2, stderr="cancelled")),
        )

        with pytest.raises(RuntimeError, match="loopMIDI installer exited with code 2"):
            install_loopmidi(installer=installer)


def test_download_url_points_to_official_site():
    assert "tobias-erichsen.de" in LOOPMIDI_DOWNLOAD_URL
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/setup_engine/test_loopmidi.py::TestDownloadLoopmidi tests/setup_engine/test_loopmidi.py::TestInstallLoopmidi -v
```

Expected: ImportError on `download_loopmidi`/`install_loopmidi`.

- [ ] **Step 3: Implement download + install**

APPEND to `installer/setup_engine/loopmidi.py`:

```python
import urllib.request

# Tobias Erichsen's official download. Free, but the author asks that we link to
# his site rather than mirror the binary. We download fresh on every install so
# users always get the current version.
LOOPMIDI_DOWNLOAD_URL = (
    "https://www.tobias-erichsen.de/wp-content/uploads/2020/01/loopMIDISetup_1_0_16_27.zip"
)


def download_loopmidi(dest: Path) -> Path:
    """Download the loopMIDI installer from the official site to `dest`.

    Raises urllib.error.URLError on network failures.
    """
    with urllib.request.urlopen(LOOPMIDI_DOWNLOAD_URL, timeout=60) as response:
        dest.write_bytes(response.read())
    return dest


def install_loopmidi(installer: Path) -> None:
    """Run the loopMIDI installer silently (`/SILENT /NORESTART`).

    Raises RuntimeError if the installer exits with a non-zero code.
    """
    result = subprocess.run(
        [str(installer), "/SILENT", "/NORESTART"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"loopMIDI installer exited with code {result.returncode}: {result.stderr.strip()}"
        )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/setup_engine/test_loopmidi.py -v
```

Expected: 12 PASS (7 from Task 5 + 5 new).

- [ ] **Step 5: Commit**

```bash
git add installer/setup_engine/loopmidi.py tests/setup_engine/test_loopmidi.py
git commit -m "feat(setup-engine): download + silent-install loopMIDI from official site"
```

---

## Task 7: `cli.py` — argparse subcommand wrapper

**Files:**
- Create: `installer/setup_engine/cli.py`
- Create: `tests/setup_engine/test_cli.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/setup_engine/test_cli.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/setup_engine/test_cli.py -v
```

Expected: ImportError on `cli`.

- [ ] **Step 3: Implement `cli.py`**

Create `installer/setup_engine/cli.py`:

```python
"""Command-line interface for the Setup Engine.

Each setup step has a subcommand so the GUI (sub-project C) can shell out OR
import these functions directly. Useful standalone for QA on real Windows
machines without a GUI.
"""
import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from installer.setup_engine.detect import detect_environment
from installer.setup_engine.claude_config import (
    find_config_path,
    backup_config,
    register_mcp_server,
)
from installer.setup_engine.fl_studio import install_device_script
from installer.setup_engine.loopmidi import (
    create_port,
    download_loopmidi,
    install_loopmidi,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="setup_engine",
        description="FL MCP Studio installer — Setup Engine CLI (run subcommands manually for debugging).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("detect", help="Print which dependencies are installed.")

    p_install_lm = sub.add_parser("install-loopmidi", help="Download + silent-install loopMIDI.")
    p_install_lm.add_argument("--dest", type=Path, default=Path("loopmidi_setup.exe"),
                              help="Where to save the downloaded installer.")

    p_create = sub.add_parser("create-port", help="Create a loopMIDI virtual port.")
    p_create.add_argument("--loopmidi-exe", type=Path, required=True)
    p_create.add_argument("--port-name", type=str, default="FL_MCP")

    p_script = sub.add_parser("install-script", help="Copy device_test.py into FL Studio's Hardware dir.")
    p_script.add_argument("--source", type=Path, required=True)
    p_script.add_argument("--fl-settings", type=Path, required=True)
    p_script.add_argument("--device-name", type=str, default="FL_MCP")

    p_mcp = sub.add_parser("register-mcp", help="Register the FL MCP server in Claude Desktop config.")
    p_mcp.add_argument("--config", type=Path, default=None,
                       help="Path to claude_desktop_config.json (default: %APPDATA%/Claude/...)")
    p_mcp.add_argument("--name", type=str, default="flstudio")
    p_mcp.add_argument("--command", type=str, required=True,
                       help="Python interpreter path to launch the MCP server.")
    p_mcp.add_argument("--args", nargs="+", required=True,
                       help="Arguments passed to the interpreter (typically [trigger.py]).")

    return parser


def _print_detect(report) -> None:
    def status(value) -> str:
        return "OK" if value else "MISSING"

    print(f"Claude Desktop:       {status(report.claude_desktop_path)} ({report.claude_desktop_path})")
    print(f"FL Studio Settings:   {status(report.fl_studio_settings_dir)} ({report.fl_studio_settings_dir})")
    print(f"loopMIDI:             {status(report.loopmidi_path)} ({report.loopmidi_path})")
    print(f"WebView2 Runtime:     {status(report.webview2_installed)}")
    print(f"\nReady to install: {report.is_ready()}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "detect":
        report = detect_environment()
        _print_detect(report)
        return 0 if report.is_ready() else 1

    if args.command == "install-loopmidi":
        download_loopmidi(dest=args.dest)
        install_loopmidi(installer=args.dest)
        return 0

    if args.command == "create-port":
        create_port(loopmidi_exe=args.loopmidi_exe, port_name=args.port_name)
        return 0

    if args.command == "install-script":
        install_device_script(
            source_script=args.source,
            fl_studio_settings_dir=args.fl_settings,
            device_name=args.device_name,
        )
        return 0

    if args.command == "register-mcp":
        config = args.config or find_config_path()
        backup_config(config)
        register_mcp_server(
            config_path=config,
            name=args.name,
            command=args.command,
            args=args.args,
        )
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2  # unreachable but satisfies type checkers


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/setup_engine/test_cli.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Verify CLI is invokable**

```bash
python -m installer.setup_engine.cli --help 2>&1 | head -15
```

Expected: argparse help output with all 5 subcommands listed.

- [ ] **Step 6: Commit**

```bash
git add installer/setup_engine/cli.py tests/setup_engine/test_cli.py
git commit -m "feat(setup-engine): add argparse CLI exposing each step as a subcommand"
```

---

## Task 8: Public API + docs update

**Files:**
- Modify: `installer/setup_engine/__init__.py` (add re-exports)
- Modify: `CLAUDE.md` (add setup_engine section)

- [ ] **Step 1: Re-export the public API**

Replace the empty `installer/setup_engine/__init__.py` with:

```python
"""Setup Engine — pure-Python library that performs the install steps the
Windows wizard (sub-project C) needs to invoke. Each module is independently
testable; this package re-exports the names the wizard will import.
"""
from installer.setup_engine.detect import (
    EnvironmentReport,
    detect_environment,
)
from installer.setup_engine.claude_config import (
    ConfigCorruptedError,
    backup_config,
    find_config_path,
    register_mcp_server,
)
from installer.setup_engine.fl_studio import install_device_script
from installer.setup_engine.loopmidi import (
    LOOPMIDI_DOWNLOAD_URL,
    LoopMidiNotInstalledError,
    create_port,
    download_loopmidi,
    install_loopmidi,
    port_exists,
)

__all__ = [
    "ConfigCorruptedError",
    "EnvironmentReport",
    "LOOPMIDI_DOWNLOAD_URL",
    "LoopMidiNotInstalledError",
    "backup_config",
    "create_port",
    "detect_environment",
    "download_loopmidi",
    "find_config_path",
    "install_device_script",
    "install_loopmidi",
    "port_exists",
    "register_mcp_server",
]
```

- [ ] **Step 2: Verify the package imports cleanly**

```bash
python -c "from installer.setup_engine import EnvironmentReport, detect_environment, create_port; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Run the full test suite**

```bash
pytest
```

Expected: 15 (existing midi_transport) + 14 (detect) + 8 (claude_config) + 7 (fl_studio) + 12 (loopmidi) + 3 (cli) = **59 tests PASS**.

- [ ] **Step 4: Update `CLAUDE.md`**

Add a new section after the "## Sistema de Mixer" section, before "## Preferencias del Proyecto":

```markdown
---

## Sistema de Instalación (Windows)

`installer/setup_engine/` es la biblioteca pura de Python que hace el setup automático del MCP en Windows. Diseñada para que la GUI del wizard (sub-proyecto C) la importe.

| Módulo | Responsabilidad |
|---|---|
| `detect.py` | Devuelve `EnvironmentReport` con qué hay instalado (Claude Desktop, FL Studio, loopMIDI, WebView2) |
| `claude_config.py` | Edita `claude_desktop_config.json` con backup `.bak`. Tira `ConfigCorruptedError` si el JSON está roto |
| `fl_studio.py` | Copia `device_test.py` a `Documents/Image-Line/FL Studio/Settings/Hardware/FL_MCP/` + crea `.nfo` companion |
| `loopmidi.py` | Descarga loopMIDI del sitio oficial, instalación silenciosa, crea/detecta puerto virtual `FL_MCP` |
| `cli.py` | Wrapper argparse: `python -m installer.setup_engine.cli <subcommand>` para QA manual |

Tests: `pytest tests/setup_engine/` (corre en Linux con pyfakefs + mocks de subprocess/urllib/rtmidi).
```

- [ ] **Step 5: Commit**

```bash
git add installer/setup_engine/__init__.py CLAUDE.md
git commit -m "docs(setup-engine): expose public API + document in CLAUDE.md"
```

---

## Done — what you should have at the end

- 5 modules under `installer/setup_engine/` with clean public API
- 44 unit tests (14 detect + 8 claude_config + 7 fl_studio + 12 loopmidi + 3 cli)
- Full suite of 59 tests passing (15 from Plan A + 44 new)
- Working CLI: `python -m installer.setup_engine.cli --help`
- Updated `CLAUDE.md` describing the new package
- 8 small commits, each independently revertible

## Verification checklist before declaring done

- [ ] `pytest` reports 59 PASS, 0 FAIL
- [ ] `python -m installer.setup_engine.cli --help` lists all 5 subcommands
- [ ] `python -c "from installer.setup_engine import detect_environment; print(detect_environment())"` runs without error (will report all-MISSING on Linux, which is expected)
- [ ] `git log --oneline` shows 8 new commits

## Out of scope (sub-project C will handle)

- Wizard UI: progress bars, "next" buttons, GIF for FL Studio manual step
- Tray app: status icon, menu, supervisor of MCP server process
- Auto-update notifications
- Inno Setup bundling

These pieces will import the functions exposed here; this plan delivers the engine that makes the wizard's job a series of single-line calls.
