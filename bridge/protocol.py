"""Wire protocol between Linux MCP and FL Studio script.

Newline-delimited JSON over TCP. Three message types:

    req  — request from client to server
    res  — response from server to client (paired by `id`)
    evt  — event pushed from server, unsolicited

Both sides import this module. Keep dependencies to stdlib only so the
FL-side embedded Python can use it without any pip install.
"""
from __future__ import annotations
import json
from typing import Any

__all__ = [
    "DEFAULT_HOST", "DEFAULT_PORT",
    "make_request", "make_response_ok", "make_response_error", "make_event",
    "encode", "decode_line",
    "FrameReader",
    "ProtocolError",
]

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


class ProtocolError(Exception):
    """Raised when a wire message is malformed or unparseable."""


def make_request(request_id: str, method: str, params: dict | None = None) -> dict:
    return {"type": "req", "id": request_id, "method": method, "params": params or {}}


def make_response_ok(request_id: str, result: Any) -> dict:
    return {"type": "res", "id": request_id, "ok": True, "result": result}


def make_response_error(request_id: str, error: str) -> dict:
    return {"type": "res", "id": request_id, "ok": False, "error": error}


def make_event(name: str, data: dict) -> dict:
    return {"type": "evt", "name": name, "data": data}


def encode(message: dict) -> str:
    return json.dumps(message, separators=(",", ":")) + "\n"


def decode_line(line: str) -> dict:
    if not line or not line.strip():
        raise ProtocolError("empty line")
    try:
        msg = json.loads(line)
    except json.JSONDecodeError as exc:
        raise ProtocolError(f"invalid json: {exc}") from exc
    if not isinstance(msg, dict):
        raise ProtocolError("message must be a json object")
    if "type" not in msg:
        raise ProtocolError("missing 'type' field")
    return msg


class FrameReader:
    """Wrap a binary readable stream to yield JSONL messages.

    Returns None on EOF. Skips blank lines silently — they're not an error,
    they can appear if a writer accidentally double-newlines.
    """

    def __init__(self, stream) -> None:
        self._stream = stream

    def read_message(self) -> dict | None:
        while True:
            raw = self._stream.readline()
            if not raw:
                return None
            line = raw.decode("utf-8")
            if not line.strip():
                continue
            return decode_line(line)
