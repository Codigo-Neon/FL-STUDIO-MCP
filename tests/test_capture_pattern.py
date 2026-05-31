from trigger import _format_captured_notes


class TestFormatCapturedNotes:
    def test_empty_explains_feasibility_fallback(self):
        out = _format_captured_notes({"notes": [], "count": 0, "channel_name": "Bass"})
        assert "0 notas" in out
        assert "OnMidiOutMsg" in out

    def test_lists_notes_with_name_bar_beat_and_duration(self):
        result = {
            "channel_name": "Bass",
            "count": 2,
            "notes": [
                {"note": 36, "velocity": 100, "length": 1.0, "position": 0.0},
                {"note": 43, "velocity": 90, "length": 0.5, "position": 4.0},
            ],
        }
        out = _format_captured_notes(result)
        assert "Bass" in out
        assert "2 notas" in out
        assert "C2" in out      # midi 36 -> C2
        assert "G2" in out      # midi 43 -> G2
        assert "bar 1" in out
        assert "bar 2" in out   # position 4.0 -> bar 2
