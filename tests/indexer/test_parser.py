"""Tests for the filename parser."""
from indexer.parser import tokenize, match_keywords, extract_bpm, parse_filename


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


class TestParseFilename:
    def test_kick_boom_bap_punchy(self):
        result = parse_filename("Kick_BoomBap_Punchy_01.wav")
        assert result["sample_type"] == "kick"
        assert "boom_bap" in result["genres"]
        assert "punchy" in result["moods"]
        assert result["bpm"] is None
        assert result["key"] is None
        assert result["is_loop"] is False

    def test_hat_closed_trap_140bpm(self):
        result = parse_filename("Hat_Closed_Trap_140bpm.wav")
        assert result["sample_type"] == "hat_closed"
        assert "trap" in result["genres"]
        assert result["bpm"] == 140

    def test_808_subby(self):
        result = parse_filename("Bass_808_Subby_F#min.wav")
        assert result["sample_type"] == "bass"
        assert result["subtype"] == "808"
        assert result["key"] == "F#min"

    def test_loop_marker(self):
        result = parse_filename("DrumLoop_90bpm.wav")
        assert result["is_loop"] is True
        assert result["is_oneshot"] is False

    def test_oneshot_marker(self):
        result = parse_filename("Kick_OneShot_01.wav")
        assert result["is_oneshot"] is True
        assert result["is_loop"] is False

    def test_neither_loop_nor_oneshot_defaults_false(self):
        result = parse_filename("Kick_01.wav")
        assert result["is_loop"] is False
        assert result["is_oneshot"] is False

    def test_unknown_filename(self):
        result = parse_filename("xyz_qqq_123.wav")
        assert result["sample_type"] is None
        assert result["genres"] == []
        assert result["moods"] == []

    def test_raw_tags_lists_all_matches(self):
        result = parse_filename("Kick_Punchy_Vintage_BoomBap_90bpm.wav")
        assert "kick" in result["raw_tags"]
        assert "punchy" in result["raw_tags"]
        assert "vintage" in result["raw_tags"]
        assert "boom_bap" in result["raw_tags"]

    def test_hat_closed_priority_over_hat(self):
        # "Hat_Closed" should resolve to hat_closed, not generic hat
        result = parse_filename("Hat_Closed_01.wav")
        assert result["sample_type"] == "hat_closed"

    def test_first_sample_type_wins(self):
        # If filename mentions both "kick" and "snare", take the first
        result = parse_filename("Kick_NotASnare.wav")
        assert result["sample_type"] == "kick"
