"""Tests for the cross-platform MIDI transport layer."""
from knowledge.midi_transport import MidiTransport


class TestMidiTransportProtocol:
    def test_protocol_has_send_method(self):
        assert hasattr(MidiTransport, "send")

    def test_protocol_has_close_method(self):
        assert hasattr(MidiTransport, "close")
