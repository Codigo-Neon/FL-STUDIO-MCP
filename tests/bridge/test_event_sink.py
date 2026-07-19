from bridge.event_sink import EventSink


class TestEventSink:
    def test_record_appends_with_incrementing_seq(self):
        s = EventSink()
        s.record("bpm", {"bpm": 120})
        s.record("transport", {"playing": True})
        events = s.recent()
        assert [e["seq"] for e in events] == [1, 2]
        assert events[0] == {"seq": 1, "name": "bpm", "data": {"bpm": 120}}

    def test_bpm_event_updates_live_state(self):
        s = EventSink()
        s.record("bpm", {"bpm": 140})
        assert s.live_state() == {"bpm": 140}

    def test_transport_event_updates_live_state(self):
        s = EventSink()
        s.record("transport", {"playing": True})
        assert s.live_state()["playing"] is True

    def test_pattern_event_updates_live_state_with_name(self):
        s = EventSink()
        s.record("pattern", {"pattern": 2, "name": "Verse"})
        live = s.live_state()
        assert live["pattern"] == 2
        assert live["pattern_name"] == "Verse"

    def test_live_state_reflects_latest_value(self):
        s = EventSink()
        s.record("bpm", {"bpm": 120})
        s.record("bpm", {"bpm": 90})
        assert s.live_state()["bpm"] == 90

    def test_recent_respects_limit(self):
        s = EventSink()
        for i in range(5):
            s.record("bpm", {"bpm": i})
        assert len(s.recent(limit=2)) == 2
        assert s.recent(limit=2)[-1]["data"]["bpm"] == 4

    def test_deque_evicts_beyond_maxlen(self):
        s = EventSink(maxlen=3)
        for i in range(5):
            s.record("bpm", {"bpm": i})
        events = s.recent(limit=100)
        assert len(events) == 3
        assert [e["data"]["bpm"] for e in events] == [2, 3, 4]

    def test_live_state_returns_copy(self):
        s = EventSink()
        s.record("bpm", {"bpm": 120})
        s.live_state()["bpm"] = 999
        assert s.live_state()["bpm"] == 120

    def test_recent_with_nonpositive_limit_returns_empty(self):
        s = EventSink()
        s.record("bpm", {"bpm": 1})
        assert s.recent(limit=0) == []
        assert s.recent(limit=-3) == []
