"""Tests for the filename parser."""
from indexer.parser import tokenize, match_keywords


class TestTokenize:
    def test_splits_on_underscore(self):
        assert tokenize("Kick_Boom_Bap.wav") == ["kick", "boom", "bap"]

    def test_splits_on_dash(self):
        assert tokenize("Kick-BoomBap.wav") == ["kick", "boombap"]

    def test_splits_on_space(self):
        assert tokenize("Kick Boom Bap.wav") == ["kick", "boom", "bap"]

    def test_splits_on_dot_except_extension(self):
        assert tokenize("Kick.Boom.Bap.wav") == ["kick", "boom", "bap"]

    def test_strips_extension(self):
        assert "wav" not in tokenize("kick.wav")
        assert "mp3" not in tokenize("kick.mp3")

    def test_lowercases(self):
        assert tokenize("KICK_PUNCHY.wav") == ["kick", "punchy"]

    def test_separates_camelcase(self):
        # "KickBoomBap" → ["kick", "boom", "bap"]
        assert tokenize("KickBoomBap.wav") == ["kick", "boom", "bap"]

    def test_keeps_digits_attached(self):
        # "Kick_01" → ["kick", "01"]
        assert tokenize("Kick_01.wav") == ["kick", "01"]

    def test_handles_bpm_suffix(self):
        # "Loop_90bpm.wav" → ["loop", "90bpm"]
        assert tokenize("Loop_90bpm.wav") == ["loop", "90bpm"]

    def test_handles_hash_in_808(self):
        # "808#5.wav" or "808_5.wav"
        tokens = tokenize("808_Sub_5.wav")
        assert "808" in tokens
        assert "sub" in tokens


class TestMatchKeywords:
    def test_single_match(self):
        from indexer.keywords import SAMPLE_TYPE_KEYWORDS
        matches = match_keywords(["kick", "boom", "bap"], SAMPLE_TYPE_KEYWORDS)
        assert matches == ["kick"]

    def test_multi_token_keyword(self):
        from indexer.keywords import GENRE_KEYWORDS
        matches = match_keywords(["epic", "boom_bap", "drums"], GENRE_KEYWORDS)
        assert matches == ["boom_bap"]

    def test_no_match_returns_empty(self):
        from indexer.keywords import SAMPLE_TYPE_KEYWORDS
        assert match_keywords(["zzz", "qqq"], SAMPLE_TYPE_KEYWORDS) == []

    def test_multiple_categories_match(self):
        from indexer.keywords import MOOD_KEYWORDS
        matches = match_keywords(["punchy", "vintage", "kick"], MOOD_KEYWORDS)
        assert sorted(matches) == ["punchy", "vintage"]
