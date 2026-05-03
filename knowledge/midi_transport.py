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
