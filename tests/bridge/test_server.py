"""Tests for the FL-side BridgeServer.

The server runs inside FL Studio's script process. In tests we run it in a
normal Python process and connect from another thread.
"""
import json
import socket
import threading
import time
import pytest
from bridge.server import BridgeServer
from bridge.protocol import make_response_ok


@pytest.fixture
def free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TestBridgeServerLifecycle:
    def test_start_then_stop(self, free_port):
        server = BridgeServer(port=free_port)
        server.start()
        assert server.is_running()
        server.stop()
        assert not server.is_running()

    def test_accepts_client_connection(self, free_port):
        server = BridgeServer(port=free_port)
        server.start()
        try:
            sock = socket.create_connection(("127.0.0.1", free_port), timeout=1.0)
            assert sock is not None
            sock.close()
        finally:
            server.stop()


class TestBridgeServerRequestQueue:
    def test_received_request_appears_on_queue(self, free_port):
        server = BridgeServer(port=free_port)
        server.start()
        try:
            sock = socket.create_connection(("127.0.0.1", free_port), timeout=1.0)
            f = sock.makefile("rwb", buffering=0)
            req = '{"type":"req","id":"abc","method":"ping","params":{}}\n'
            f.write(req.encode("utf-8"))
            request = server.pending_requests.get(timeout=1.0)
            assert request["id"] == "abc"
            assert request["method"] == "ping"
            sock.close()
        finally:
            server.stop()


class TestBridgeServerSendResponse:
    def test_send_response_reaches_client(self, free_port):
        server = BridgeServer(port=free_port)
        server.start()
        try:
            sock = socket.create_connection(("127.0.0.1", free_port), timeout=1.0)
            f = sock.makefile("rwb", buffering=0)
            f.write(b'{"type":"req","id":"abc","method":"ping","params":{}}\n')
            server.pending_requests.get(timeout=1.0)
            server.send_message(make_response_ok("abc", {"pong": True}))
            line = f.readline()
            msg = json.loads(line.decode("utf-8"))
            assert msg == {"type": "res", "id": "abc", "ok": True, "result": {"pong": True}}
            sock.close()
        finally:
            server.stop()


class TestBridgeServerEvents:
    def test_send_event_reaches_client(self, free_port):
        from bridge.protocol import make_event

        server = BridgeServer(port=free_port)
        server.start()
        try:
            sock = socket.create_connection(("127.0.0.1", free_port), timeout=1.0)
            f = sock.makefile("rwb", buffering=0)
            # wait for server to register the client
            time.sleep(0.1)
            server.send_message(make_event("bpm_changed", {"new": 120}))
            line = f.readline()
            msg = json.loads(line.decode("utf-8"))
            assert msg == {"type": "evt", "name": "bpm_changed", "data": {"new": 120}}
            sock.close()
        finally:
            server.stop()
