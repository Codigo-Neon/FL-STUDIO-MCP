from bridge.state_watcher import StateWatcher


class FakeStateApi:
    def __init__(self):
        self.bpm = 90.0
        self.pattern = 0
        self.playing = False
        self.pattern_names = {0: "Pattern 1", 1: "Pattern 2"}

    def get_bpm(self): return self.bpm
    def get_current_pattern(self): return self.pattern
    def is_playing(self): return self.playing
    def get_pattern_name(self, idx): return self.pattern_names.get(idx, f"Pattern {idx + 1}")


class TestStateWatcher:
    def test_first_poll_is_silent_baseline(self):
        w = StateWatcher(FakeStateApi())
        assert w.poll() == []

    def test_bpm_change_emits_event(self):
        api = FakeStateApi()
        w = StateWatcher(api)
        w.poll()                 # baseline
        api.bpm = 140.0
        assert w.poll() == [{"name": "bpm", "data": {"bpm": 140.0}}]

    def test_pattern_change_emits_event_with_name(self):
        api = FakeStateApi()
        w = StateWatcher(api)
        w.poll()
        api.pattern = 1
        assert w.poll() == [{"name": "pattern", "data": {"pattern": 1, "name": "Pattern 2"}}]

    def test_transport_change_emits_event(self):
        api = FakeStateApi()
        w = StateWatcher(api)
        w.poll()
        api.playing = True
        assert w.poll() == [{"name": "transport", "data": {"playing": True}}]

    def test_simultaneous_changes_emit_multiple_events(self):
        api = FakeStateApi()
        w = StateWatcher(api)
        w.poll()
        api.bpm = 100.0
        api.playing = True
        names = [e["name"] for e in w.poll()]
        assert names == ["bpm", "transport"]

    def test_no_change_emits_nothing(self):
        api = FakeStateApi()
        w = StateWatcher(api)
        w.poll()
        assert w.poll() == []

    def test_change_then_stable_emits_once(self):
        api = FakeStateApi()
        w = StateWatcher(api)
        w.poll()
        api.bpm = 120.0
        assert len(w.poll()) == 1
        assert w.poll() == []     # stable after the change

    def test_bpm_jitter_below_precision_does_not_emit(self):
        api = FakeStateApi()
        api.bpm = 140.0
        w = StateWatcher(api)
        w.poll()                  # baseline at 140.0
        api.bpm = 140.001         # sub-0.01 jitter (tempo automation)
        assert w.poll() == []
