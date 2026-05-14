"""Tests for the Linux-side BridgeClient.

Uses real loopback TCP sockets where possible — the protocol is simple
enough that mocking the socket layer obscures more than it reveals.
"""
import socket
import threading
import pytest
from bridge.client import BridgeClient, BridgeError
from bridge.protocol import encode, make_response_ok


def _start_echo_server(port: int, handler) -> threading.Thread:
    """Start a one-connection TCP server that calls `handler(line)` for each
    line received and sends back whatever handler returns (or nothing if None).

    Blocks until the server is listening, then returns. The returned thread
    runs the accept+serve loop.
    """
    ready = threading.Event()

    def serve():
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", port))
        srv.listen(1)
        ready.set()
        conn, _ = srv.accept()
        f = conn.makefile("rwb", buffering=0)
        try:
            while True:
                line = f.readline()
                if not line:
                    break
                resp = handler(line.decode("utf-8"))
                if resp is not None:
                    f.write(resp.encode("utf-8"))
        finally:
            conn.close()
            srv.close()
    t = threading.Thread(target=serve, daemon=True)
    t.start()
    ready.wait(timeout=2.0)
    return t


@pytest.fixture
def free_port():
    """Allocate an ephemeral free port for a test."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TestBridgeClientConnect:
    def test_raises_when_server_unreachable(self, free_port):
        client = BridgeClient(host="127.0.0.1", port=free_port, connect_timeout=0.2)
        with pytest.raises(BridgeError, match="connect"):
            client.connect()

    def test_connects_to_running_server(self, free_port):
        _start_echo_server(free_port, lambda line: None)
        client = BridgeClient(host="127.0.0.1", port=free_port, connect_timeout=1.0)
        client.connect()
        assert client.is_connected()
        client.close()


class TestBridgeClientRequest:
    def test_request_returns_result(self, free_port):
        import json

        def handler(line):
            req = json.loads(line)
            assert req["method"] == "ping"
            return encode(make_response_ok(request_id=req["id"], result={"pong": True}))

        _start_echo_server(free_port, handler)
        client = BridgeClient(host="127.0.0.1", port=free_port, connect_timeout=1.0)
        client.connect()
        result = client.request("ping", timeout=1.0)
        assert result == {"pong": True}
        client.close()

    def test_request_raises_on_server_error(self, free_port):
        import json
        from bridge.protocol import make_response_error

        def handler(line):
            req = json.loads(line)
            return encode(make_response_error(request_id=req["id"], error="bad method"))

        _start_echo_server(free_port, handler)
        client = BridgeClient(host="127.0.0.1", port=free_port, connect_timeout=1.0)
        client.connect()
        with pytest.raises(BridgeError, match="bad method"):
            client.request("ping", timeout=1.0)
        client.close()

    def test_request_times_out_when_server_silent(self, free_port):
        _start_echo_server(free_port, lambda line: None)  # never responds
        client = BridgeClient(host="127.0.0.1", port=free_port, connect_timeout=1.0)
        client.connect()
        with pytest.raises(BridgeError, match="timeout"):
            client.request("ping", timeout=0.2)
        client.close()

    def test_malformed_frame_then_valid_response(self, free_port):
        import json
        # First send garbage, then a valid response. Client should skip the garbage.

        def handler(line):
            req = json.loads(line)
            return f"garbage_no_json\n" + encode(make_response_ok(request_id=req["id"], result={"ok": True}))

        _start_echo_server(free_port, handler)
        client = BridgeClient(host="127.0.0.1", port=free_port, connect_timeout=1.0)
        client.connect()
        result = client.request("ping", timeout=1.0)
        assert result == {"ok": True}
        client.close()


class TestBridgeClientEvents:
    def test_event_invokes_callback(self, free_port):
        from bridge.protocol import make_event

        received = []
        event = threading.Event()

        def handler(line):
            # push an event without waiting for a request
            return encode(make_event(name="bpm_changed", data={"new": 120}))

        _start_echo_server(free_port, handler)
        client = BridgeClient(host="127.0.0.1", port=free_port, connect_timeout=1.0)
        client.connect()

        def on_evt(name, data):
            received.append((name, data))
            event.set()

        client.on_event(on_evt)
        # Trigger a write to get the server to send the event
        try:
            client.request("any", timeout=0.2)
        except BridgeError:
            pass  # we don't expect a response
        event.wait(timeout=1.0)
        client.close()

        assert received == [("bpm_changed", {"new": 120})]


class TestBridgeClientReconnect:
    def test_request_after_disconnect_reconnects(self, free_port):
        import json

        connection_count = [0]
        server_ready = threading.Event()

        def server_thread():
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", free_port))
            srv.listen(2)
            server_ready.set()
            for _ in range(2):
                conn, _ = srv.accept()
                connection_count[0] += 1
                f = conn.makefile("rwb", buffering=0)
                line = f.readline()
                req = json.loads(line.decode("utf-8"))
                resp = encode(make_response_ok(req["id"], {"hit": connection_count[0]}))
                f.write(resp.encode("utf-8"))
                # Close both the file wrapper and the socket so that the
                # kernel sends FIN immediately (makefile() dup()s the fd,
                # so both handles must be closed to release the connection).
                f.close()
                conn.close()
                if connection_count[0] == 2:
                    break
            srv.close()

        t = threading.Thread(target=server_thread, daemon=True)
        t.start()
        server_ready.wait(timeout=2.0)

        client = BridgeClient(host="127.0.0.1", port=free_port, connect_timeout=1.0, auto_reconnect=True)
        client.connect()
        r1 = client.request("ping", timeout=1.0)
        assert r1 == {"hit": 1}
        # The reader detects EOF, reconnect kicks in. We don't need a sleep —
        # `_connected.wait` inside request() blocks until the reader has
        # re-established the connection.
        r2 = client.request("ping", timeout=3.0)
        assert r2 == {"hit": 2}
        client.close()
