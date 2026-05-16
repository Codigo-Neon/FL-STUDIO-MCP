"""Smoke test: 100 round-trips through the bridge to catch performance
regressions. Marked slow so it doesn't run on default `pytest` invocations.
"""
import socket
import threading
import time
import pytest
from bridge.client import BridgeClient
from bridge.server import BridgeServer
from bridge.handlers import HandlerRegistry


@pytest.fixture
def free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.mark.slow
def test_100_round_trips_under_1_second(free_port):
    registry = HandlerRegistry()
    registry.register("ping", lambda params: {"pong": True})

    server = BridgeServer(port=free_port)
    server.start()
    stop = threading.Event()

    def drain_loop():
        while not stop.is_set():
            server.drain_once(registry)
            time.sleep(0.001)

    drain_thread = threading.Thread(target=drain_loop, daemon=True)
    drain_thread.start()
    try:
        client = BridgeClient(port=free_port, connect_timeout=1.0)
        client.connect()
        t0 = time.monotonic()
        for _ in range(100):
            result = client.request("ping", timeout=2.0)
            assert result == {"pong": True}
        elapsed = time.monotonic() - t0
        client.close()
        assert elapsed < 1.0, f"100 round-trips took {elapsed:.3f}s (>1s threshold)"
        print(f"\n100 round-trips: {elapsed*1000:.1f}ms total, {elapsed*10:.2f}ms per request")
    finally:
        stop.set()
        drain_thread.join(timeout=1.0)
        server.stop()
