"""Peak metering service for FL Studio. Sampled from OnIdle() with max-hold.

No threading (FL sub-interpreter forbids daemon threads). State persists
between OnIdle calls. Takes any object exposing get_mixer_track_count() and
get_track_peaks(idx) -> (L, R) in dB — the LiveFLAdapter in production, a
fake in tests."""

__all__ = ["PeakMonitor"]

_NEG_INF = -90.0


class PeakMonitor:
    def __init__(self, api):
        self.api = api
        self.active = False
        self.max_peaks = {}      # idx -> (max_L, max_R)
        self.sample_count = 0

    def start(self):
        self.active = True
        self.max_peaks = {}
        self.sample_count = 0

    def stop(self):
        self.active = False

    def sample(self):
        """Cheap loop over tracks; called every OnIdle. No-op when inactive."""
        if not self.active:
            return
        for idx in range(self.api.get_mixer_track_count()):
            L, R = self.api.get_track_peaks(idx)
            prev_L, prev_R = self.max_peaks.get(idx, (_NEG_INF, _NEG_INF))
            self.max_peaks[idx] = (max(L, prev_L), max(R, prev_R))
        self.sample_count += 1

    def report(self) -> dict:
        return {
            "active": self.active,
            "sample_count": self.sample_count,
            "tracks": [
                {"idx": idx, "L": L, "R": R}
                for idx, (L, R) in sorted(self.max_peaks.items())
            ],
        }
