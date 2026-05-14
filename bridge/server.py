"""FL Studio-side bridge server.

CRITICAL: this module is imported by `device_test.py` which runs inside the
embedded Python 3.9 of FL Studio. Keep deps to stdlib only and avoid
asyncio — FL's script API doesn't play well with event loops in worker
threads.

The architecture is intentionally simple:

    accept thread  ──►  reader thread (per connection)  ──►  pending_requests Queue
    pending_requests Queue  ──►  consumer (FL main thread via OnIdle())
    consumer  ──►  send_message()  ──►  current client socket

`send_message` is the only API the FL handler dispatcher needs to push
either a response or an unsolicited event back to the client. There is
only ever one active client connection at a time (the MCP).
"""
from __future__ import annotations
import socket
import threading
from queue import Queue, Empty
from typing import Any

from bridge.protocol import (
    DEFAULT_HOST, DEFAULT_PORT,
    encode, FrameReader, ProtocolError,
)

__all__ = ["BridgeServer"]


class BridgeServer:
    """Single-client TCP server speaking JSONL bridge protocol.

    Lifecycle:
        s = BridgeServer(port=8765)
        s.start()              # spawns listener thread
        ...
        req = s.pending_requests.get(timeout=...)  # called from FL main thread
        s.send_message({...})                      # send response back
        ...
        s.stop()
    """

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
        self._host = host
        self._port = port
        self._listen_sock: socket.socket | None = None
        self._client_sock: socket.socket | None = None
        self._client_stream = None
        self._client_lock = threading.Lock()
        self._listen_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self.pending_requests: Queue = Queue()

    def start(self) -> None:
        if self._listen_thread is not None:
            return
        self._listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listen_sock.bind((self._host, self._port))
        self._listen_sock.listen(1)
        self._listen_sock.settimeout(0.5)  # allow stop_event check
        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listen_thread.start()

    def is_running(self) -> bool:
        return self._listen_thread is not None and not self._stop_event.is_set()

    def stop(self) -> None:
        self._stop_event.set()
        with self._client_lock:
            if self._client_stream is not None:
                try:
                    self._client_stream.close()
                except OSError:
                    pass
            if self._client_sock is not None:
                try:
                    self._client_sock.close()
                except OSError:
                    pass
            self._client_sock = None
            self._client_stream = None
        if self._listen_sock is not None:
            try:
                self._listen_sock.close()
            except OSError:
                pass
            self._listen_sock = None
        if self._listen_thread is not None:
            self._listen_thread.join(timeout=2.0)
        self._listen_thread = None

    def send_message(self, msg: dict) -> bool:
        line = encode(msg).encode("utf-8")
        with self._client_lock:
            if self._client_stream is None:
                return False
            try:
                self._client_stream.write(line)
                return True
            except OSError:
                return False

    def _listen_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                conn, _addr = self._listen_sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            self._handle_client(conn)

    def _handle_client(self, conn: socket.socket) -> None:
        conn.settimeout(None)
        stream = conn.makefile("rwb", buffering=0)
        with self._client_lock:
            # Replace any prior client. Drop the old connection cleanly.
            if self._client_stream is not None:
                try:
                    self._client_stream.close()
                except OSError:
                    pass
            if self._client_sock is not None:
                try:
                    self._client_sock.close()
                except OSError:
                    pass
            self._client_sock = conn
            self._client_stream = stream
        reader = FrameReader(stream)
        try:
            while not self._stop_event.is_set():
                try:
                    msg = reader.read_message()
                except ProtocolError:
                    continue
                if msg is None:
                    break
                if msg.get("type") == "req":
                    self.pending_requests.put(msg)
        except OSError:
            pass
        finally:
            with self._client_lock:
                if self._client_sock is conn:
                    self._client_sock = None
                    self._client_stream = None
            try:
                conn.close()
            except OSError:
                pass
