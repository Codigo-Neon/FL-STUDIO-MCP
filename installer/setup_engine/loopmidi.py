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
