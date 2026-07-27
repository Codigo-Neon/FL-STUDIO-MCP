"""Tests for the Linux-side SysEx client (python-rtmidi)."""
import threading
import time
import pytest
from unittest.mock import MagicMock
from bridge.sysex_client import SysExClient, SysExBridgeError


def make_fake_rtmidi():
    """Build a fake rtmidi module with MidiIn / MidiOut."""
    fake = MagicMock()
    midi_in_inst = MagicMock()
    midi_out_inst = MagicMock()
    fake.MidiIn.return_value = midi_in_inst
    fake.MidiOut.return_value = midi_out_inst
    midi_in_inst.get_ports.return_value = ["FL_MCP_OUT 0"]   # FL writes here
    midi_out_inst.get_ports.return_value = ["FL_MCP_IN 0"]   # FL reads here
    midi_in_inst._captured_callback = None
    def set_callback(cb, data=None):
        midi_in_inst._captured_callback = cb
    midi_in_inst.set_callback.side_effect = set_callback
    midi_in_inst.ignore_types.return_value = None
    return fake, midi_in_inst, midi_out_inst


class TestSysExClientLifecycle:
    def test_connect_opens_both_ports(self, monkeypatch):
        fake, mi, mo = make_fake_rtmidi()
        monkeypatch.setattr("bridge.sysex_client.rtmidi", fake)
        c = SysExClient(in_port_name="FL_MCP_OUT", out_port_name="FL_MCP_IN")
        c.connect()
        mi.open_port.assert_called_once_with(0)
        mo.open_port.assert_called_once_with(0)
        mi.set_callback.assert_called_once()
        mi.ignore_types.assert_called_once_with(sysex=False, timing=True, active_sense=True)
        c.close()

    def test_connect_raises_if_in_port_missing(self, monkeypatch):
        fake, mi, mo = make_fake_rtmidi()
        mi.get_ports.return_value = []
        monkeypatch.setattr("bridge.sysex_client.rtmidi", fake)
        c = SysExClient(in_port_name="FL_MCP_OUT", out_port_name="FL_MCP_IN")
        with pytest.raises(SysExBridgeError, match="input port"):
            c.connect()


class TestSysExClientRequest:
    def test_request_sends_sysex_and_waits(self, monkeypatch):
        from bridge.sysex_protocol import encode_dict, unpack_packet, decode_payload
        fake, mi, mo = make_fake_rtmidi()
        monkeypatch.setattr("bridge.sysex_client.rtmidi", fake)
        c = SysExClient(in_port_name="FL_MCP_OUT", out_port_name="FL_MCP_IN")
        c.connect()
        # Background thread simulates FL responding to whatever client sends.
        def respond():
            time.sleep(0.05)
            sent_call = mo.send_message.call_args
            sent_bytes = bytes(sent_call.args[0])
            req = decode_payload(unpack_packet(sent_bytes).payload)
            resp = {"type": "res", "id": req["id"], "ok": True, "result": {"pong": True}}
            packets = encode_dict(seq=999, message=resp)
            for p in packets:
                mi._captured_callback((list(p), 0.0), None)
        threading.Thread(target=respond, daemon=True).start()
        result = c.request("ping", timeout=1.0)
        assert result == {"pong": True}
        c.close()

    def test_request_timeout(self, monkeypatch):
        fake, mi, mo = make_fake_rtmidi()
        monkeypatch.setattr("bridge.sysex_client.rtmidi", fake)
        c = SysExClient(in_port_name="FL_MCP_OUT", out_port_name="FL_MCP_IN")
        c.connect()
        with pytest.raises(SysExBridgeError, match="timeout"):
            c.request("any", timeout=0.2)
        c.close()
