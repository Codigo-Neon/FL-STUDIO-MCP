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
