import importlib
import pytest

trigger = importlib.import_module("trigger")


class TestGenreState:
    def setup_method(self):
        trigger.current_genre = "neutral"
        trigger.current_mastering_target = dict(
            trigger.mix_analyzer.GENRE_TARGETS["neutral"])

    def test_set_genre_updates_target(self):
        msg = trigger.set_genre("phonk")
        assert trigger.current_genre == "phonk"
        assert trigger.current_mastering_target["lufs"] == -6
        assert "phonk" in msg

    def test_set_genre_unknown_rejected(self):
        msg = trigger.set_genre("dubstep")
        assert "no soportado" in msg
        assert trigger.current_genre == "neutral"

    def test_set_mastering_target_override(self):
        trigger.set_genre("phonk")
        trigger.set_mastering_target(lufs=-5)
        assert trigger.current_mastering_target["lufs"] == -5
        assert trigger.current_mastering_target["true_peak"] == -0.3  # unchanged

    def test_set_mastering_target_out_of_range(self):
        msg = trigger.set_mastering_target(lufs=5)
        assert "rango" in msg

    def test_get_mastering_target_returns_dict(self):
        trigger.set_genre("trap")
        t = trigger.get_mastering_target()
        assert t["lufs"] == -7
