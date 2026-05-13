"""Tests for keyword dictionaries."""
from indexer.keywords import (
    SAMPLE_TYPE_KEYWORDS,
    GENRE_KEYWORDS,
    MOOD_KEYWORDS,
    SUBTYPE_KEYWORDS,
    LOOP_KEYWORDS,
    ONESHOT_KEYWORDS,
    AUDIO_EXTENSIONS,
    SKIP_EXTENSIONS,
)


class TestSampleTypeKeywords:
    def test_kick_keywords_include_obvious_terms(self):
        assert "kick" in SAMPLE_TYPE_KEYWORDS["kick"]
        assert "bd" in SAMPLE_TYPE_KEYWORDS["kick"]

    def test_hat_variants_separate(self):
        assert "hat_closed" in SAMPLE_TYPE_KEYWORDS
        assert "hat_open" in SAMPLE_TYPE_KEYWORDS
        assert "hat" in SAMPLE_TYPE_KEYWORDS
        # Closed/open should not pollute the generic 'hat' bucket
        assert "closedhat" not in SAMPLE_TYPE_KEYWORDS["hat"]
        assert "openhat" not in SAMPLE_TYPE_KEYWORDS["hat"]

    def test_bass_includes_808(self):
        assert "808" in SAMPLE_TYPE_KEYWORDS["bass"]

    def test_all_keywords_lowercase(self):
        for category, keywords in SAMPLE_TYPE_KEYWORDS.items():
            for kw in keywords:
                assert kw == kw.lower(), f"Keyword '{kw}' in {category} not lowercase"


class TestGenreKeywords:
    def test_includes_main_genres(self):
        assert "trap" in GENRE_KEYWORDS
        assert "boom_bap" in GENRE_KEYWORDS
        assert "phonk" in GENRE_KEYWORDS

    def test_boom_bap_variations(self):
        # "Boom Bap" with space, with underscore, with dash
        assert "boombap" in GENRE_KEYWORDS["boom_bap"]
        assert "boom bap" in GENRE_KEYWORDS["boom_bap"]


class TestMoodKeywords:
    def test_punchy_aliases(self):
        assert "punchy" in MOOD_KEYWORDS["punchy"]
        assert "snappy" in MOOD_KEYWORDS["punchy"]


class TestExtensions:
    def test_audio_extensions_lowercase_with_dot(self):
        for ext in AUDIO_EXTENSIONS:
            assert ext.startswith(".")
            assert ext == ext.lower()

    def test_skip_extensions_include_presets(self):
        assert ".fst" in SKIP_EXTENSIONS  # FL preset
        assert ".fxp" in SKIP_EXTENSIONS  # VST preset
        assert ".nki" in SKIP_EXTENSIONS  # Kontakt
