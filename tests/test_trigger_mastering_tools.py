import importlib
import pytest
from unittest.mock import Mock

trigger = importlib.import_module("trigger")


class TestGenreState:
    def setup_method(self):
        trigger.current_genre = "neutral"
        trigger.current_mastering_target = dict(
            trigger.mix_analyzer.GENRE_TARGETS["neutral"])

    def test_set_genre_updates_target(self):
        msg = trigger.set_genre("phonk")
        assert trigger.current_genre == "phonk"
        assert trigger.current_mastering_target["lufs"] == -6
        assert "phonk" in msg

    def test_set_genre_unknown_rejected(self):
        msg = trigger.set_genre("dubstep")
        assert "no soportado" in msg
        assert trigger.current_genre == "neutral"

    def test_set_mastering_target_override(self):
        trigger.set_genre("phonk")
        trigger.set_mastering_target(lufs=-5)
        assert trigger.current_mastering_target["lufs"] == -5
        assert trigger.current_mastering_target["true_peak"] == -0.3  # unchanged

    def test_set_mastering_target_out_of_range(self):
        msg = trigger.set_mastering_target(lufs=5)
        assert "rango" in msg

    def test_get_mastering_target_returns_dict(self):
        trigger.set_genre("trap")
        t = trigger.get_mastering_target()
        assert t["lufs"] == -7


class TestAnalyzeMixStatic:
    def test_static_report_built_from_bridge_snapshot(self, monkeypatch):
        fake = Mock()
        fake.request.return_value = {"tracks": [
            {"idx": 0, "name": "Master", "vol": 1.25, "pan": 0.0, "mute": False,
             "solo": False, "fx": [], "sends": []},
            {"idx": 5, "name": "Kick", "vol": 0.8, "pan": 0.0, "mute": False,
             "solo": False, "fx": ["EQ", "C", "EQ", "Sat", "Lim"], "sends": [0]},
        ]}
        monkeypatch.setattr(trigger, "_get_bridge", lambda: fake)
        result = trigger.analyze_mix_static()
        assert "Kick" in result
        assert "master-clipping-risk" in result or "master fader" in result.lower()
        fake.request.assert_called_with("get_mixer_snapshot", timeout=5.0)

    def test_bridge_error_returns_message(self, monkeypatch):
        def boom():
            raise trigger.SysExBridgeError("no port")
        monkeypatch.setattr(trigger, "_get_bridge", boom)
        result = trigger.analyze_mix_static()
        assert "Bridge desconectado" in result


class TestAnalyzeMaster:
    def setup_method(self):
        trigger.current_mastering_target = {"lufs": -6, "true_peak": -0.3,
                                            "headroom_db": 4, "dynamics": "tight"}

    def test_master_report_uses_current_target(self, monkeypatch):
        fake = Mock()
        fake.request.side_effect = [
            {"idx": 0, "name": "Master", "vol": 0.85, "pan": 0.0, "fx": ["Maximus"], "sends": []},
            {"sample_count": 100, "tracks": [{"idx": 0, "L": -0.1, "R": -0.4}]},
        ]
        monkeypatch.setattr(trigger, "_get_bridge", lambda: fake)
        result = trigger.analyze_master()
        assert "-0.3" in result          # target true peak
        assert "over-target" in result or "excede" in result.lower()
        assert "LUFS" in result          # discloses LUFS unavailability

    def test_no_peak_data_guidance(self, monkeypatch):
        fake = Mock()
        fake.request.side_effect = [
            {"idx": 0, "name": "Master", "vol": 0.85, "fx": [], "sends": []},
            {"sample_count": 0, "tracks": []},
        ]
        monkeypatch.setattr(trigger, "_get_bridge", lambda: fake)
        result = trigger.analyze_master()
        assert "start_peak_monitoring" in result

    def test_bridge_error_returns_message(self, monkeypatch):
        def boom():
            raise trigger.SysExBridgeError("no port")
        monkeypatch.setattr(trigger, "_get_bridge", boom)
        assert "Bridge desconectado" in trigger.analyze_master()
