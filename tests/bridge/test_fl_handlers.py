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
        self.transport_log = []
        self.selected_channel_name = "Selected"
        self.playing = False
        self.pattern_names = {0: "Pattern 1"}

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
    def get_effect_names(self, track): return list(self.fx.get(track, []))
    def get_track_route_sends(self, idx): return self.sends.get(idx, [])

    def start_playback(self): self.transport_log.append("start")
    def stop_playback(self): self.transport_log.append("stop")
    def seek_to_start(self): self.transport_log.append("seek")
    def get_selected_channel_name(self): return self.selected_channel_name
    def is_playing(self): return self.playing
    def get_pattern_name(self, idx): return self.pattern_names.get(idx, f"Pattern {idx + 1}")


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

    def test_snapshot_fx_list_from_get_effect_names(self):
        api = FakeFLApi()
        api.fx[5] = ["EQ", "Comp", "Limiter"]
        from bridge.handlers import HandlerRegistry
        reg = HandlerRegistry()
        register_all(reg, api)
        snap = reg.dispatch("get_mixer_snapshot", {})
        kick = next(t for t in snap["tracks"] if t["idx"] == 5)
        assert kick["fx"] == ["EQ", "Comp", "Limiter"]


class TestPeakMonitoringHandlers:
    def _reg(self, monitor=None):
        from bridge.handlers import HandlerRegistry
        reg = HandlerRegistry()
        register_all(reg, FakeFLApi(), peak_monitor=monitor)
        return reg

    def test_start_stop_report_lifecycle(self):
        from bridge.peak_monitor import PeakMonitor
        api = FakeFLApi()
        monitor = PeakMonitor(api)
        reg = self._reg(monitor)

        reg.dispatch("start_peak_monitoring", {})
        assert monitor.active is True
        monitor.sample()  # simulate OnIdle
        reg.dispatch("stop_peak_monitoring", {})
        assert monitor.active is False

        report = reg.dispatch("get_peak_report", {})
        assert report["sample_count"] == 1
        assert any(t["idx"] == 5 for t in report["tracks"])

    def test_handlers_error_when_no_monitor(self):
        reg = self._reg(monitor=None)
        result = reg.dispatch("get_peak_report", {})
        assert "error" in result


class TestGranularHandlers:
    def _reg(self):
        from bridge.handlers import HandlerRegistry
        reg = HandlerRegistry()
        register_all(reg, FakeFLApi())
        return reg

    def test_get_track_volume(self):
        assert self._reg().dispatch("get_track_volume", {"track": 5}) == {"track": 5, "volume": 0.8}

    def test_get_track_pan(self):
        assert self._reg().dispatch("get_track_pan", {"track": 5}) == {"track": 5, "pan": 0.0}

    def test_get_track_peaks(self):
        result = self._reg().dispatch("get_track_peaks", {"track": 5})
        assert result == {"track": 5, "L": -3.0, "R": -3.2}


class TestTransportAndSelectedChannel:
    def test_fake_api_supports_transport_and_selected_channel(self):
        api = FakeFLApi()
        api.start_playback()
        api.stop_playback()
        api.seek_to_start()
        assert api.transport_log == ["start", "stop", "seek"]
        assert api.get_selected_channel_name() == "Selected"


class TestNoteCaptureHandlers:
    def _reg(self, api, note_capture):
        from bridge.handlers import HandlerRegistry
        reg = HandlerRegistry()
        register_all(reg, api, note_capture=note_capture)
        return reg

    def test_arm_arms_and_starts_playback(self):
        from bridge.note_capture import NoteCapture
        api, nc = FakeFLApi(), NoteCapture()
        reg = self._reg(api, nc)
        res = reg.dispatch("arm_note_capture", {})
        assert res == {"armed": True}
        assert nc.armed is True
        assert api.transport_log == ["seek", "start"]

    def test_disarm_disarms_and_stops_playback(self):
        from bridge.note_capture import NoteCapture
        api, nc = FakeFLApi(), NoteCapture()
        nc.arm()
        reg = self._reg(api, nc)
        res = reg.dispatch("disarm_note_capture", {})
        assert res == {"armed": False}
        assert nc.armed is False
        assert api.transport_log == ["stop"]

    def test_get_captured_notes_returns_notes_and_channel(self):
        from bridge.note_capture import NoteCapture
        api, nc = FakeFLApi(), NoteCapture()
        api.selected_channel_name = "Bass"
        nc.arm()
        nc.feed(40, 100, True, 0.0); nc.feed(40, 0, False, 1.0)
        reg = self._reg(api, nc)
        res = reg.dispatch("get_captured_notes", {})
        assert res["channel_name"] == "Bass"
        assert res["count"] == 1
        assert res["notes"][0] == {"note": 40, "velocity": 100, "length": 1.0, "position": 0.0}

    def test_handlers_error_when_capture_unavailable(self):
        from bridge.handlers import HandlerRegistry
        reg = HandlerRegistry()
        register_all(reg, FakeFLApi())          # note_capture defaults to None
        assert reg.dispatch("arm_note_capture", {}) == {"error": "note capture not available"}
        assert reg.dispatch("get_captured_notes", {}) == {"error": "note capture not available"}


class TestPlayingAndPatternName:
    def test_fake_api_supports_is_playing_and_pattern_name(self):
        api = FakeFLApi()
        assert api.is_playing() is False
        api.playing = True
        assert api.is_playing() is True
        assert api.get_pattern_name(0) == "Pattern 1"
