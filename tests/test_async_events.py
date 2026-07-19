import trigger
from bridge.event_sink import EventSink


class TestAsyncEventTools:
    def setup_method(self):
        # Fresh sink per test so records don't leak across tests.
        trigger._event_sink = EventSink()

    def test_get_recent_events_returns_recorded_events(self):
        trigger._event_sink.record("bpm", {"bpm": 128})
        events = trigger.get_recent_events(limit=10)
        assert events[-1]["name"] == "bpm"
        assert events[-1]["data"] == {"bpm": 128}

    def test_get_recent_events_respects_limit(self):
        for i in range(5):
            trigger._event_sink.record("bpm", {"bpm": i})
        assert len(trigger.get_recent_events(limit=2)) == 2

    def test_get_live_state_reflects_events(self):
        trigger._event_sink.record("transport", {"playing": True})
        trigger._event_sink.record("pattern", {"pattern": 3, "name": "Drop"})
        live = trigger.get_live_state()
        assert live["playing"] is True
        assert live["pattern"] == 3
        assert live["pattern_name"] == "Drop"
