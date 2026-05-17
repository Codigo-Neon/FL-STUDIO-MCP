"""Linux-side bridge client. Connects to FL Studio script over TCP."""
from __future__ import annotations
import socket
import threading
import time
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

    When `auto_reconnect=True`, the reader loop transparently reopens the
    socket on disconnect with exponential backoff starting at
    `reconnect_initial_delay` seconds, doubling per attempt, capped at
    `reconnect_max_delay`. Pending requests are failed with "connection lost"
    during the disconnect window; if a request was issued during reconnect
    it waits on `_connected` up to min(timeout, 2.0) seconds before failing.

    Malformed frames (ProtocolError) are skipped silently by the reader; any
    in-flight request whose response frame was malformed will time out.
    """

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        connect_timeout: float = 2.0,
        auto_reconnect: bool = False,
        reconnect_initial_delay: float = 0.5,
        reconnect_max_delay: float = 30.0,
    ) -> None:
        self._host = host
        self._port = port
        self._connect_timeout = connect_timeout
        self._auto_reconnect = auto_reconnect
        self._reconnect_initial_delay = reconnect_initial_delay
        self._reconnect_max_delay = reconnect_max_delay
        self._sock: socket.socket | None = None
        self._stream = None
        self._reader_thread: threading.Thread | None = None
        self._waiters: dict[str, Queue] = {}
        self._waiters_lock = threading.Lock()
        self._event_callbacks: list[Callable[[str, dict], None]] = []
        self._closed = threading.Event()
        self._connected = threading.Event()
        self._write_lock = threading.Lock()

    def connect(self) -> None:
        if self._reader_thread is not None and self._reader_thread.is_alive():
            raise BridgeError("already connected; call close() first")
        self._open_socket()
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()

    def _open_socket(self) -> None:
        # Close any stale socket/stream from a previous attempt (reconnect path).
        if self._stream is not None:
            try:
                self._stream.close()
            except OSError:
                pass
            self._stream = None
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        try:
            self._sock = socket.create_connection((self._host, self._port), timeout=self._connect_timeout)
        except OSError as exc:
            raise BridgeError(f"connect failed: {exc}") from exc
        self._sock.settimeout(None)
        self._stream = self._sock.makefile("rwb", buffering=0)
        self._connected.set()

    def is_connected(self) -> bool:
        return self._connected.is_set() and not self._closed.is_set()

    def request(self, method: str, params: dict | None = None, timeout: float = 5.0) -> dict:
        if self._closed.is_set():
            raise BridgeError("client closed")
        deadline = time.monotonic() + timeout
        while True:
            # If we're mid-reconnect, give the reader a moment to re-establish.
            if not self._connected.is_set():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise BridgeError("not connected")
                if not self._connected.wait(timeout=min(remaining, 2.0)):
                    raise BridgeError("not connected")
            if self._closed.is_set():
                raise BridgeError("client closed")
            request_id = uuid.uuid4().hex[:12]
            queue: Queue = Queue(maxsize=1)
            with self._waiters_lock:
                self._waiters[request_id] = queue
            try:
                line = encode(make_request(request_id, method, params)).encode("utf-8")
                try:
                    with self._write_lock:
                        if self._stream is None:
                            raise BridgeError("stream closed")
                        self._stream.write(line)
                except OSError as exc:
                    raise BridgeError(f"write failed: {exc}") from exc
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise BridgeError(f"request '{method}' timeout after {timeout}s")
                try:
                    response = queue.get(timeout=remaining)
                except Empty:
                    raise BridgeError(f"request '{method}' timeout after {timeout}s")
            finally:
                with self._waiters_lock:
                    self._waiters.pop(request_id, None)
            # If the connection dropped while waiting, retry if auto_reconnect is on.
            if (
                not response.get("ok")
                and response.get("error") == "connection lost"
                and self._auto_reconnect
                and not self._closed.is_set()
            ):
                continue
            if not response.get("ok"):
                raise BridgeError(response.get("error", "unknown error"))
            return response.get("result")

    def on_event(self, callback: Callable[[str, dict], None]) -> None:
        """Register a callback invoked from the reader thread for every event."""
        self._event_callbacks.append(callback)

    def close(self) -> None:
        self._closed.set()
        self._connected.clear()
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
        if self._reader_thread is not None:
            self._reader_thread.join(timeout=2.0)

    def _reader_loop(self) -> None:
        delay = self._reconnect_initial_delay
        while not self._closed.is_set():
            reader = FrameReader(self._stream)
            try:
                while not self._closed.is_set():
                    try:
                        msg = reader.read_message()
                    except ProtocolError:
                        continue
                    if msg is None:
                        break
                    self._dispatch(msg)
            except OSError:
                pass
            self._connected.clear()
            self._fail_pending_requests("connection lost")
            if not self._auto_reconnect or self._closed.is_set():
                break
            time.sleep(delay)
            delay = min(delay * 2, self._reconnect_max_delay)
            try:
                self._open_socket()
                delay = self._reconnect_initial_delay  # reset on success
            except BridgeError:
                continue

    def _fail_pending_requests(self, reason: str) -> None:
        from bridge.protocol import make_response_error
        with self._waiters_lock:
            waiters = dict(self._waiters)
            self._waiters.clear()
        for request_id, queue in waiters.items():
            try:
                queue.put_nowait(make_response_error(request_id, reason))
            except Exception:
                pass

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
