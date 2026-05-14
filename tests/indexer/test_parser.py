"""Tests for the filename parser."""
from indexer.parser import tokenize, match_keywords, extract_bpm


class TestTokenize:
    def test_splits_on_underscore(self):
        assert tokenize("Kick_Boom_Bap.wav") == ["kick", "boom", "bap"]

    def test_splits_on_dash(self):
        assert tokenize("Kick-BoomBap.wav") == ["kick", "boombap"]

    def test_camelcase_suppressed_when_separator_present(self):
        # "FatBoom" is a camelCase segment, but the dash makes _HAS_SEPARATOR
        # fire and prevents camelCase splitting. If the guard were removed,
        # this would yield ["kick", "fat", "boom"] instead.
        assert tokenize("Kick-FatBoom.wav") == ["kick", "fatboom"]

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

    def test_empty_string(self):
        assert tokenize("") == []


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


class TestExtractBpm:
    def test_explicit_bpm_suffix(self):
        assert extract_bpm("Loop_90bpm.wav") == 90

    def test_explicit_bpm_with_space(self):
        assert extract_bpm("Loop 140 bpm.wav") == 140

    def test_explicit_bpm_uppercase(self):
        assert extract_bpm("Loop_120BPM.wav") == 120

    def test_bpm_in_folder(self):
        assert extract_bpm("/packs/Trap_140bpm/loop.wav") == 140

    def test_no_bpm_returns_none(self):
        assert extract_bpm("Kick_Punchy.wav") is None

    def test_rejects_bpm_out_of_range(self):
        # 999 BPM is nonsense — likely a sample ID, not tempo
        assert extract_bpm("Kick_999bpm.wav") is None

    def test_rejects_bpm_under_40(self):
        assert extract_bpm("Loop_30bpm.wav") is None

    def test_three_digit_bpm_within_range(self):
        assert extract_bpm("Loop_174bpm.wav") == 174  # DnB territory

    def test_ignores_year_like_numbers(self):
        # "2024" in filename is not a BPM
        assert extract_bpm("Sample_2024.wav") is None


from indexer.parser import extract_key


class TestExtractKey:
    def test_canonical_minor(self):
        assert extract_key("Bass_F#min_140.wav") == "F#min"

    def test_canonical_major(self):
        assert extract_key("Lead_Cmaj.wav") == "Cmaj"

    def test_short_minor_form(self):
        assert extract_key("Bass_Fm.wav") == "Fmin"  # 'm' suffix → 'min'

    def test_with_minor_word(self):
        assert extract_key("Lead C minor.wav") == "Cmin"

    def test_with_major_word(self):
        assert extract_key("Lead D# Major.wav") == "D#maj"

    def test_flat_key(self):
        assert extract_key("Bass_Bb_min.wav") == "Bbmin"

    def test_rejects_plain_letter_without_quality(self):
        # "C" alone could be anything — too ambiguous
        assert extract_key("Kick_C_01.wav") is None

    def test_no_key_returns_none(self):
        assert extract_key("Kick_Punchy.wav") is None

    def test_in_key_phrase(self):
        assert extract_key("Bass_in_F#_min.wav") == "F#min"
