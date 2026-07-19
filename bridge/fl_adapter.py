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
        import transport
        self._mixer = mixer
        self._patterns = patterns
        self._channels = channels
        self._general = general
        self._transport = transport

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

    def get_effect_names(self, track: int) -> list:
        # FL mixer tracks have 10 effect slots; collect names of non-empty ones.
        import plugins
        names = []
        for slot in range(10):
            if self._mixer.getTrackPluginId(track, slot) != -1:
                names.append(plugins.getPluginName(track, slot))
        return names

    def get_track_route_sends(self, index: int) -> list:
        sends = []
        for dest in range(self._mixer.trackCount()):
            if dest != index and self._mixer.getRouteSendActive(index, dest):
                sends.append(dest)
        return sends

    def start_playback(self) -> None:
        if not self._transport.isPlaying():
            self._transport.start()

    def stop_playback(self) -> None:
        if self._transport.isPlaying():
            self._transport.stop()

    def seek_to_start(self) -> None:
        # 2 = SONGLENGTH_ABSTICKS (same constant used elsewhere in device_test)
        self._transport.setSongPos(0, 2)

    def get_selected_channel_name(self) -> str:
        return self._channels.getChannelName(self._channels.selectedChannel())

    def is_playing(self) -> bool:
        return bool(self._transport.isPlaying())

    def get_pattern_name(self, idx: int) -> str:
        return self._patterns.getPatternName(idx)
