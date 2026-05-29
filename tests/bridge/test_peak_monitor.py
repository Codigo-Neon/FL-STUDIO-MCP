from bridge.peak_monitor import PeakMonitor


class FakePeakApi:
    def __init__(self):
        self.count = 3
        self.peaks = {0: (-6.0, -6.0), 1: (-3.0, -3.0)}

    def get_mixer_track_count(self):
        return self.count

    def get_track_peaks(self, idx):
        return self.peaks.get(idx, (-90.0, -90.0))


class TestPeakMonitor:
    def test_sample_noop_when_inactive(self):
        m = PeakMonitor(FakePeakApi())
        m.sample()
        assert m.report()["sample_count"] == 0

    def test_max_hold_keeps_highest_per_channel(self):
        api = FakePeakApi()
        m = PeakMonitor(api)
        m.start()
        api.peaks[1] = (-6.0, -5.5)
        m.sample()
        api.peaks[1] = (-3.0, -8.0)  # L rises, R falls
        m.sample()
        track1 = next(t for t in m.report()["tracks"] if t["idx"] == 1)
        assert track1["L"] == -3.0
        assert track1["R"] == -5.5

    def test_start_clears_previous_state(self):
        api = FakePeakApi()
        m = PeakMonitor(api)
        m.start()
        m.sample()
        m.start()
        assert m.report()["sample_count"] == 0
        assert m.report()["tracks"] == []

    def test_stop_keeps_data_but_marks_inactive(self):
        m = PeakMonitor(FakePeakApi())
        m.start()
        m.sample()
        m.stop()
        rep = m.report()
        assert rep["active"] is False
        assert rep["sample_count"] == 1

    def test_report_tracks_is_sorted_list(self):
        m = PeakMonitor(FakePeakApi())
        m.start()
        m.sample()
        idxs = [t["idx"] for t in m.report()["tracks"]]
        assert idxs == sorted(idxs)
