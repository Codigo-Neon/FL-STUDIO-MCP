"""Tests for the cross-platform MIDI transport layer."""
from unittest.mock import MagicMock, call
import pytest
from knowledge.midi_transport import MidiTransport, LinuxRawTransport, WindowsRtmidiTransport


class TestMidiTransportProtocol:
    def test_protocol_has_send_method(self):
        assert hasattr(MidiTransport, "send")

    def test_protocol_has_close_method(self):
        assert hasattr(MidiTransport, "close")


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

    def test_first_match_wins_when_multiple_ports_match(self, mock_rtmidi):
        midi_out = mock_rtmidi.MidiOut.return_value
        midi_out.get_ports.return_value = ["FL_MCP 0", "FL_MCP Legacy 1"]

        WindowsRtmidiTransport(port_name="FL_MCP")

        midi_out.open_port.assert_called_once_with(0)
