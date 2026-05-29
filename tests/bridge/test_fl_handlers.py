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

        # Mix data: idx -> values
        self.volumes = {0: 0.85, 5: 0.8}
        self.pans = {}
        self.mutes = {}
        self.solos = {}
        self.peaks = {0: (-0.1, -0.4), 5: (-3.0, -3.2)}
        self.fx = {0: ["Maximus"], 5: ["EQ", "Comp"]}
        self.sends = {5: [0]}
        self.names = {0: "Master", 5: "Kick"}

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
        return self.names.get(index, f"Insert {index}")

    def get_track_volume(self, idx): return self.volumes.get(idx, 0.0)
    def get_track_pan(self, idx): return self.pans.get(idx, 0.0)
    def get_track_mute(self, idx): return self.mutes.get(idx, False)
    def get_track_solo(self, idx): return self.solos.get(idx, False)
    def get_track_peaks(self, idx): return self.peaks.get(idx, (-90.0, -90.0))
    def get_effect_count(self, track): return len(self.fx.get(track, []))
    def get_effect_name(self, track, slot):
        fx = self.fx.get(track, [])
        return fx[slot] if slot < len(fx) else ""
    def get_track_route_sends(self, idx): return self.sends.get(idx, [])


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


class TestMixerSnapshot:
    def _reg(self):
        from bridge.handlers import HandlerRegistry
        reg = HandlerRegistry()
        register_all(reg, FakeFLApi())
        return reg

    def test_snapshot_includes_active_tracks_with_fields(self):
        snap = self._reg().dispatch("get_mixer_snapshot", {})
        kick = next(t for t in snap["tracks"] if t["idx"] == 5)
        assert kick["name"] == "Kick"
        assert kick["vol"] == 0.8
        assert kick["fx"] == ["EQ", "Comp"]
        assert kick["sends"] == [0]

    def test_snapshot_omits_empty_default_tracks(self):
        # track 7 has default name, vol 0, no fx → omitted
        snap = self._reg().dispatch("get_mixer_snapshot", {})
        idxs = [t["idx"] for t in snap["tracks"]]
        assert 7 not in idxs

    def test_snapshot_includes_master(self):
        snap = self._reg().dispatch("get_mixer_snapshot", {})
        assert any(t["idx"] == 0 for t in snap["tracks"])

    def test_master_snapshot_returns_track_zero_detail(self):
        ms = self._reg().dispatch("get_master_snapshot", {})
        assert ms["idx"] == 0
        assert ms["name"] == "Master"
        assert ms["fx"] == ["Maximus"]
