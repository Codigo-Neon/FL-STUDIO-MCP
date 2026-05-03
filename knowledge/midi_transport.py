"""Cross-platform MIDI transport abstraction.

The MCP server sends raw MIDI bytes to FL Studio. On Linux this means writing
directly to /dev/snd/midiC0D0; on Windows it means using python-rtmidi to send
to a virtual port created by loopMIDI. This module hides that difference.
"""
from typing import Protocol, runtime_checkable


@runtime_checkable
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
                return
        raise RuntimeError(f"MIDI port '{port_name}' not found")

    def send(self, data: bytes) -> None:
        self._out.send_message(list(data))

    def close(self) -> None:
        self._out.close_port()
