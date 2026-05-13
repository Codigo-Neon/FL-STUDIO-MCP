"""Filename and folder parser.

Converts file paths into structured tags by:
1. Tokenizing the filename (and optionally the folder path)
2. Matching tokens against keyword dictionaries
3. Extracting numeric metadata (BPM, key) with regex
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
)

__all__ = [
    "tokenize",
    "match_keywords",
]


# Split on: _ - . space / \  AND between lowercase→uppercase transitions (camelCase)
_CAMEL_SPLIT = re.compile(r'(?<=[a-z])(?=[A-Z])')
_TOKEN_SPLIT = re.compile(r'[_\-\.\s/\\]+')
_HAS_SEPARATOR = re.compile(r'[_\-\s/\\]')


def tokenize(text: str) -> list[str]:
    """Normalize a filename or folder name into lowercase tokens.

    Strips the file extension if present. Splits on common separators and
    on camelCase boundaries. Removes empty tokens.

    camelCase splitting only applies when the string (minus extension) contains
    no explicit separators — i.e. a pure camelCase identifier like "KickBoomBap".
    When separators are present, each segment is kept as-is (lowercased).
    """
    if text.lower().rsplit(".", 1)[-1] in (
        "wav", "mp3", "flac", "ogg", "aiff", "aif"
    ):
        text = text.rsplit(".", 1)[0]
    # Apply camelCase splitting only when there are no explicit separators
    if not _HAS_SEPARATOR.search(text):
        text = _CAMEL_SPLIT.sub(" ", text)
    # Then split on all separators (including dots between non-extension segments)
    tokens = _TOKEN_SPLIT.split(text)
    return [t.lower() for t in tokens if t]


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
