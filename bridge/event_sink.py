"""Linux-side sink for async bridge events (`evt`). Registered via
SysExClient.on_event, so record() is called from the reader thread — it's
thread-safe. Keeps a bounded log of recent events plus a live-state cache
that reflects the latest value of each tracked field."""
from collections import deque
import threading

__all__ = ["EventSink"]


class EventSink:
    def __init__(self, maxlen=100):
        self._events = deque(maxlen=maxlen)
        self._live = {}
        self._seq = 0
        self._lock = threading.Lock()

    def record(self, name, data):
        """on_event callback. Appends to the log and updates the live cache."""
        with self._lock:
            self._seq += 1
            self._events.append({"seq": self._seq, "name": name, "data": data})
            if name == "bpm":
                self._live["bpm"] = data.get("bpm")
            elif name == "transport":
                self._live["playing"] = data.get("playing")
            elif name == "pattern":
                self._live["pattern"] = data.get("pattern")
                self._live["pattern_name"] = data.get("name")

    def recent(self, limit=20):
        with self._lock:
            events = list(self._events)
        return events[-limit:]

    def live_state(self):
        with self._lock:
            return dict(self._live)
