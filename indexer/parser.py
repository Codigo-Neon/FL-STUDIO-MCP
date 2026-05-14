"""Filename and folder parser.

Converts file paths into structured tags by:
1. Tokenizing the filename (and optionally the folder path)
2. Matching tokens against keyword dictionaries
3. Extracting numeric metadata (BPM, key) with regex

camelCase splitting is applied only when the stem contains no explicit
separator characters (_, -, space, /, \\). This avoids mangling filenames
like "Kick-BoomBap" which would otherwise yield spurious extra tokens.
"""
import re
from pathlib import Path

from indexer.keywords import (
    SAMPLE_TYPE_KEYWORDS,
    SUBTYPE_KEYWORDS,
    GENRE_KEYWORDS,
    MOOD_KEYWORDS,
    LOOP_KEYWORDS,
    ONESHOT_KEYWORDS,
    AUDIO_EXTENSIONS,
)

# Stems (no leading dot) of recognized audio extensions, derived once.
_AUDIO_EXT_STEMS = frozenset(ext.lstrip(".") for ext in AUDIO_EXTENSIONS)

__all__ = [
    "tokenize",
    "match_keywords",
    "extract_bpm",
    "extract_key",
]


# Split on: _ - . space / \  AND between lowercase→uppercase transitions (camelCase)
_CAMEL_SPLIT = re.compile(r'(?<=[a-z])(?=[A-Z])')   # lowercase→uppercase boundary
_TOKEN_SPLIT = re.compile(r'[_\-\.\s/\\]+')          # any separator run
_HAS_SEPARATOR = re.compile(r'[_\-\s/\\]')           # presence check (dots excluded: may be extension)

_BPM_REGEX = re.compile(r'(?<!\d)(\d{2,3})\s*bpm(?!\w)', re.IGNORECASE)

# Matches: <key><quality>  where:
#   key     = [A-G] optionally followed by # or b
#   quality = min, minor, m, maj, major (case-insensitive)
# Surrounded by explicit musical separators (start-of-string, space, _, -, .)
# rather than \b — because regex \b doesn't fire between letters and
# underscores (both are word chars), so 'F#min_140' would fail with \b.
_KEY_REGEX = re.compile(
    r'(?:^|[\s_\-\.])([A-G])(#|b)?[\s_\-]*(min|minor|m|maj|major)(?=[\s_\-\.]|$)',
    re.IGNORECASE
)


def tokenize(text: str) -> list[str]:
    """Normalize a filename or folder name into lowercase tokens.

    Strips the file extension if present. Splits on common separators and
    on camelCase boundaries. Removes empty tokens.

    camelCase splitting only applies when the string (minus extension) contains
    no explicit separators — i.e. a pure camelCase identifier like "KickBoomBap".
    When separators are present, each segment is kept as-is (lowercased).
    """
    if text.lower().rsplit(".", 1)[-1] in _AUDIO_EXT_STEMS:
        text = text.rsplit(".", 1)[0]
    # Apply camelCase splitting only when there are no explicit separators
    if not _HAS_SEPARATOR.search(text):
        text = _CAMEL_SPLIT.sub(" ", text)
    # Then split on all separators (including dots between non-extension segments)
    tokens = _TOKEN_SPLIT.split(text)
    return [t.lower() for t in tokens if t]


def extract_bpm(text: str, min_bpm: int = 40, max_bpm: int = 220) -> int | None:
    """Extract BPM from a filename or path.

    Looks for explicit "<number>bpm" or "<number> bpm" markers. Returns None
    if no marker found or the number is out of plausible musical range.
    """
    m = _BPM_REGEX.search(text)
    if not m:
        return None
    bpm = int(m.group(1))
    if bpm < min_bpm or bpm > max_bpm:
        return None
    return bpm


def extract_key(text: str) -> str | None:
    """Extract musical key from a filename, e.g. 'F#min', 'Cmaj'.

    Conservative: requires both letter AND a quality suffix (min/maj/m).
    Returns canonical form: '<letter><#|b|>{min|maj}'.
    """
    m = _KEY_REGEX.search(text)
    if not m:
        return None
    letter = m.group(1).upper()
    accidental = m.group(2) or ""
    quality_raw = m.group(3).lower()
    if quality_raw in ("min", "minor", "m"):
        quality = "min"
    else:
        quality = "maj"
    return f"{letter}{accidental}{quality}"


def match_keywords(tokens: list[str], dictionary: dict[str, list[str]]) -> list[str]:
    """Return the list of categories from `dictionary` whose keywords match
    any of the input tokens. Categories preserve insertion order.

    For multi-word keywords (e.g. "boom bap"), the entire keyword must appear
    contiguously in the tokens, or in a single joined token (e.g. "boom_bap"
    gets joined to "boom_bap" via tokenize; comparison handles both).
    """
    matches = []
    joined = " ".join(tokens)
    for category, keywords in dictionary.items():
        for kw in keywords:
            kw_norm = kw.lower()
            if " " in kw_norm:
                if kw_norm in joined or kw_norm.replace(" ", "_") in tokens:
                    matches.append(category)
                    break
            else:
                if kw_norm in tokens:
                    matches.append(category)
                    break
    return matches
