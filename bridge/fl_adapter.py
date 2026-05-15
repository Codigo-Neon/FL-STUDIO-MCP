"""Live adapter that bridges FLApi to FL Studio's Script API.

This module is imported only by `device_test.py` inside FL Studio. Importing
it outside FL will raise ImportError because `mixer`, `patterns`, etc. are
modules injected by FL into its embedded Python.

Tests use the fake adapter from tests/bridge/test_fl_handlers.py; this file
is verified manually via the QA checklist.
"""

__all__ = ["LiveFLAdapter"]


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
