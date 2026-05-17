"""Tests for FL-specific bridge handlers using a stub FL API."""
import pytest
from bridge.fl_handlers import register_all, FLApi


class FakeFLApi:
    """Implements the FLApi interface using in-memory state."""
    def __init__(self) -> None:
        self.bpm = 90.0
        self.pattern_count = 4
        self.channel_count = 8
        self.mixer_track_count = 16

    def get_bpm(self) -> float:
        return self.bpm

    def get_current_pattern(self) -> int:
        return 0

    def get_pattern_count(self) -> int:
        return self.pattern_count

    def get_channel_count(self) -> int:
        return self.channel_count

    def get_channel_name(self, index: int) -> str:
        return f"Channel {index}"

    def get_mixer_track_count(self) -> int:
        return self.mixer_track_count

    def get_mixer_track_name(self, index: int) -> str:
        return f"Track {index}" if index > 0 else "Master"


class TestPingHandler:
    def test_ping_returns_pong(self):
        from bridge.handlers import HandlerRegistry
        reg = HandlerRegistry()
        register_all(reg, FakeFLApi())
        result = reg.dispatch("ping", {})
        assert result == {"pong": True}


class TestGetFlStateHandler:
    def test_state_includes_bpm(self):
        from bridge.handlers import HandlerRegistry
        api = FakeFLApi()
        api.bpm = 128.5
        reg = HandlerRegistry()
        register_all(reg, api)
        state = reg.dispatch("get_fl_state", {})
        assert state["bpm"] == 128.5

    def test_state_includes_pattern_info(self):
        from bridge.handlers import HandlerRegistry
        reg = HandlerRegistry()
        register_all(reg, FakeFLApi())
        state = reg.dispatch("get_fl_state", {})
        assert state["current_pattern"] == 0
        assert state["pattern_count"] == 4

    def test_state_includes_channel_list(self):
        from bridge.handlers import HandlerRegistry
        reg = HandlerRegistry()
        register_all(reg, FakeFLApi())
        state = reg.dispatch("get_fl_state", {})
        assert state["channels"] == [
            {"index": 0, "name": "Channel 0"},
            {"index": 1, "name": "Channel 1"},
            {"index": 2, "name": "Channel 2"},
            {"index": 3, "name": "Channel 3"},
            {"index": 4, "name": "Channel 4"},
            {"index": 5, "name": "Channel 5"},
            {"index": 6, "name": "Channel 6"},
            {"index": 7, "name": "Channel 7"},
        ]

    def test_state_includes_mixer_tracks(self):
        from bridge.handlers import HandlerRegistry
        reg = HandlerRegistry()
        register_all(reg, FakeFLApi())
        state = reg.dispatch("get_fl_state", {})
        assert state["mixer_tracks"][0] == {"index": 0, "name": "Master"}
        assert len(state["mixer_tracks"]) == 16
