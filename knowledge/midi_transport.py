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
