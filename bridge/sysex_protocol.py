"""SysEx wire protocol for FL Studio bridge.

Encodes JSON messages as SysEx packets:
    F0 7D 00 01 <SEQ_HI> <SEQ_LO> <CHUNK_IDX> <CHUNK_CNT> <PAYLOAD...> F7

All bytes inside the SysEx body (between F0/F7) must be 0-127 (data bytes).
The payload is the JSON serialized with ensure_ascii=True so it's pure ASCII.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass

__all__ = [
    "MFG_ID", "MAGIC", "MAX_PAYLOAD", "HEADER_SIZE",
    "pack_message", "unpack_packet",
    "Unpacked", "Reassembler",
    "encode_dict", "decode_payload",
    "SysExProtocolError",
]

MFG_ID = 0x7D            # Non-commercial / educational manufacturer ID
MAGIC = bytes([0x00, 0x01])  # FL_MCP signature
HEADER_SIZE = 8          # F0 + MFG + MAGIC(2) + SEQ(2) + IDX + CNT
TAIL_SIZE = 1            # F7
SYSEX_MAX = 1024
MAX_PAYLOAD = SYSEX_MAX - HEADER_SIZE - TAIL_SIZE  # 1015 worst-case


class SysExProtocolError(Exception):
    """Raised when packing/unpacking a SysEx packet fails."""


@dataclass(frozen=True)
class Unpacked:
    seq: int
    chunk_idx: int
    chunk_cnt: int
    payload: bytes


def pack_message(seq: int, payload: bytes) -> list[bytes]:
    """Pack a payload into one or more SysEx chunks.

    `payload` must be ASCII (all bytes 0-127). Use json.dumps(...,
    ensure_ascii=True) before passing.

    Returns a list of SysEx packets, each ending with F7. The caller
    transmits them in order.
    """
    if seq < 0 or seq > 0x3FFF:
        raise SysExProtocolError(f"seq must fit in 14 bits (got {seq})")
    for b in payload:
        if b > 0x7F:
            raise SysExProtocolError(
                "payload contains non-ASCII byte; use ensure_ascii=True"
            )

    if len(payload) == 0:
        chunks_data = [b'']
    else:
        chunks_data = [
            payload[i:i + MAX_PAYLOAD]
            for i in range(0, len(payload), MAX_PAYLOAD)
        ]

    total = len(chunks_data)
    if total > 128:
        raise SysExProtocolError(f"message too large: {total} chunks (max 128)")

    seq_hi = (seq >> 7) & 0x7F
    seq_lo = seq & 0x7F

    packets: list[bytes] = []
    for idx, chunk in enumerate(chunks_data):
        packet = (
            bytes([0xF0, MFG_ID])
            + MAGIC
            + bytes([seq_hi, seq_lo, idx, total])
            + chunk
            + bytes([0xF7])
        )
        packets.append(packet)
    return packets


def unpack_packet(packet: bytes) -> Unpacked:
    """Validate and parse a SysEx packet emitted by pack_message.

    Raises SysExProtocolError on any framing problem.
    """
    if not packet or packet[0] != 0xF0:
        raise SysExProtocolError("missing F0 start byte")
    if len(packet) < HEADER_SIZE + TAIL_SIZE:
        raise SysExProtocolError(f"too short: {len(packet)} bytes")
    if packet[-1] != 0xF7:
        raise SysExProtocolError("missing F7 end byte")
    if packet[1] != MFG_ID:
        raise SysExProtocolError(f"wrong manufacturer id: 0x{packet[1]:02x}")
    if packet[2:4] != MAGIC:
        raise SysExProtocolError(f"bad magic: {packet[2:4]!r}")
    seq_hi = packet[4]
    seq_lo = packet[5]
    seq = (seq_hi << 7) | seq_lo
    chunk_idx = packet[6]
    chunk_cnt = packet[7]
    payload = packet[8:-1]
    return Unpacked(seq=seq, chunk_idx=chunk_idx, chunk_cnt=chunk_cnt, payload=bytes(payload))


class Reassembler:
    """Accumulates chunks of multi-packet SysEx messages.

    `feed(unpacked)` returns the complete payload bytes when the last chunk
    arrives, else None. Single-chunk messages return immediately.

    Sequences older than `ttl_seconds` (default 5s) get discarded silently
    to avoid memory leaks if chunks get lost.
    """

    def __init__(self, ttl_seconds: float = 5.0) -> None:
        self._pending: dict[int, dict] = {}
        self._ttl = ttl_seconds

    def feed(self, packet: Unpacked) -> bytes | None:
        self._gc()
        if packet.chunk_cnt == 1:
            return packet.payload
        entry = self._pending.setdefault(
            packet.seq,
            {"chunks": {}, "cnt": packet.chunk_cnt, "ts": time.monotonic()},
        )
        entry["ts"] = time.monotonic()
        entry["chunks"][packet.chunk_idx] = packet.payload
        if len(entry["chunks"]) == packet.chunk_cnt:
            ordered = b"".join(entry["chunks"][i] for i in range(packet.chunk_cnt))
            del self._pending[packet.seq]
            return ordered
        return None

    def _gc(self) -> None:
        now = time.monotonic()
        expired = [seq for seq, e in self._pending.items() if now - e["ts"] > self._ttl]
        for seq in expired:
            del self._pending[seq]


def encode_dict(seq: int, message: dict) -> list[bytes]:
    """Serialize a dict as JSON (ensure_ascii=True) and pack into SysEx packets."""
    payload = json.dumps(message, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return pack_message(seq=seq, payload=payload)


def decode_payload(payload: bytes) -> dict:
    """Parse a reassembled payload as JSON. Raises SysExProtocolError on failure."""
    try:
        text = payload.decode("ascii")
    except UnicodeDecodeError as exc:
        raise SysExProtocolError(f"payload not ascii: {exc}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise SysExProtocolError(f"invalid json: {exc}") from exc
