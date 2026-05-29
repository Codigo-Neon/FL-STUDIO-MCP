import pytest
from knowledge import mix_analyzer


class TestGenreTarget:
    def test_known_genre_returns_its_target(self):
        t = mix_analyzer.get_genre_target("phonk")
        assert t["lufs"] == -6
        assert t["true_peak"] == -0.3

    def test_unknown_genre_returns_neutral(self):
        assert mix_analyzer.get_genre_target("dubstep") == mix_analyzer.GENRE_TARGETS["neutral"]

    def test_returns_a_copy_not_the_shared_dict(self):
        t = mix_analyzer.get_genre_target("trap")
        t["lufs"] = 0
        assert mix_analyzer.GENRE_TARGETS["trap"]["lufs"] == -7
