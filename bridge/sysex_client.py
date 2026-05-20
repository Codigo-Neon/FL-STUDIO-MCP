"""Linux-side SysEx bridge client.

Both directions use the raw ALSA MIDI device (/dev/snd/midiC0D0) because
python-rtmidi's ALSA Sequencer routing drops SysEx packets when one of
the endpoints is Wine — observed empirically with FL Studio 2024.

OUTPUT (Linux → FL): plain write() to the device fd.
INPUT (FL → Linux): a daemon thread does blocking read() on a second fd
    and reassembles SysEx packets (delimited by F0..F7).
"""
from __future__ import annotations
import os
import threading
import uuid
from queue import Queue, Empty
from typing import Callable

from bridge.sysex_protocol import (
    encode_dict, unpack_packet, decode_payload,
    Reassembler, SysExProtocolError,
)

__all__ = ["SysExClient", "SysExBridgeError"]


class SysExBridgeError(Exception):
    """Raised by SysExClient on connect/request failures."""


class SysExClient:
    """SysEx bridge client speaking the FL_MCP protocol.

    Thread-safe: `request()` may be called from any thread. Responses are
    correlated by the `id` field of the JSON envelope (set automatically).
    """

    def __init__(self, raw_device: str = "/dev/snd/midiC0D0") -> None:
        self._raw_device = raw_device
        self._fd_out: int | None = None
        self._fd_in: int | None = None
        self._reader_thread: threading.Thread | None = None
        self._reassembler = Reassembler()
        self._waiters: dict[str, Queue] = {}
        self._waiters_lock = threading.Lock()
        self._event_callbacks: list[Callable[[str, dict], None]] = []
        self._seq = 0
        self._seq_lock = threading.Lock()
        self._closed = False

    def connect(self) -> None:
        try:
            self._fd_out = os.open(self._raw_device, os.O_WRONLY)
        except OSError as exc:
            raise SysExBridgeError(
                f"could not open {self._raw_device!r} for write: {exc}"
            )
        try:
            self._fd_in = os.open(self._raw_device, os.O_RDONLY)
        except OSError as exc:
            os.close(self._fd_out)
            self._fd_out = None
            raise SysExBridgeError(
                f"could not open {self._raw_device!r} for read: {exc}"
            )
        self._reader_thread = threading.Thread(
            target=self._read_loop, name="SysExClient-reader", daemon=True
        )
        self._reader_thread.start()

    def request(self, method: str, params: dict | None = None, timeout: float = 5.0) -> dict:
        if self._closed:
            raise SysExBridgeError("client closed")
        if self._fd_out is None:
            raise SysExBridgeError("client not connected")
        request_id = uuid.uuid4().hex[:12]
        msg = {"type": "req", "id": request_id, "method": method, "params": params or {}}
        queue: Queue = Queue(maxsize=1)
        with self._waiters_lock:
            self._waiters[request_id] = queue
        try:
            with self._seq_lock:
                seq = self._seq
                self._seq = (self._seq + 1) & 0x3FFF
            for packet in encode_dict(seq, msg):
                os.write(self._fd_out, bytes(packet))
            try:
                response = queue.get(timeout=timeout)
            except Empty:
                raise SysExBridgeError(f"request {method!r} timeout after {timeout}s")
        finally:
            with self._waiters_lock:
                self._waiters.pop(request_id, None)
        if not response.get("ok"):
            raise SysExBridgeError(response.get("error", "unknown error"))
        return response.get("result")

    def on_event(self, callback: Callable[[str, dict], None]) -> None:
        self._event_callbacks.append(callback)

    def close(self) -> None:
        self._closed = True
        if self._fd_in is not None:
            try:
                os.close(self._fd_in)
            except OSError:
                pass
            self._fd_in = None
        if self._fd_out is not None:
            try:
                os.close(self._fd_out)
            except OSError:
                pass
            self._fd_out = None

    def _read_loop(self) -> None:
        """Read raw bytes from the MIDI device, slice into SysEx packets,
        and dispatch each complete packet."""
        buf = bytearray()
        in_sysex = False
        fd = self._fd_in
        while not self._closed and fd is not None:
            try:
                chunk = os.read(fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            for byte in chunk:
                if byte == 0xF0:
                    buf = bytearray([0xF0])
                    in_sysex = True
                elif in_sysex:
                    buf.append(byte)
                    if byte == 0xF7:
                        self._handle_packet(bytes(buf))
                        buf = bytearray()
                        in_sysex = False
                # bytes outside an active F0..F7 frame are non-SysEx; ignore

    def _handle_packet(self, raw: bytes) -> None:
        try:
            unpacked = unpack_packet(raw)
        except SysExProtocolError:
            return  # not our protocol
        completed = self._reassembler.feed(unpacked)
        if completed is None:
            return
        try:
            msg = decode_payload(completed)
        except SysExProtocolError:
            return
        msg_type = msg.get("type")
        if msg_type == "req":
            # Our own outgoing echoed back via virmidi loopback; ignore.
            return
        if msg_type == "res":
            request_id = msg.get("id")
            with self._waiters_lock:
                q = self._waiters.get(request_id)
            if q is not None:
                q.put(msg)
        elif msg_type == "evt":
            name = msg.get("name", "")
            data = msg.get("data", {})
            for cb in list(self._event_callbacks):
                try:
                    cb(name, data)
                except Exception:
                    pass

    def is_connected(self) -> bool:
        return self._fd_out is not None and self._fd_in is not None and not self._closed
