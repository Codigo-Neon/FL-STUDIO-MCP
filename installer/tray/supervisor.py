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
