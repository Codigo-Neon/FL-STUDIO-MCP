"""End-to-end tests: client → server → registry → response."""
import socket
import threading
import time
import pytest
from bridge.client import BridgeClient, BridgeError
from bridge.server import BridgeServer
from bridge.handlers import HandlerRegistry


@pytest.fixture
def free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TestIntegration:
    def test_ping_round_trip(self, free_port):
        registry = HandlerRegistry()
        registry.register("ping", lambda params: {"pong": True})

        server = BridgeServer(port=free_port)
        server.start()

        # Pump drain loop from a background thread so the test feels like
        # the real OnIdle() callback in FL Studio.
        stop = threading.Event()

        def drain_loop():
            while not stop.is_set():
                server.drain_once(registry)
                time.sleep(0.01)

        drain_thread = threading.Thread(target=drain_loop, daemon=True)
        drain_thread.start()

        try:
            client = BridgeClient(port=free_port, connect_timeout=1.0)
            client.connect()
            result = client.request("ping", timeout=2.0)
            assert result == {"pong": True}
            client.close()
        finally:
            stop.set()
            drain_thread.join(timeout=1.0)
            server.stop()

    def test_unknown_method_returns_error(self, free_port):
        registry = HandlerRegistry()  # empty

        server = BridgeServer(port=free_port)
        server.start()
        stop = threading.Event()

        def drain_loop():
            while not stop.is_set():
                server.drain_once(registry)
                time.sleep(0.01)

        drain_thread = threading.Thread(target=drain_loop, daemon=True)
        drain_thread.start()

        try:
            client = BridgeClient(port=free_port, connect_timeout=1.0)
            client.connect()
            with pytest.raises(BridgeError, match="unknown method"):
                client.request("nope", timeout=2.0)
            client.close()
        finally:
            stop.set()
            drain_thread.join(timeout=1.0)
            server.stop()

    def test_handler_exception_returns_error(self, free_port):
        registry = HandlerRegistry()

        def boom(params):
            raise RuntimeError("handler crashed")

        registry.register("boom", boom)

        server = BridgeServer(port=free_port)
        server.start()
        stop = threading.Event()

        def drain_loop():
            while not stop.is_set():
                server.drain_once(registry)
                time.sleep(0.01)

        drain_thread = threading.Thread(target=drain_loop, daemon=True)
        drain_thread.start()

        try:
            client = BridgeClient(port=free_port, connect_timeout=1.0)
            client.connect()
            with pytest.raises(BridgeError, match="handler crashed"):
                client.request("boom", timeout=2.0)
            client.close()
        finally:
            stop.set()
            drain_thread.join(timeout=1.0)
            server.stop()
