"""Tests for the Linux-side SysEx client.

The client talks to the raw ALSA MIDI device with os.open/os.write/os.read
(python-rtmidi drops SysEx through Wine — see bridge/sysex_client.py). These
tests stand in a pair of real pipes for the device so the actual read loop,
framing, and reassembly code runs unmodified.
"""
import os
import threading

import pytest

from bridge.sysex_client import SysExClient, SysExBridgeError
from bridge.sysex_protocol import (
    Reassembler,
    decode_payload,
    encode_dict,
    unpack_packet,
)


class FakeDevice:
    """Stands in for /dev/snd/midiC0D0 using two pipes.

    The client opens the path twice (O_WRONLY then O_RDONLY); we hand it one
    end of each pipe and keep the other end for the test to drive.
    """

    def __init__(self, monkeypatch, fail_on=None):
        self._to_fl_r, self.client_out = os.pipe()
        self.client_in, self._from_fl_w = os.pipe()
        self.opened_flags = []
        self._reassembler = Reassembler()
        real_open = os.open

        def fake_open(path, flags, *a, **kw):
            if path != "/dev/snd/midiC0D0":
                return real_open(path, flags, *a, **kw)
            self.opened_flags.append(flags)
            if fail_on == "write" and flags == os.O_WRONLY:
                raise OSError(2, "No such device")
            if fail_on == "read" and flags == os.O_RDONLY:
                raise OSError(2, "No such device")
            return self.client_out if flags == os.O_WRONLY else self.client_in

        monkeypatch.setattr(os, "open", fake_open)

    def read_message(self):
        """Read one complete SysEx frame the client wrote, decoded to a dict."""
        buf = bytearray()
        while True:
            byte = os.read(self._to_fl_r, 1)
            if not byte:
                raise AssertionError("device closed before a full frame arrived")
            if byte[0] == 0xF0:
                buf = bytearray([0xF0])
            elif buf:
                buf.append(byte[0])
                if byte[0] == 0xF7:
                    payload = self._reassembler.feed(unpack_packet(bytes(buf)))
                    if payload is not None:
                        return decode_payload(payload)
                    buf = bytearray()

    def send(self, message, seq=0):
        """Push a message toward the client, as FL Studio would."""
        for packet in encode_dict(seq, message):
            os.write(self._from_fl_w, bytes(packet))

    def cleanup(self):
        for fd in (self._to_fl_r, self._from_fl_w):
            try:
                os.close(fd)
            except OSError:
                pass


@pytest.fixture
def device(monkeypatch):
    dev = FakeDevice(monkeypatch)
    yield dev
    dev.cleanup()


@pytest.fixture
def client(device):
    c = SysExClient()
    c.connect()
    yield c
    c.close()


class TestSysExClientLifecycle:
    def test_connect_opens_device_for_read_and_write(self, device):
        c = SysExClient()
        c.connect()
        try:
            assert device.opened_flags == [os.O_WRONLY, os.O_RDONLY]
            assert c.is_connected() is True
        finally:
            c.close()

    def test_connect_raises_when_device_cannot_be_opened_for_write(self, monkeypatch):
        dev = FakeDevice(monkeypatch, fail_on="write")
        try:
            with pytest.raises(SysExBridgeError, match="for write"):
                SysExClient().connect()
        finally:
            dev.cleanup()

    def test_connect_releases_write_fd_when_read_open_fails(self, monkeypatch):
        dev = FakeDevice(monkeypatch, fail_on="read")
        try:
            c = SysExClient()
            with pytest.raises(SysExBridgeError, match="for read"):
                c.connect()
            # The write fd must not stay half-open when the second open fails.
            assert c.is_connected() is False
        finally:
            dev.cleanup()

    def test_close_marks_client_disconnected(self, device):
        c = SysExClient()
        c.connect()
        c.close()
        assert c.is_connected() is False

    def test_request_before_connect_raises(self):
        with pytest.raises(SysExBridgeError, match="not connected"):
            SysExClient().request("ping")

    def test_request_after_close_raises(self, device):
        c = SysExClient()
        c.connect()
        c.close()
        with pytest.raises(SysExBridgeError, match="closed"):
            c.request("ping")


class TestSysExClientRequest:
    def _respond(self, device, client, method, response_builder, timeout=5.0):
        """Run `request` in a thread, answer it from the device side, and
        return (box, sent) where box holds "result" or "error"."""
        box = {}

        def run():
            try:
                box["result"] = client.request(method, timeout=timeout)
            except Exception as exc:  # noqa: BLE001 - inspected by the caller
                box["error"] = exc

        t = threading.Thread(target=run)
        t.start()
        sent = device.read_message()
        device.send(response_builder(sent))
        t.join(timeout=5.0)
        assert not t.is_alive(), "request did not return"
        return box, sent

    def test_request_sends_well_formed_envelope(self, device, client):
        box, sent = self._respond(
            device, client, "ping",
            lambda req: {"type": "res", "id": req["id"], "ok": True,
                         "result": {"pong": True}},
        )
        assert sent["type"] == "req"
        assert sent["method"] == "ping"
        assert sent["params"] == {}
        assert sent["id"]
        assert box["result"] == {"pong": True}

    def test_request_returns_result_payload(self, device, client):
        box, _ = self._respond(
            device, client, "get_fl_state",
            lambda req: {
                "type": "res", "id": req["id"], "ok": True,
                "result": {"bpm": 140, "current_pattern": 3},
            },
        )
        assert box["result"] == {"bpm": 140, "current_pattern": 3}

    def test_request_raises_on_error_response(self, device, client):
        box, _ = self._respond(
            device, client, "explode",
            lambda req: {"type": "res", "id": req["id"], "ok": False,
                         "error": "boom"},
        )
        assert isinstance(box.get("error"), SysExBridgeError)
        assert "boom" in str(box["error"])

    def test_response_with_mismatched_id_is_ignored(self, device, client):
        """A stale response must not satisfy a pending request."""
        box, _ = self._respond(
            device, client, "ping",
            lambda req: {"type": "res", "id": "not-the-id", "ok": True, "result": {}},
            timeout=0.4,
        )
        assert isinstance(box.get("error"), SysExBridgeError)
        assert "timeout" in str(box["error"])

    def test_request_times_out_when_no_response(self, client):
        with pytest.raises(SysExBridgeError, match="timeout"):
            client.request("ping", timeout=0.2)

    def test_concurrent_requests_are_correlated_by_id(self, device, client):
        """Two in-flight requests answered out of order each get their own result."""
        results = {}

        def call(name):
            results[name] = client.request(name, timeout=5.0)

        t1 = threading.Thread(target=call, args=("first",))
        t2 = threading.Thread(target=call, args=("second",))
        t1.start()
        req_a = device.read_message()
        t2.start()
        req_b = device.read_message()

        # Answer in reverse order.
        device.send({"type": "res", "id": req_b["id"], "ok": True,
                     "result": {"who": req_b["method"]}}, seq=1)
        device.send({"type": "res", "id": req_a["id"], "ok": True,
                     "result": {"who": req_a["method"]}}, seq=2)

        t1.join(timeout=5.0)
        t2.join(timeout=5.0)
        assert results == {"first": {"who": "first"}, "second": {"who": "second"}}


class TestSysExClientEvents:
    def test_event_callback_receives_name_and_data(self, device, client):
        seen = threading.Event()
        got = {}

        def on_event(name, data):
            got["name"] = name
            got["data"] = data
            seen.set()

        client.on_event(on_event)
        device.send({"type": "evt", "name": "bpm_changed", "data": {"bpm": 92}})

        assert seen.wait(timeout=5.0), "event callback never fired"
        assert got["name"] == "bpm_changed"
        assert got["data"] == {"bpm": 92}

    def test_callback_exception_does_not_stop_later_callbacks(self, device, client):
        second = threading.Event()

        def raising(name, data):
            raise RuntimeError("bad handler")

        client.on_event(raising)
        client.on_event(lambda name, data: second.set())

        device.send({"type": "evt", "name": "pattern_changed", "data": {"index": 2}})

        assert second.wait(timeout=5.0), "a raising callback stopped later callbacks"

    def test_echoed_request_is_ignored(self, device, client):
        """VirMIDI loopback echoes our own outgoing frames back; they must not
        be dispatched as events."""
        fired = threading.Event()
        client.on_event(lambda name, data: fired.set())
        device.send({"type": "req", "id": "abc", "method": "ping", "params": {}})
        assert not fired.wait(timeout=0.4)

    def test_malformed_frame_does_not_kill_reader(self, device, client):
        """Garbage on the wire must not stop later, valid traffic."""
        fired = threading.Event()
        client.on_event(lambda name, data: fired.set())
        # Wrong manufacturer ID (0x7E instead of 0x7D) -> not our protocol.
        os.write(device._from_fl_w, bytes([0xF0, 0x7E, 0x00, 0x01, 0x00, 0xF7]))
        device.send({"type": "evt", "name": "ok_after_garbage", "data": {}})
        assert fired.wait(timeout=5.0), "reader died on a malformed frame"
