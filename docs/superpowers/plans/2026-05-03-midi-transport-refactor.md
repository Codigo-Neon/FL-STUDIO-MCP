# MIDI Transport Cross-Platform Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Abstract the MIDI transport layer in `trigger.py` so the same code runs on Linux (raw `/dev/snd/midiC0D0` writes) and Windows (`python-rtmidi` to a virtual port named `FL_MCP`), with full test coverage and zero Linux regressions.

**Architecture:** Introduce a new module `knowledge/midi_transport.py` that exposes a `MidiTransport` protocol with two implementations (`LinuxRawTransport`, `WindowsRtmidiTransport`) and a `create_transport()` factory that picks the right one via `sys.platform`. Refactor `trigger.py` to call the factory once at module init and route `send_raw_midi()` through it.

**Tech Stack:** Python 3.11+, `python-rtmidi==1.5.8` (already in requirements.txt), `pytest` (new dev dep), `unittest.mock` for platform mocking.

**Spec reference:** `docs/superpowers/specs/2026-05-03-windows-installer-design.md` section 3 ("Cambio crítico en código existente")

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `knowledge/midi_transport.py` | Create | Protocol + Linux + Windows transport classes + factory |
| `tests/__init__.py` | Create | Empty marker, makes `tests/` a package |
| `tests/conftest.py` | Create | Shared pytest fixtures (mock rtmidi, temp device files) |
| `tests/test_midi_transport.py` | Create | Unit tests for all transport classes and the factory |
| `trigger.py` | Modify | Replace `open(MIDI_DEV)` + `send_raw_midi` with calls to the new module (lines 88-95) |
| `requirements-dev.txt` | Create | pytest + pytest-mock for dev dependencies |
| `pytest.ini` | Create | Pytest config: testpaths, no-cache, verbose |

---

## Task 1: Set up testing infrastructure

**Files:**
- Create: `requirements-dev.txt`
- Create: `pytest.ini`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create `requirements-dev.txt`**

```
pytest==8.3.4
pytest-mock==3.14.0
```

- [ ] **Step 2: Install dev dependencies in the project venv**

Run:
```bash
cd "/home/roska/Documentos/FL MCP"
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Expected: pytest 8.3.4 and pytest-mock 3.14.0 installed without errors.

- [ ] **Step 3: Create `pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --no-header
```

- [ ] **Step 4: Create `tests/__init__.py`**

Empty file (zero bytes). Just makes `tests/` an importable package.

- [ ] **Step 5: Create `tests/conftest.py`**

```python
"""Shared pytest fixtures for the FL MCP test suite."""
import sys
from unittest.mock import MagicMock
import pytest


@pytest.fixture
def mock_rtmidi(monkeypatch):
    """Inject a fake `rtmidi` module so tests can run on platforms where rtmidi
    is not installed or where we want to control its behavior."""
    fake_rtmidi = MagicMock()
    monkeypatch.setitem(sys.modules, "rtmidi", fake_rtmidi)
    return fake_rtmidi


@pytest.fixture
def force_platform(monkeypatch):
    """Return a callable that overrides sys.platform for the duration of a test."""
    def _set(value: str) -> None:
        monkeypatch.setattr(sys, "platform", value)
    return _set
```

- [ ] **Step 6: Verify pytest can discover the empty test suite**

Run:
```bash
pytest
```

Expected: `no tests ran in 0.0Xs` — no errors, just "no tests collected".

- [ ] **Step 7: Commit**

```bash
git add requirements-dev.txt pytest.ini tests/__init__.py tests/conftest.py
git commit -m "test: add pytest infrastructure with rtmidi/platform fixtures"
```

---

## Task 2: Define the `MidiTransport` protocol

**Files:**
- Create: `knowledge/midi_transport.py`
- Create: `tests/test_midi_transport.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_midi_transport.py`:

```python
"""Tests for the cross-platform MIDI transport layer."""
from knowledge.midi_transport import MidiTransport


class TestMidiTransportProtocol:
    def test_protocol_has_send_method(self):
        assert hasattr(MidiTransport, "send")

    def test_protocol_has_close_method(self):
        assert hasattr(MidiTransport, "close")
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_midi_transport.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'knowledge.midi_transport'`.

- [ ] **Step 3: Create the protocol**

Create `knowledge/midi_transport.py`:

```python
"""Cross-platform MIDI transport abstraction.

The MCP server sends raw MIDI bytes to FL Studio. On Linux this means writing
directly to /dev/snd/midiC0D0; on Windows it means using python-rtmidi to send
to a virtual port created by loopMIDI. This module hides that difference.
"""
from typing import Protocol


class MidiTransport(Protocol):
    """Send raw MIDI bytes and clean up resources."""

    def send(self, data: bytes) -> None:
        """Send a MIDI message (status + data bytes)."""
        ...

    def close(self) -> None:
        """Release the underlying device or port."""
        ...
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/test_midi_transport.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add knowledge/midi_transport.py tests/test_midi_transport.py
git commit -m "feat(midi): introduce MidiTransport protocol"
```

---

## Task 3: Implement `LinuxRawTransport`

**Files:**
- Modify: `knowledge/midi_transport.py` (add class)
- Modify: `tests/test_midi_transport.py` (add test class)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_midi_transport.py`:

```python
from unittest.mock import MagicMock, call
from knowledge.midi_transport import LinuxRawTransport


class TestLinuxRawTransport:
    def test_opens_device_path_on_init(self, monkeypatch):
        fake_open = MagicMock()
        monkeypatch.setattr("builtins.open", fake_open)

        LinuxRawTransport(device_path="/dev/snd/midiC0D0")

        fake_open.assert_called_once_with("/dev/snd/midiC0D0", "wb", buffering=0)

    def test_send_writes_then_flushes(self, monkeypatch):
        fake_dev = MagicMock()
        fake_open = MagicMock(return_value=fake_dev)
        monkeypatch.setattr("builtins.open", fake_open)

        transport = LinuxRawTransport(device_path="/dev/snd/midiC0D0")
        transport.send(b"\x90\x3c\x64")

        assert fake_dev.method_calls == [
            call.write(b"\x90\x3c\x64"),
            call.flush(),
        ]

    def test_close_closes_device(self, monkeypatch):
        fake_dev = MagicMock()
        monkeypatch.setattr("builtins.open", MagicMock(return_value=fake_dev))

        transport = LinuxRawTransport(device_path="/dev/snd/midiC0D0")
        transport.close()

        fake_dev.close.assert_called_once()

    def test_default_device_path(self, monkeypatch):
        fake_open = MagicMock()
        monkeypatch.setattr("builtins.open", fake_open)

        LinuxRawTransport()

        fake_open.assert_called_once_with("/dev/snd/midiC0D0", "wb", buffering=0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
pytest tests/test_midi_transport.py::TestLinuxRawTransport -v
```

Expected: 4 FAILs with `ImportError: cannot import name 'LinuxRawTransport'`.

- [ ] **Step 3: Implement `LinuxRawTransport`**

Append to `knowledge/midi_transport.py`:

```python
class LinuxRawTransport:
    """Write raw MIDI bytes directly to an ALSA character device.

    This preserves the existing Linux behavior of trigger.py: open the device
    once at startup, write+flush per message. Wine forwards the bytes to FL
    Studio via the WINE ALSA Input connection.
    """

    DEFAULT_DEVICE = "/dev/snd/midiC0D0"

    def __init__(self, device_path: str = DEFAULT_DEVICE) -> None:
        self._dev = open(device_path, "wb", buffering=0)

    def send(self, data: bytes) -> None:
        self._dev.write(data)
        self._dev.flush()

    def close(self) -> None:
        self._dev.close()
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
pytest tests/test_midi_transport.py::TestLinuxRawTransport -v
```

Expected: 4 PASS.

- [ ] **Step 5: Commit**

```bash
git add knowledge/midi_transport.py tests/test_midi_transport.py
git commit -m "feat(midi): add LinuxRawTransport for /dev/snd character devices"
```

---

## Task 4: Implement `WindowsRtmidiTransport`

**Files:**
- Modify: `knowledge/midi_transport.py` (add class)
- Modify: `tests/test_midi_transport.py` (add test class)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_midi_transport.py`:

```python
import pytest
from knowledge.midi_transport import WindowsRtmidiTransport


class TestWindowsRtmidiTransport:
    def test_opens_matching_port(self, mock_rtmidi):
        midi_out = mock_rtmidi.MidiOut.return_value
        midi_out.get_ports.return_value = [
            "Microsoft GS Wavetable Synth 0",
            "FL_MCP 1",
            "loopMIDI Port 2",
        ]

        WindowsRtmidiTransport(port_name="FL_MCP")

        midi_out.open_port.assert_called_once_with(1)

    def test_raises_when_port_not_found(self, mock_rtmidi):
        midi_out = mock_rtmidi.MidiOut.return_value
        midi_out.get_ports.return_value = ["Other Port 0"]

        with pytest.raises(RuntimeError, match="MIDI port 'FL_MCP' not found"):
            WindowsRtmidiTransport(port_name="FL_MCP")

    def test_send_forwards_bytes_as_int_list(self, mock_rtmidi):
        midi_out = mock_rtmidi.MidiOut.return_value
        midi_out.get_ports.return_value = ["FL_MCP 0"]

        transport = WindowsRtmidiTransport(port_name="FL_MCP")
        transport.send(b"\x90\x3c\x64")

        midi_out.send_message.assert_called_once_with([0x90, 0x3C, 0x64])

    def test_close_closes_port(self, mock_rtmidi):
        midi_out = mock_rtmidi.MidiOut.return_value
        midi_out.get_ports.return_value = ["FL_MCP 0"]

        transport = WindowsRtmidiTransport(port_name="FL_MCP")
        transport.close()

        midi_out.close_port.assert_called_once()

    def test_default_port_name_is_fl_mcp(self, mock_rtmidi):
        midi_out = mock_rtmidi.MidiOut.return_value
        midi_out.get_ports.return_value = ["FL_MCP 0"]

        WindowsRtmidiTransport()

        midi_out.open_port.assert_called_once_with(0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
pytest tests/test_midi_transport.py::TestWindowsRtmidiTransport -v
```

Expected: 5 FAILs with `ImportError: cannot import name 'WindowsRtmidiTransport'`.

- [ ] **Step 3: Implement `WindowsRtmidiTransport`**

Append to `knowledge/midi_transport.py`:

```python
class WindowsRtmidiTransport:
    """Send MIDI bytes to a virtual port (created by loopMIDI) via python-rtmidi.

    The Windows installer creates a loopMIDI port named "FL_MCP" during setup;
    FL Studio is configured to read from it. We open the first port whose name
    contains the substring `port_name` (rtmidi suffixes ports with an index).
    """

    DEFAULT_PORT_NAME = "FL_MCP"

    def __init__(self, port_name: str = DEFAULT_PORT_NAME) -> None:
        import rtmidi  # imported lazily so Linux callers never need rtmidi
        self._out = rtmidi.MidiOut()
        for index, name in enumerate(self._out.get_ports()):
            if port_name in name:
                self._out.open_port(index)
                self._port_name = port_name
                return
        raise RuntimeError(f"MIDI port '{port_name}' not found")

    def send(self, data: bytes) -> None:
        self._out.send_message(list(data))

    def close(self) -> None:
        self._out.close_port()
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
pytest tests/test_midi_transport.py::TestWindowsRtmidiTransport -v
```

Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add knowledge/midi_transport.py tests/test_midi_transport.py
git commit -m "feat(midi): add WindowsRtmidiTransport using python-rtmidi"
```

---

## Task 5: Add the `create_transport()` factory

**Files:**
- Modify: `knowledge/midi_transport.py` (add function)
- Modify: `tests/test_midi_transport.py` (add test class)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_midi_transport.py`:

```python
from knowledge.midi_transport import create_transport, LinuxRawTransport, WindowsRtmidiTransport


class TestCreateTransport:
    def test_linux_returns_linux_raw_transport(self, force_platform, monkeypatch):
        force_platform("linux")
        monkeypatch.setattr("builtins.open", MagicMock())

        transport = create_transport()

        assert isinstance(transport, LinuxRawTransport)

    def test_win32_returns_windows_rtmidi_transport(self, force_platform, mock_rtmidi):
        force_platform("win32")
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = ["FL_MCP 0"]

        transport = create_transport()

        assert isinstance(transport, WindowsRtmidiTransport)

    def test_unsupported_platform_raises(self, force_platform):
        force_platform("darwin")

        with pytest.raises(RuntimeError, match="Unsupported platform: darwin"):
            create_transport()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
pytest tests/test_midi_transport.py::TestCreateTransport -v
```

Expected: 3 FAILs with `ImportError: cannot import name 'create_transport'`.

- [ ] **Step 3: Implement the factory**

Append to `knowledge/midi_transport.py`:

```python
import sys


def create_transport() -> MidiTransport:
    """Pick the right transport for the current OS.

    On macOS or any other unsupported platform we raise rather than guess —
    silent fallbacks would just produce confusing 'no MIDI received' bug
    reports.
    """
    if sys.platform == "linux":
        return LinuxRawTransport()
    if sys.platform == "win32":
        return WindowsRtmidiTransport()
    raise RuntimeError(f"Unsupported platform: {sys.platform}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
pytest tests/test_midi_transport.py -v
```

Expected: all 14 tests PASS (2 protocol + 4 Linux + 5 Windows + 3 factory).

- [ ] **Step 5: Commit**

```bash
git add knowledge/midi_transport.py tests/test_midi_transport.py
git commit -m "feat(midi): add platform-detecting create_transport factory"
```

---

## Task 6: Refactor `trigger.py` to use the new module

**Files:**
- Modify: `trigger.py:88-95` (replace device-open + send_raw_midi with module call)

- [ ] **Step 1: Read the current code to confirm the lines to replace**

Run:
```bash
sed -n '85,100p' "/home/roska/Documentos/FL MCP/trigger.py"
```

Expected output (these are the lines we will replace):

```python
# Initialize FastMCP server
mcp = FastMCP("flstudio")

MIDI_DEV = "/dev/snd/midiC0D0"
midi_dev = open(MIDI_DEV, "wb", buffering=0)

def send_raw_midi(hex_string):
    """Send raw MIDI bytes directly to device"""
    data = bytes.fromhex(hex_string.replace(" ", ""))
    midi_dev.write(data)
    midi_dev.flush()

# Global BPM state - tracks the current project tempo
```

- [ ] **Step 2: Replace lines 88-95 of `trigger.py`**

Use the Edit tool. Replace this block:

```python
MIDI_DEV = "/dev/snd/midiC0D0"
midi_dev = open(MIDI_DEV, "wb", buffering=0)

def send_raw_midi(hex_string):
    """Send raw MIDI bytes directly to device"""
    data = bytes.fromhex(hex_string.replace(" ", ""))
    midi_dev.write(data)
    midi_dev.flush()
```

With this:

```python
from knowledge.midi_transport import create_transport

_transport = create_transport()

def send_raw_midi(hex_string: str) -> None:
    """Send raw MIDI bytes to the active transport (Linux raw device or Windows rtmidi port)."""
    data = bytes.fromhex(hex_string.replace(" ", ""))
    _transport.send(data)
```

- [ ] **Step 3: Verify the file still imports cleanly on Linux**

Run:
```bash
cd "/home/roska/Documentos/FL MCP"
source .venv/bin/activate
python -c "import trigger; print('imported OK, transport:', type(trigger._transport).__name__)"
```

Expected: `imported OK, transport: LinuxRawTransport`

(If FL Studio isn't running and `/dev/snd/midiC0D0` doesn't exist, the open() will fail — that's the same failure mode as before the refactor, not a regression.)

- [ ] **Step 4: Verify all 8 prior `send_raw_midi` call sites still work syntactically**

Run:
```bash
grep -n "send_raw_midi" "/home/roska/Documentos/FL MCP/trigger.py"
```

Expected: 9 matches total — 1 def line + 8 call sites at lines 116, 118, 125, 127, 217, 219, 237, 240.

Run a syntax check:
```bash
python -m py_compile "/home/roska/Documentos/FL MCP/trigger.py"
```

Expected: no output (success).

- [ ] **Step 5: Run the full test suite one more time**

Run:
```bash
pytest
```

Expected: 14 tests PASS, no warnings related to our code.

- [ ] **Step 6: Commit**

```bash
git add trigger.py
git commit -m "refactor(trigger): route send_raw_midi through cross-platform transport"
```

---

## Task 7: Add a Linux smoke-test script

**Files:**
- Create: `tests/smoke_test_linux.py`

This is an opt-in script the user can run manually after FL Studio is connected to verify nothing regressed. Not part of the automated suite (it requires a real MIDI device).

- [ ] **Step 1: Create the smoke test script**

Create `tests/smoke_test_linux.py`:

```python
"""Manual smoke test for the Linux MIDI transport.

Run this AFTER FL Studio is open and the WINE ALSA connection is up:

    aconnect -l                   # confirm WINE ALSA Input is visible
    aconnect 'VirMIDI 0-0' 'WINE ALSA Input'

    python tests/smoke_test_linux.py

You should hear/see one C5 note (MIDI note 60) play in FL Studio. If you
hear nothing, the transport refactor regressed Linux behavior.
"""
import time
from knowledge.midi_transport import create_transport


def main() -> None:
    transport = create_transport()
    print(f"Using transport: {type(transport).__name__}")

    print("Sending C5 note ON (vel 100)...")
    transport.send(bytes.fromhex("90 3C 64"))
    time.sleep(0.5)

    print("Sending C5 note OFF...")
    transport.send(bytes.fromhex("80 3C 00"))

    transport.close()
    print("Done. Did you hear/see the note in FL Studio?")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify the script is syntactically valid**

Run:
```bash
python -m py_compile tests/smoke_test_linux.py
```

Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add tests/smoke_test_linux.py
git commit -m "test: add manual Linux smoke test for transport refactor"
```

---

## Task 8: Update CLAUDE.md and MEMORY.md notes

**Files:**
- Modify: `CLAUDE.md` (add note about the new transport module)
- Modify: `/home/roska/.claude/projects/-home-roska-Documentos-FL-MCP/memory/MEMORY.md` (update architecture section)

- [ ] **Step 1: Update `CLAUDE.md`**

Use the Edit tool. Find this block in `CLAUDE.md`:

```markdown
### Transporte MIDI
- Escritura directa a `/dev/snd/midiC0D0` (bytes crudos)
- **NO usar** mido (falla con Wine ALSA) ni amidi subprocess (demasiado lento)
- Conexión: `aconnect` VirMIDI 0-0 → WINE ALSA Input
```

Replace with:

```markdown
### Transporte MIDI
- Abstracción cross-platform en `knowledge/midi_transport.py`:
  - **Linux**: `LinuxRawTransport` → escritura directa a `/dev/snd/midiC0D0`
  - **Windows**: `WindowsRtmidiTransport` → `python-rtmidi` al puerto virtual `FL_MCP` (creado por loopMIDI)
- `trigger.py` usa `create_transport()` que detecta plataforma vía `sys.platform`
- **NO usar** mido (falla con Wine ALSA) ni amidi subprocess (demasiado lento)
- Conexión Linux: `aconnect` VirMIDI 0-0 → WINE ALSA Input
- Tests: `pytest tests/test_midi_transport.py` (mocks rtmidi y open() — corre en cualquier plataforma)
```

- [ ] **Step 2: Update the memory file architecture section**

Use the Edit tool on `/home/roska/.claude/projects/-home-roska-Documentos-FL-MCP/memory/MEMORY.md`. Find:

```markdown
- MIDI transport: Direct write to `/dev/snd/midiC0D0` (NOT mido, NOT amidi subprocess)
- mido doesn't work reliably through Wine ALSA, amidi subprocess too slow for timing
- VirMIDI 0-0 → WINE ALSA Input connection via `aconnect`
```

Replace with:

```markdown
- MIDI transport: cross-platform abstraction in `knowledge/midi_transport.py`
  - Linux: `LinuxRawTransport` writes raw bytes to `/dev/snd/midiC0D0`
  - Windows: `WindowsRtmidiTransport` uses python-rtmidi → virtual port "FL_MCP" (loopMIDI)
  - `create_transport()` factory picks based on `sys.platform`
- mido doesn't work reliably through Wine ALSA, amidi subprocess too slow for timing
- VirMIDI 0-0 → WINE ALSA Input connection via `aconnect` (Linux only)
- Tests: pytest tests/test_midi_transport.py (uses fixtures from tests/conftest.py)
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md to reflect cross-platform MIDI transport"
```

(Note: `MEMORY.md` lives outside the repo in `~/.claude/...` and is not tracked by git. The Edit just updates it in place — no commit needed.)

---

## Done — what you should have at the end

- 14 passing unit tests covering all transports + the factory
- `knowledge/midi_transport.py` with `MidiTransport` protocol, `LinuxRawTransport`, `WindowsRtmidiTransport`, and `create_transport()`
- `trigger.py` lines 88-95 refactored to use the new module — Linux behavior bit-for-bit identical
- `tests/smoke_test_linux.py` for manual end-to-end verification
- `CLAUDE.md` and `MEMORY.md` updated
- 7 small commits, each independently revertible

## Verification checklist before declaring done

- [ ] `pytest` reports 14 PASS, 0 FAIL
- [ ] `python -c "import trigger"` succeeds on Linux (FL Studio running)
- [ ] `tests/smoke_test_linux.py` plays a note in FL Studio (manual)
- [ ] `git log --oneline` shows 7 new commits
