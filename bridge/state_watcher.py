"""State watcher for FL Studio. Polled from OnIdle; diffs (bpm, pattern,
playing) against the last tick and returns change events to push to Linux
via the SysEx bridge as `evt` messages. No threading. Pure logic —
production reads from an FLApi adapter, tests inject a fake. Mirrors the
PeakMonitor service."""

__all__ = ["StateWatcher"]


class StateWatcher:
    def __init__(self, api):
        self.api = api
        self._last = None

    def poll(self):
        """Return a list of {"name", "data"} events for fields that changed
        since the last poll. The first poll establishes a silent baseline
        (returns [] and records the current state)."""
        current = {
            # Round BPM before diffing: FL returns a float and tempo
            # automation can jitter the low bits, which would otherwise
            # emit a bpm event every OnIdle (flood).
            "bpm": round(self.api.get_bpm(), 2),
            "pattern": self.api.get_current_pattern(),
            "playing": self.api.is_playing(),
        }
        if self._last is None:
            self._last = current
            return []
        events = []
        if current["bpm"] != self._last["bpm"]:
            events.append({"name": "bpm", "data": {"bpm": current["bpm"]}})
        if current["pattern"] != self._last["pattern"]:
            idx = current["pattern"]
            events.append({"name": "pattern",
                           "data": {"pattern": idx, "name": self.api.get_pattern_name(idx)}})
        if current["playing"] != self._last["playing"]:
            events.append({"name": "transport", "data": {"playing": current["playing"]}})
        self._last = current
        return events
