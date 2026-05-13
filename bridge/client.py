"""Linux-side bridge client. Connects to FL Studio script over TCP."""
from __future__ import annotations
import socket
import threading
import uuid
from queue import Queue, Empty
from typing import Callable

from bridge.protocol import (
    DEFAULT_HOST, DEFAULT_PORT,
    encode, FrameReader,
    make_request,
    ProtocolError,
)

__all__ = ["BridgeClient", "BridgeError"]


class BridgeError(Exception):
    """Raised when the bridge fails to connect, times out, or returns an error."""


class BridgeClient:
    """Persistent TCP client to the FL Studio bridge server.

    Thread-safe: `request()` may be called from any thread; a single
    background reader thread distributes responses to waiters via per-request
    queues keyed by request id.

    Reconnection is NOT automatic in v1 — explicit `connect()` and `close()`.
    Reconnect-on-failure is added in a later task.
    """

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        connect_timeout: float = 2.0,
    ) -> None:
        self._host = host
        self._port = port
        self._connect_timeout = connect_timeout
        self._sock: socket.socket | None = None
        self._stream = None
        self._reader_thread: threading.Thread | None = None
        self._waiters: dict[str, Queue] = {}
        self._waiters_lock = threading.Lock()
        self._event_callbacks: list[Callable[[str, dict], None]] = []
        self._closed = threading.Event()

    def connect(self) -> None:
        try:
            self._sock = socket.create_connection(
                (self._host, self._port), timeout=self._connect_timeout
            )
        except OSError as exc:
            raise BridgeError(f"connect failed: {exc}") from exc
        self._sock.settimeout(None)
        self._stream = self._sock.makefile("rwb", buffering=0)
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()

    def is_connected(self) -> bool:
        return self._sock is not None and not self._closed.is_set()

    def request(self, method: str, params: dict | None = None, timeout: float = 5.0) -> dict:
        if not self.is_connected():
            raise BridgeError("not connected")
        request_id = uuid.uuid4().hex[:12]
        queue: Queue = Queue(maxsize=1)
        with self._waiters_lock:
            self._waiters[request_id] = queue
        try:
            self._stream.write(encode(make_request(request_id, method, params)).encode("utf-8"))
            try:
                response = queue.get(timeout=timeout)
            except Empty:
                raise BridgeError(f"request '{method}' timeout after {timeout}s")
        finally:
            with self._waiters_lock:
                self._waiters.pop(request_id, None)
        if not response.get("ok"):
            raise BridgeError(response.get("error", "unknown error"))
        return response.get("result")

    def on_event(self, callback: Callable[[str, dict], None]) -> None:
        """Register a callback invoked from the reader thread for every event."""
        self._event_callbacks.append(callback)

    def close(self) -> None:
        self._closed.set()
        if self._stream is not None:
            try:
                self._stream.close()
            except OSError:
                pass
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass

    def _reader_loop(self) -> None:
        reader = FrameReader(self._stream)
        try:
            while not self._closed.is_set():
                try:
                    msg = reader.read_message()
                except ProtocolError:
                    continue
                if msg is None:
                    break  # EOF
                self._dispatch(msg)
        finally:
            self._closed.set()

    def _dispatch(self, msg: dict) -> None:
        if msg.get("type") == "res":
            request_id = msg.get("id")
            with self._waiters_lock:
                queue = self._waiters.get(request_id)
            if queue is not None:
                queue.put(msg)
        elif msg.get("type") == "evt":
            name = msg.get("name", "")
            data = msg.get("data", {})
            for cb in list(self._event_callbacks):
                try:
                    cb(name, data)
                except Exception:
                    pass  # callback errors must not kill the reader
