"""Note capture service for FL Studio. Buffers note-on/off during pattern
playback so Linux can reconstruct the selected channel's notes.

No threading (FL sub-interpreter forbids daemon threads). FL's playback
callback (OnMidiOutMsg) calls feed(...) on the main thread; bridge handlers
query it via arm()/disarm()/notes(). Pure logic — production passes
positions read from FL's transport (in beats); tests inject positions
directly. Mirrors the PeakMonitor service."""

__all__ = ["NoteCapture"]


class NoteCapture:
    def __init__(self):
        self.armed = False
        self._open = {}      # note -> FIFO list of (velocity, position_beats)
        self._closed = []    # list of {note, velocity, length, position}

    def arm(self):
        self.armed = True
        self._open = {}
        self._closed = []

    def disarm(self):
        self.armed = False

    def feed(self, note, velocity, is_on, position_beats):
        """Record a note event. No-op when not armed. A note-on with
        velocity 0 is treated as a note-off (running-status convention)."""
        if not self.armed:
            return
        if is_on and velocity > 0:
            self._open.setdefault(note, []).append((velocity, position_beats))
            return
        # note-off (or note-on vel 0): close oldest open note of this pitch
        stack = self._open.get(note)
        if not stack:
            return  # orphan off — discard
        vel, pos_on = stack.pop(0)
        length = position_beats - pos_on
        if length < 0:
            length = 0.0
        self._closed.append({
            "note": note, "velocity": vel,
            "length": length, "position": pos_on,
        })

    def notes(self):
        """Reconstructed notes, sorted by (position, pitch). Notes still open
        (no matching off) are included with length 0 — signals a cut capture."""
        result = list(self._closed)
        for note, stack in self._open.items():
            for vel, pos_on in stack:
                result.append({"note": note, "velocity": vel,
                               "length": 0.0, "position": pos_on})
        result.sort(key=lambda n: (n["position"], n["note"]))
        return result
