from bridge.note_capture import NoteCapture


class TestNoteCapture:
    def test_feed_noop_when_not_armed(self):
        nc = NoteCapture()
        nc.feed(60, 100, True, 0.0)
        nc.feed(60, 0, False, 1.0)
        assert nc.notes() == []

    def test_simple_on_off_pair_reconstructs_note(self):
        nc = NoteCapture()
        nc.arm()
        nc.feed(60, 100, True, 2.0)   # note-on at beat 2
        nc.feed(60, 0, False, 2.5)    # note-off at beat 2.5
        notes = nc.notes()
        assert notes == [{"note": 60, "velocity": 100, "length": 0.5, "position": 2.0}]

    def test_noteon_with_zero_velocity_closes_note(self):
        nc = NoteCapture()
        nc.arm()
        nc.feed(64, 90, True, 0.0)
        nc.feed(64, 0, True, 1.0)     # vel-0 note-on acts as note-off
        notes = nc.notes()
        assert notes == [{"note": 64, "velocity": 90, "length": 1.0, "position": 0.0}]

    def test_orphan_note_off_is_discarded(self):
        nc = NoteCapture()
        nc.arm()
        nc.feed(72, 0, False, 1.0)    # off with no prior on
        assert nc.notes() == []

    def test_overlapping_same_pitch_fifo(self):
        nc = NoteCapture()
        nc.arm()
        nc.feed(60, 100, True, 0.0)   # first on
        nc.feed(60, 80, True, 0.5)    # second on (overlap)
        nc.feed(60, 0, False, 1.0)    # closes the FIRST (FIFO)
        nc.feed(60, 0, False, 2.0)    # closes the SECOND
        notes = nc.notes()
        assert notes == [
            {"note": 60, "velocity": 100, "length": 1.0, "position": 0.0},
            {"note": 60, "velocity": 80, "length": 1.5, "position": 0.5},
        ]

    def test_negative_length_clamped_to_zero(self):
        nc = NoteCapture()
        nc.arm()
        nc.feed(60, 100, True, 2.0)
        nc.feed(60, 0, False, 1.0)    # off before on (position wrap)
        assert nc.notes()[0]["length"] == 0.0

    def test_still_open_note_included_with_zero_length(self):
        nc = NoteCapture()
        nc.arm()
        nc.feed(67, 110, True, 1.0)   # never closed
        notes = nc.notes()
        assert notes == [{"note": 67, "velocity": 110, "length": 0.0, "position": 1.0}]

    def test_notes_sorted_by_position_then_pitch(self):
        nc = NoteCapture()
        nc.arm()
        nc.feed(64, 100, True, 2.0); nc.feed(64, 0, False, 2.5)
        nc.feed(60, 100, True, 0.0); nc.feed(60, 0, False, 0.5)
        positions = [n["position"] for n in nc.notes()]
        assert positions == [0.0, 2.0]

    def test_arm_clears_previous_capture(self):
        nc = NoteCapture()
        nc.arm()
        nc.feed(60, 100, True, 0.0); nc.feed(60, 0, False, 1.0)
        nc.arm()                      # re-arm wipes state
        assert nc.notes() == []

    def test_disarm_keeps_buffer(self):
        nc = NoteCapture()
        nc.arm()
        nc.feed(60, 100, True, 0.0); nc.feed(60, 0, False, 1.0)
        nc.disarm()
        assert len(nc.notes()) == 1
        assert nc.armed is False
