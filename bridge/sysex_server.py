"""FL-Studio-side SysEx bridge server.

This module is imported INSIDE FL Studio's script. It is NOT a long-running
server like the old TCP version — it's a stateless message dispatcher fed
from FL's OnSysEx(event) callback. The script must:

    server = SysExServer(device_module=device)
    # in OnSysEx:
    server.feed_packet(bytes(event.sysex))
    # in OnIdle:
    server.drain_once(registry)

There's no threading because FL Studio's sandbox blocks daemon threads.
All dispatch happens on FL's main thread via OnIdle drain — same pattern
as the TCP version.
"""
from __future__ import annotations
from queue import Queue, Empty
from typing import Any

from bridge.sysex_protocol import (
    encode_dict, unpack_packet, decode_payload,
    Reassembler, SysExProtocolError,
)

__all__ = ["SysExServer"]


class SysExServer:
    """SysEx-based bridge endpoint for the FL-Studio side.

    `device_module` is FL's `device` module (or a fake for tests). It only
    needs a `midiOutSysex(message: bytes)` method.
    """

    def __init__(self, device_module: Any) -> None:
        self._device = device_module
        self._reassembler = Reassembler()
        self._seq = 0
        self.pending_requests: Queue = Queue()

    def feed_packet(self, raw: bytes) -> None:
        """Called from OnSysEx(event) with the SysEx bytes (incl. F0..F7).
        Reassembles multi-chunk messages and enqueues complete requests.
        """
        try:
            unpacked = unpack_packet(raw)
        except SysExProtocolError:
            return  # not our protocol; ignore silently
        completed = self._reassembler.feed(unpacked)
        if completed is None:
            return
        try:
            msg = decode_payload(completed)
        except SysExProtocolError:
            return
        if msg.get("type") == "req":
            self.pending_requests.put(msg)

    def send_message(self, msg: dict) -> None:
        """Pack a dict into SysEx and emit via device.midiOutSysex.
        Used internally by drain_once and externally for unsolicited events.
        """
        self._seq = (self._seq + 1) & 0x3FFF
        for packet in encode_dict(self._seq, msg):
            self._device.midiOutSysex(bytes(packet))

    def drain_once(self, registry: Any, max_per_call: int = 8) -> int:
        """Process up to `max_per_call` pending requests, dispatching each
        through `registry` and sending the response via SysEx.
        """
        from bridge.handlers import HandlerError
        processed = 0
        for _ in range(max_per_call):
            try:
                request = self.pending_requests.get_nowait()
            except Empty:
                break
            request_id = request.get("id", "")
            method = request.get("method", "")
            params = request.get("params") or {}
            try:
                result = registry.dispatch(method, params)
                self.send_message({"type": "res", "id": request_id, "ok": True, "result": result})
            except HandlerError as exc:
                self.send_message({"type": "res", "id": request_id, "ok": False, "error": str(exc)})
            except Exception as exc:
                self.send_message({"type": "res", "id": request_id, "ok": False, "error": f"internal: {exc}"})
            processed += 1
        return processed
