"""Tests for bridge protocol message types and serialization."""
import json
import pytest
from bridge.protocol import (
    DEFAULT_HOST, DEFAULT_PORT,
    make_request, make_response_ok, make_response_error, make_event,
    encode, decode_line,
    ProtocolError,
)


class TestMessageBuilders:
    def test_make_request_has_correct_shape(self):
        msg = make_request(request_id="abc", method="ping", params={"x": 1})
        assert msg == {"type": "req", "id": "abc", "method": "ping", "params": {"x": 1}}

    def test_make_request_defaults_params_to_empty(self):
        msg = make_request(request_id="abc", method="ping")
        assert msg["params"] == {}

    def test_make_response_ok(self):
        msg = make_response_ok(request_id="abc", result={"bpm": 90})
        assert msg == {"type": "res", "id": "abc", "ok": True, "result": {"bpm": 90}}

    def test_make_response_error(self):
        msg = make_response_error(request_id="abc", error="bad method")
        assert msg == {"type": "res", "id": "abc", "ok": False, "error": "bad method"}

    def test_make_event(self):
        msg = make_event(name="bpm_changed", data={"new": 120})
        assert msg == {"type": "evt", "name": "bpm_changed", "data": {"new": 120}}


class TestEncoding:
    def test_encode_terminates_with_newline(self):
        line = encode({"type": "req", "id": "x", "method": "ping", "params": {}})
        assert line.endswith("\n")
        assert line.count("\n") == 1

    def test_encode_produces_parseable_json(self):
        line = encode({"type": "req", "id": "x", "method": "ping", "params": {}})
        parsed = json.loads(line)
        assert parsed["method"] == "ping"

    def test_decode_line_strips_newline(self):
        line = '{"type":"req","id":"x","method":"ping","params":{}}\n'
        msg = decode_line(line)
        assert msg["method"] == "ping"

    def test_decode_line_rejects_empty(self):
        with pytest.raises(ProtocolError, match="empty"):
            decode_line("")

    def test_decode_line_rejects_invalid_json(self):
        with pytest.raises(ProtocolError, match="json"):
            decode_line("not json\n")

    def test_decode_line_rejects_missing_type(self):
        with pytest.raises(ProtocolError, match="type"):
            decode_line('{"id":"x"}\n')


class TestDefaults:
    def test_default_host_is_localhost(self):
        assert DEFAULT_HOST == "127.0.0.1"

    def test_default_port(self):
        assert DEFAULT_PORT == 8765


import io
from bridge.protocol import FrameReader


class TestFrameReader:
    def test_reads_single_message(self):
        stream = io.BufferedReader(io.BytesIO(b'{"type":"req","id":"x","method":"ping","params":{}}\n'))
        reader = FrameReader(stream)
        msg = reader.read_message()
        assert msg["method"] == "ping"

    def test_reads_multiple_messages(self):
        data = (
            b'{"type":"req","id":"1","method":"a","params":{}}\n'
            b'{"type":"req","id":"2","method":"b","params":{}}\n'
        )
        reader = FrameReader(io.BufferedReader(io.BytesIO(data)))
        assert reader.read_message()["id"] == "1"
        assert reader.read_message()["id"] == "2"

    def test_returns_none_on_eof(self):
        reader = FrameReader(io.BufferedReader(io.BytesIO(b"")))
        assert reader.read_message() is None

    def test_skips_blank_lines(self):
        data = b'\n\n{"type":"req","id":"x","method":"ping","params":{}}\n'
        reader = FrameReader(io.BufferedReader(io.BytesIO(data)))
        msg = reader.read_message()
        assert msg["method"] == "ping"
