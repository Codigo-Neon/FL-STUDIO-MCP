"""Live adapter that bridges FLApi to FL Studio's Script API.

This module is imported only by `device_test.py` inside FL Studio. Importing
it outside FL will raise ImportError because `mixer`, `patterns`, etc. are
modules injected by FL into its embedded Python.

Tests use the fake adapter from tests/bridge/test_fl_handlers.py; this file
is verified manually via the QA checklist.
"""
import math

__all__ = ["LiveFLAdapter"]


def _amp_to_db(amp: float) -> float:
    """Convert FL linear peak amplitude (0.0..~1.0) to dBFS, clamped at -90."""
    if amp <= 0.0:
        return -90.0
    return 20.0 * math.log10(amp)


class LiveFLAdapter:
    """Concrete FLApi implementation backed by FL Studio's script modules."""

    def __init__(self) -> None:
        # Lazy imports so the module file itself can be loaded outside FL.
        import mixer
        import patterns
        import channels
        import general
        self._mixer = mixer
        self._patterns = patterns
        self._channels = channels
        self._general = general

    def get_bpm(self) -> float:
        # FL exposes BPM via mixer.getCurrentTempo() returning BPM * 1000.
        return self._mixer.getCurrentTempo() / 1000.0

    def get_current_pattern(self) -> int:
        return self._patterns.patternNumber()

    def get_pattern_count(self) -> int:
        return self._patterns.patternCount()

    def get_channel_count(self) -> int:
        return self._channels.channelCount()

    def get_channel_name(self, index: int) -> str:
        return self._channels.getChannelName(index)

    def get_mixer_track_count(self) -> int:
        return self._mixer.trackCount()

    def get_mixer_track_name(self, index: int) -> str:
        return self._mixer.getTrackName(index)

    def get_track_volume(self, index: int) -> float:
        return self._mixer.getTrackVolume(index)

    def get_track_pan(self, index: int) -> float:
        return self._mixer.getTrackPan(index)

    def get_track_mute(self, index: int) -> bool:
        return bool(self._mixer.isTrackMuted(index))

    def get_track_solo(self, index: int) -> bool:
        return bool(self._mixer.isTrackSolo(index))

    def get_track_peaks(self, index: int):
        # mixer.getTrackPeaks(track, mode): mode 0 = left, 1 = right (linear amp)
        L = self._mixer.getTrackPeaks(index, 0)
        R = self._mixer.getTrackPeaks(index, 1)
        return (_amp_to_db(L), _amp_to_db(R))

    def get_effect_count(self, track: int) -> int:
        # FL mixer tracks have 10 effect slots; count the non-empty ones.
        count = 0
        for slot in range(10):
            if self._mixer.getTrackPluginId(track, slot) != -1:
                count += 1
        return count

    def get_effect_name(self, track: int, slot: int) -> str:
        plugin_id = self._mixer.getTrackPluginId(track, slot)
        if plugin_id == -1:
            return ""
        import plugins
        return plugins.getPluginName(track, slot)

    def get_track_route_sends(self, index: int) -> list:
        sends = []
        for dest in range(self._mixer.trackCount()):
            if dest != index and self._mixer.getRouteSendActive(index, dest):
                sends.append(dest)
        return sends
