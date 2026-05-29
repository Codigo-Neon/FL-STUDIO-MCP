import pytest
from knowledge import mix_analyzer


class TestGenreTarget:
    def test_known_genre_returns_its_target(self):
        t = mix_analyzer.get_genre_target("phonk")
        assert t["lufs"] == -6
        assert t["true_peak"] == -0.3

    def test_unknown_genre_returns_neutral(self):
        assert mix_analyzer.get_genre_target("dubstep") == mix_analyzer.GENRE_TARGETS["neutral"]

    def test_returns_a_copy_not_the_shared_dict(self):
        t = mix_analyzer.get_genre_target("trap")
        t["lufs"] = 0
        assert mix_analyzer.GENRE_TARGETS["trap"]["lufs"] == -7


class TestAnalyzeStatic:
    def _track(self, **kw):
        base = {"idx": 1, "name": "Insert 1", "vol": 0.8, "pan": 0.0,
                "mute": False, "solo": False, "fx": [], "sends": []}
        base.update(kw)
        return base

    def test_flags_fx_heavy_track(self):
        snap = {"tracks": [self._track(idx=5, name="Kick", fx=["EQ", "C", "EQ", "Sat", "Lim"])]}
        report = mix_analyzer.analyze_static(snap)
        flagged = [t for t in report["tracks"] if "fx-heavy" in t["flags"]]
        assert len(flagged) == 1 and flagged[0]["idx"] == 5

    def test_four_fx_is_not_fx_heavy(self):
        snap = {"tracks": [self._track(idx=5, fx=["EQ", "C", "EQ", "Sat"])]}
        report = mix_analyzer.analyze_static(snap)
        assert report["tracks"] == []  # no flags → not listed

    def test_flags_master_clipping_risk_when_fader_above_unity(self):
        # vol 1.0 == 0dB unity in FL; >1.0 means boost
        snap = {"tracks": [self._track(idx=0, name="Master", vol=1.25)]}
        report = mix_analyzer.analyze_static(snap)
        assert "master-clipping-risk" in report["global_flags"]

    def test_flags_silent_active_track(self):
        snap = {"tracks": [self._track(idx=3, name="Hat", vol=0.0, mute=False)]}
        report = mix_analyzer.analyze_static(snap)
        flagged = [t for t in report["tracks"] if "silent-active" in t["flags"]]
        assert len(flagged) == 1

    def test_muted_silent_track_not_flagged(self):
        snap = {"tracks": [self._track(idx=3, vol=0.0, mute=True)]}
        report = mix_analyzer.analyze_static(snap)
        assert report["tracks"] == []

    def test_report_kind_and_count(self):
        snap = {"tracks": [self._track(idx=1), self._track(idx=2)]}
        report = mix_analyzer.analyze_static(snap)
        assert report["kind"] == "static"
        assert report["track_count"] == 2

    def test_missing_keys_use_defaults_no_crash(self):
        report = mix_analyzer.analyze_static({"tracks": [{"idx": 9}]})
        assert report["kind"] == "static"
