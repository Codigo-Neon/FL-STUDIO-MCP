"""Tests for the cross-platform MIDI transport layer."""
from unittest.mock import MagicMock, call
from knowledge.midi_transport import MidiTransport, LinuxRawTransport


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
