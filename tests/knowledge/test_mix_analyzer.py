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


class TestAnalyzePeaks:
    def test_flags_near_clip_track(self):
        peaks = {"sample_count": 50, "tracks": [{"idx": 5, "L": -2.0, "R": -2.5}]}
        report = mix_analyzer.analyze_peaks(peaks, {"true_peak": -1.0})
        flagged = [t for t in report["tracks"] if "near-clip" in t["flags"]]
        assert len(flagged) == 1 and flagged[0]["idx"] == 5

    def test_peak_below_threshold_not_flagged(self):
        peaks = {"sample_count": 50, "tracks": [{"idx": 5, "L": -6.0, "R": -6.0}]}
        report = mix_analyzer.analyze_peaks(peaks, {"true_peak": -1.0})
        assert report["tracks"] == []

    def test_no_peak_data_sets_flag(self):
        report = mix_analyzer.analyze_peaks({"sample_count": 0, "tracks": []}, {"true_peak": -1.0})
        assert "no-peak-data" in report["global_flags"]

    def test_kind_is_peaks(self):
        report = mix_analyzer.analyze_peaks({"sample_count": 1, "tracks": []}, {"true_peak": -1.0})
        assert report["kind"] == "peaks"


class TestScoreMaster:
    def _peaks(self, L, R, count=100):
        return {"sample_count": count, "tracks": [{"idx": 0, "L": L, "R": R}]}

    def test_flags_over_target_with_excess(self):
        report = mix_analyzer.score_master(
            {"idx": 0, "fx": ["Maximus"]}, self._peaks(-0.1, -0.4), {"true_peak": -0.3})
        assert "over-target" in report["flags"]
        assert report["L_excess_db"] == pytest.approx(0.2)
        assert report["R_excess_db"] == pytest.approx(0.0)  # -0.4 is under -0.3

    def test_within_target_no_over_flag(self):
        report = mix_analyzer.score_master(
            {"idx": 0, "fx": []}, self._peaks(-1.5, -1.6), {"true_peak": -1.0})
        assert "over-target" not in report["flags"]

    def test_flags_stereo_imbalance(self):
        report = mix_analyzer.score_master(
            {"idx": 0, "fx": []}, self._peaks(-1.0, -5.0), {"true_peak": -0.3})
        assert "stereo-imbalance" in report["flags"]

    def test_no_peak_data_when_count_zero(self):
        report = mix_analyzer.score_master(
            {"idx": 0, "fx": []}, {"sample_count": 0, "tracks": []}, {"true_peak": -1.0})
        assert "no-peak-data" in report["flags"]

    def test_kind_is_master(self):
        report = mix_analyzer.score_master(
            {"idx": 0, "fx": []}, self._peaks(-2.0, -2.0), {"true_peak": -1.0})
        assert report["kind"] == "master"

    def test_lufs_declared_unavailable(self):
        report = mix_analyzer.score_master(
            {"idx": 0, "fx": []}, self._peaks(-2.0, -2.0), {"true_peak": -1.0})
        assert report["lufs"] == "not_available"


class TestSuggestFixes:
    def test_over_target_suggests_lowering_limiter(self):
        master = {"kind": "master", "flags": ["over-target"], "L_excess_db": 0.2,
                  "R_excess_db": 0.0, "true_peak_target": -0.3}
        fixes = mix_analyzer.suggest_fixes({"global_flags": [], "tracks": []}, master, {})
        assert any("limiter" in f.lower() or "ceiling" in f.lower() for f in fixes)
        assert any("0.2" in f for f in fixes)

    def test_fx_heavy_suggests_review(self):
        static = {"global_flags": [], "tracks": [{"idx": 5, "name": "Kick", "flags": ["fx-heavy"]}]}
        fixes = mix_analyzer.suggest_fixes(static, {"flags": []}, {})
        assert any("Kick" in f and ("FX" in f or "efecto" in f.lower()) for f in fixes)

    def test_no_flags_returns_empty(self):
        fixes = mix_analyzer.suggest_fixes({"global_flags": [], "tracks": []}, {"flags": []}, {})
        assert fixes == []


class TestFormatReportEs:
    def test_static_report_mentions_track_count_and_flags(self):
        static = {"kind": "static", "track_count": 23,
                  "tracks": [{"idx": 5, "name": "Kick", "flags": ["fx-heavy"]}],
                  "global_flags": ["master-clipping-risk"]}
        text = mix_analyzer.format_report_es(static, fixes=["Bajá el master fader."])
        assert "23" in text
        assert "Kick" in text
        assert "Bajá el master fader." in text

    def test_master_report_mentions_peaks_and_target(self):
        master = {"kind": "master", "master_L": -0.1, "master_R": -0.4,
                  "true_peak_target": -0.3, "lufs": "not_available",
                  "flags": ["over-target"]}
        text = mix_analyzer.format_report_es(master, fixes=[])
        assert "-0.1" in text and "-0.4" in text
        assert "-0.3" in text
        assert "LUFS" in text  # must disclose LUFS unavailability

    def test_no_peak_data_message(self):
        master = {"kind": "master", "master_L": -90.0, "master_R": -90.0,
                  "true_peak_target": -1.0, "lufs": "not_available",
                  "flags": ["no-peak-data"]}
        text = mix_analyzer.format_report_es(master, fixes=[])
        assert "start_peak_monitoring" in text

    def test_master_report_missing_peak_keys_no_crash(self):
        master = {"kind": "master", "true_peak_target": -1.0,
                  "lufs": "not_available", "flags": []}
        text = mix_analyzer.format_report_es(master, fixes=[])
        assert "LUFS" in text  # renders without raising
