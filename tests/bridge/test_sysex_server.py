from bridge.sysex_server import SysExServer
from bridge.sysex_protocol import unpack_packet, decode_payload, Reassembler


class FakeDevice:
    def __init__(self):
        self.sent = []

    def midiOutSysex(self, message):
        self.sent.append(bytes(message))


class TestSendEvent:
    def test_send_event_emits_decodable_evt_message(self):
        dev = FakeDevice()
        server = SysExServer(device_module=dev)
        server.send_event("bpm", {"bpm": 140})
        assert len(dev.sent) == 1
        reasm = Reassembler()
        msg = decode_payload(reasm.feed(unpack_packet(dev.sent[0])))
        assert msg == {"type": "evt", "name": "bpm", "data": {"bpm": 140}}
